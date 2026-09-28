# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Preflight and readiness reporting for the platform declared in live/<env>."""
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    try:
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Se agotó el tiempo de: {' '.join(args)}") from None
    if result.returncode:
        # Do not echo provider output: it may contain decrypted credentials.
        detail = '' if args[0] == 'sops' else '\n' + result.stderr.strip()[-1500:]
        raise RuntimeError(f"Falló: {' '.join(args)}{detail}")
    return result.stdout


def configuration(env):
    return yaml.safe_load((ROOT / 'live' / env / 'config/values.yaml').read_text())


def repository_url(env):
    github = configuration(env)['github']
    return f"git@github.com:{github['organization']}/{github['infrastructureRepository']}.git"


def platform_application_set(env):
    manifests = run('kubectl', 'kustomize', '--enable-helm', str(ROOT / 'live' / env / 'kubernetes'))
    return next(resource for resource in yaml.safe_load_all(manifests)
                if resource and resource.get('kind') == 'ApplicationSet'
                and resource['metadata']['name'] == 'platform')


def expected_apps(env):
    return {f"{p.parent.parent.name}-{p.parent.name}" for p in
            (ROOT / 'live' / env / 'kubernetes').glob('*/*/kustomization.yaml')}


def preflight(env):
    for tool in ['kubectl', 'helm', 'helmfile', 'terragrunt', 'terraform', 'sops', 'gh', 'git']:
        if not shutil.which(tool):
            raise RuntimeError(f"Falta {tool}. Ejecutá make init dentro de mise.")
    folder = ROOT / 'live' / env
    if 'REPLACE_ME' in (folder / 'config/values.yaml').read_text():
        raise RuntimeError(f'Completá los placeholders de live/{env}/config/values.yaml antes de crear recursos.')
    if not (folder / 'terraform/cluster/terragrunt.hcl').is_file():
        raise RuntimeError(f"Falta live/{env}/terraform/cluster/terragrunt.hcl")
    if not expected_apps(env):
        raise RuntimeError(f"No hay aplicaciones declaradas en live/{env}/kubernetes")
    run('gh', 'auth', 'status')
    if (folder / 'terraform/cloudflare').is_dir():
        for name in ['cloudflare.env', 'digitalocean.env']:
            if not (folder / 'secrets' / name).is_file():
                raise RuntimeError(f'Falta live/{env}/secrets/{name}; configurá las credenciales antes de crear recursos.')
    provider_values = dict(os.environ)
    for secret in sorted((folder / 'secrets').rglob('*')):
        if secret.is_file() and secret.name != 'kustomization.yaml' and secret.suffix in ('.env', '.yaml', '.yml', '.json'):
            cleartext = run('sops', '--decrypt', str(secret.relative_to(ROOT)))
            if 'REPLACE_ME' in cleartext:
                raise RuntimeError(f'Completá los placeholders: make secrets FILE={secret.relative_to(ROOT)}')
            if secret.suffix == '.env':
                for key, value in re.findall(r'^(?:export\s+)?([A-Z_][A-Z_0-9]*)=(.*)$', cleartext, re.MULTILINE):
                    provider_values[key] = value.strip().strip("\"'")
            del cleartext
    if (folder / 'kubernetes/arc-runners').is_dir() and not (folder / 'secrets/github-arc.yaml').is_file():
        raise RuntimeError(f"Falta live/{env}/secrets/github-arc.yaml para inicializar los runners")
    if (folder / 'terraform/cloudflare').is_dir():
        required = ['DIGITALOCEAN_TOKEN', 'CLOUDFLARE_API_TOKEN', 'SPACES_ACCESS_KEY_ID',
                    'SPACES_SECRET_ACCESS_KEY', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing = [key for key in required if not provider_values.get(key)]
        if missing:
            raise RuntimeError('Faltan credenciales del entorno: ' + ', '.join(missing))
    del provider_values
    # Argo reads Git, not the worktree used to invoke Make.
    appset = platform_application_set(env)
    source = appset['spec']['template']['spec']['source']
    repo, revision = source['repoURL'], source['targetRevision']
    # Use gh's credential helper rather than requiring the creator to configure SSH.
    fetch_url = repo.replace('git@github.com:', 'https://github.com/')
    run('git', '-c', 'credential.https://github.com.helper=!gh auth git-credential',
        'fetch', '--quiet', fetch_url, revision)
    paths = [f'live/{env}/kubernetes', f'live/{env}/secrets', f'live/{env}/config',
             f'live/{env}/transformers', f'live/{env}/generators', 'kubernetes']
    changed = run('git', 'diff', '--name-only', 'FETCH_HEAD', '--', *paths).strip()
    untracked = run('git', 'ls-files', '--others', '--exclude-standard', '--', *paths).strip()
    if changed or untracked:
        raise RuntimeError(f"Argo lee {repo} ({revision}), pero hay configuración sin publicar:\n"
                           f"{changed}\n{untracked}\nRevisá el diff y publicá esos cambios antes de crear el clúster.")
    print('✓ Credenciales descifrables y configuración publicada en el Git que leerá Argo.', flush=True)
    # Rendering catches missing files, chart downloads and invalid Kustomize patches before spending money.
    overlays = [folder / 'kubernetes', *sorted((folder / 'kubernetes').glob('*/*/kustomization.yaml'))]
    for overlay in overlays:
        directory = overlay.parent if overlay.is_file() else overlay
        print(f"  Validando {directory.relative_to(ROOT)}", flush=True)
        run('kubectl', 'kustomize', '--enable-helm', str(directory))
    print(f'✓ Configuración válida: {len(expected_apps(env))} aplicaciones de plataforma.', flush=True)


def application_ready(app, revision=None):
    status = app.get('status', {})
    return ((revision is None or status.get('sync', {}).get('revision') == revision)
            and status.get('sync', {}).get('status') == 'Synced'
            and status.get('health', {}).get('status') == 'Healthy'
            and status.get('operationState', {}).get('phase') not in ('Running', 'Failed', 'Error', 'Terminating')
            and not any(c.get('type', '').endswith('Error') for c in status.get('conditions', [])))


def pending_reason(app):
    if not app:
        return 'ApplicationSet todavía no creó la aplicación'
    status = app.get('status', {})
    conditions = status.get('conditions', [])
    errors = [c.get('message', '') for c in conditions if c.get('type', '').endswith('Error')]
    return '; '.join(errors) or status.get('operationState', {}).get('message') or (
        f"{status.get('sync', {}).get('status', 'Unknown')} / "
        f"{status.get('health', {}).get('status', 'Unknown')}")


def route_urls(routes, apps, port, require_attached=True):
    result = {}
    for route in routes:
        metadata = route['metadata']
        tracking = metadata.get('annotations', {}).get('argocd.argoproj.io/tracking-id', '')
        if tracking.split(':')[0] not in apps:
            continue
        # A host alone does not mean the Gateway has attached the route.
        attached = any(all(any(c.get('type') == kind and c.get('status') == 'True'
                               and c.get('observedGeneration') == metadata.get('generation')
                               for c in parent.get('conditions', []))
                           for kind in ['Accepted', 'ResolvedRefs'])
                       for parent in route.get('status', {}).get('parents', []))
        if require_attached and not attached:
            continue
        for host in route.get('spec', {}).get('hostnames', []):
            if '*' not in host:
                result[f"{metadata['namespace']}/{metadata['name']}"] = f'https://{host}{port}/'
    return result


def reachable(url):
    # Localhost uses the template's self-signed development certificate.
    host = urllib.parse.urlparse(url).hostname or ''
    context = ssl._create_unverified_context() if host.endswith('.localhost') else ssl.create_default_context()
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
    try:
        with opener.open(url, timeout=3) as response:
            return response.status < 400
    except urllib.error.HTTPError as error:
        return error.code in (301, 302, 303, 307, 308, 401)
    except (OSError, urllib.error.URLError):
        return False


def remote_revision(appset):
    source = appset['spec']['template']['spec']['source']
    revision = source['targetRevision']
    if re.fullmatch(r'[a-f0-9]{40}', revision):
        return revision
    repo = source['repoURL'].replace('git@github.com:', 'https://github.com/')
    refs = run('git', '-c', 'credential.https://github.com.helper=!gh auth git-credential',
               'ls-remote', '--exit-code', repo, revision, revision + '^{}').splitlines()
    if not refs:
        raise RuntimeError(f'No se encontró la revisión {revision} en {repo}')
    return refs[-1].split()[0]


def wait_for_platform(env, timeout, interval):
    names = expected_apps(env)
    if not names:
        raise RuntimeError(f'No hay aplicaciones de plataforma en live/{env}/kubernetes')
    appset = platform_application_set(env)
    revision = remote_revision(appset)
    port = appset.get('metadata', {}).get('annotations', {}).get('blackstorm.dev/public-https-port', '443')
    suffix = '' if port == '443' else ':' + port
    kubectl = ['kubectl', '--context', env, '--request-timeout=10s']
    deadline = time.monotonic() + timeout
    previous = None
    argo_shown = False
    apps, urls, unavailable = {}, {}, []
    api_error = None
    while True:
        try:
            items = json.loads(run(*kubectl, '-n', 'argocd', 'get', 'applications', '-o', 'json'))['items']
            apps = {a['metadata']['name']: a for a in items if a['metadata']['name'] in names}
            routes = json.loads(run(*kubectl, 'get', 'httproutes', '-A', '-o', 'json'))['items']
            api_error = None
            urls = route_urls(routes, names, suffix)
            declared_urls = route_urls(routes, names, suffix, require_attached=False)
            argo = urls.get('argocd/argocd')
            if argo and not argo_shown and reachable(argo):
                print(f'\n✓ Argo CD disponible. Seguí el despliegue acá:\n{argo}\n', flush=True)
                argo_shown = True
            ready = sum(application_ready(a, revision) for a in apps.values())
            pending = sorted(names - {name for name, a in apps.items() if application_ready(a, revision)})
            state = (ready, tuple((name, f'Esperando revisión {revision[:8]}'
                                   if name in apps and application_ready(apps[name])
                                   else pending_reason(apps.get(name))) for name in pending))
            if state != previous:
                print(f'⏳ Plataforma: {ready}/{len(names)} aplicaciones listas.', flush=True)
                for name, reason in state[1]:
                    print(f'  {name}: {reason}', flush=True)
                previous = state
            if not pending:
                unavailable = [url for name, url in declared_urls.items()
                               if name not in urls or not reachable(urls[name])]
                if argo_shown and not unavailable:
                    print('\n✓ Plataforma lista. Accesos:', flush=True)
                    for name, url in sorted(urls.items()):
                        print(f'  {name}: {url}', flush=True)
                    # Do not promise SSO for environments that have not enabled Dex.
                    if 'identity-dex' in names:
                        print('  Paneles integrados con Dex: ingreso con GitHub.', flush=True)
                    return
                print('⏳ Esperando acceso público a los paneles (DNS, túnel o rutas).', flush=True)
        except (RuntimeError, json.JSONDecodeError) as error:
            api_error = str(error)
            print(f'⏳ Esperando Kubernetes/Argo: {error}', flush=True)
        if time.monotonic() >= deadline:
            print('\nNo se pudo confirmar que toda la plataforma esté lista.', file=sys.stderr)
            for name in sorted(names):
                if name not in apps or not application_ready(apps[name], revision):
                    print(f'  {name}: {pending_reason(apps.get(name))}', file=sys.stderr)
            if api_error:
                print(f'  {api_error}', file=sys.stderr)
            if not argo_shown:
                print('  Argo CD todavía no tiene una URL pública accesible.', file=sys.stderr)
            for url in unavailable:
                print(f'  Sin acceso: {url}', file=sys.stderr)
            raise RuntimeError(f'Retomá con: make cluster-wait ENV={env}\n'
                               f'Diagnóstico: kubectl --context {env} -n argocd get applications')
        time.sleep(min(interval, max(0, deadline - time.monotonic())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'wait', 'repo-url'])
    parser.add_argument('--env', required=True)
    parser.add_argument('--timeout', type=int, default=1800)
    parser.add_argument('--interval', type=int, default=10)
    args = parser.parse_args()
    if args.timeout < 0 or args.interval <= 0:
        parser.error('timeout debe ser >= 0 e interval > 0')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.env) or not (ROOT / 'live' / args.env).is_dir():
        parser.error('ENV debe ser el nombre de un entorno existente en live/')
    os.chdir(ROOT)
    try:
        if args.action == 'repo-url':
            print(repository_url(args.env))
        elif args.action == 'check':
            preflight(args.env)
        else:
            wait_for_platform(args.env, args.timeout, args.interval)
    except (RuntimeError, OSError, KeyError, yaml.YAMLError) as error:
        print(f'\nERROR: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f'\nEspera interrumpida. Retomá con: make cluster-wait ENV={args.env}', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    sys.exit(main())
