"""Render an independent installation to catch hardcoded environment values."""
import base64
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class ManifestLoader(getattr(yaml, 'CSafeLoader', yaml.SafeLoader)):
    pass


ManifestLoader.add_constructor('tag:yaml.org,2002:value', ManifestLoader.construct_scalar)


def strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)
    elif isinstance(value, str):
        yield value


class EnvironmentConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='environment-config-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        # Copy source files only: never age keys, state, decrypted files or project checkouts.
        files = subprocess.check_output(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', 'live', 'kubernetes'],
            cwd=ROOT, text=True).splitlines()
        for name in files:
            source = ROOT / name
            if source.is_file():
                destination = cls.root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        for example in cls.root.glob('live/*/secrets/**/*.example'):
            shutil.copyfile(example, example.with_suffix(''))
        for env in ('local', 'prod'):
            path = cls.root / 'live' / env / 'config/values.yaml'
            config = yaml.safe_load(path.read_text())
            config['domain'] = 'example.test'
            config['github'].update(organization='example-team', infrastructureRepository='cluster',
                                    discoveryTopic='example-deploy')
            config['identity'].update(adminUsername='example-admin', adminEmail='admin@example.test',
                                      allowedSubjects=['example-subject'])
            config['backups'].update(bucket='example-backups', region='ams3')
            if env == 'local':
                config['cluster']['httpsPort'] = 9443
            else:
                config['registry']['namespace'] = 'example-user'
            path.write_text(yaml.safe_dump(config, sort_keys=False))

    def render(self, env, component=''):
        result = subprocess.run(
            ['kubectl', 'kustomize', '--enable-helm', str(self.root / 'live' / env / 'kubernetes' / component)],
            text=True, capture_output=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('configured-by-environment', result.stdout)
        return [doc for doc in yaml.load_all(result.stdout, Loader=ManifestLoader) if doc]

    def test_docs_digest_update_preserves_configuration_transformers(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/deploy-docs.yaml').read_text())
        step = next(step for step in workflow['jobs']['publish']['steps']
                    if step.get('name') == 'Update the image deployed by Argo CD')
        script = step['run'].split("<<'PYTHON'\n", 1)[1].split('\nPYTHON', 1)[0]
        import os
        result = subprocess.run(['python3', '-c', script], cwd=self.root, text=True,
                                capture_output=True, env={**os.environ, 'DIGEST': 'sha256:' + '1' * 64})
        self.assertEqual(result.returncode, 0, result.stderr)
        config = yaml.safe_load((self.root / 'live/prod/kubernetes/docs/site/kustomization.yaml').read_text())
        self.assertEqual(config['transformers'], ['../../../transformers'])
        self.assertEqual(config['images'][0]['digest'], 'sha256:' + '1' * 64)

    def test_onboarding_passes_the_configured_repository_to_delivery(self):
        result = subprocess.run(
            ['helm', 'template', 'sample', str(self.root / 'kubernetes/charts/project-onboarding'),
             '--set', 'repository=sample', '--set', 'repoURL=https://github.com/example-team/sample.git',
             '--set', 'revision=main', '--set', 'infrastructureRepoURL=git@github.com:example-team/cluster.git'],
            text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        docs = list(yaml.safe_load_all(result.stdout))
        delivery = next(doc for doc in docs if doc['kind'] == 'Application')
        self.assertEqual(delivery['spec']['sources'][0]['repoURL'], 'git@github.com:example-team/cluster.git')
        self.assertNotIn('blackstorm-dev', result.stdout)


    def test_standard_https_port_does_not_create_a_duplicate_service_port(self):
        path = self.root / 'live/local/config/values.yaml'
        original = path.read_text()
        config = yaml.safe_load(original)
        config['cluster']['httpsPort'] = 443
        try:
            path.write_text(yaml.safe_dump(config, sort_keys=False))
            docs = self.render('local', 'network/gateways')
            proxy = next(doc for doc in docs if doc['kind'] == 'EnvoyProxy')
            ports = proxy['spec']['provider']['kubernetes']['envoyService']['patch']['value']['spec']['ports']
            self.assertEqual([port['port'] for port in ports], [80, 443])
        finally:
            path.write_text(original)


    def test_new_installation_reaches_routes_identity_discovery_and_backups(self):
        components = ['', 'argocd/projects', 'argocd/argocd', 'identity/dex', 'kargo/kargo',
                      'o11y/gatus', 'o11y/kube-prometheus-stack', 'velero/velero-ui',
                      'stackgres/stackgres', 'network/gateways', 'arc-runners/blackstorm', 'velero/velero']
        # Only Kind needs in-cluster resolution of the public local domain.
        for env in ('local', 'prod'):
            selected = components + (['kube-system/coredns'] if env == 'local' else [])
            for component in selected:
                with self.subTest(env=env, component=component):
                    docs = self.render(env, component)
                    for doc in docs:
                        if doc['kind'] in ('CustomResourceDefinition', 'SopsSecret'):
                            continue
                        values = list(strings(doc))
                        if doc['kind'] == 'Secret' and doc['metadata']['name'].startswith('dex-config-') \
                                and 'config.yaml' in doc.get('data', {}):
                            values.append(base64.b64decode(doc['data']['config.yaml']).decode())
                        for value in values:
                            for previous in ('blackstorm.dev', 'blackstorm-dev', 'TomasCaruso10',
                                             'tomascaruso1098@gmail.com', 'blackstorm-backups'):
                                self.assertNotIn(previous, value, f"{doc['kind']}/{doc['metadata']['name']}")
                        if doc['kind'] == 'HTTPRoute':
                            self.assertTrue(all(host.endswith('.example.test') for host in doc['spec']['hostnames']))
                        if doc['kind'] == 'EnvoyProxy' and doc['metadata']['name'] == 'envoy-external' and env == 'local':
                            ports = doc['spec']['provider']['kubernetes']['envoyService']['patch']['value']['spec']['ports']
                            self.assertEqual(next(port['port'] for port in ports if port.get('name') == 'https-local'), 9443)
                        if doc['kind'] == 'ConfigMap' and doc['metadata']['name'] == 'coredns':
                            self.assertIn(r'\.example\.test\.', doc['data']['Corefile'])
                        if doc['kind'] == 'BackupStorageLocation':
                            self.assertEqual(doc['spec']['objectStorage']['bucket'], 'example-backups')
                            self.assertEqual(doc['spec']['config']['s3Url'], 'https://ams3.digitaloceanspaces.com')
                        if doc['kind'] == 'ApplicationSet' and doc['metadata']['name'] in ('platform', 'projects'):
                            self.assertEqual(doc['spec']['template']['spec']['source']['repoURL'],
                                             'git@github.com:example-team/cluster.git')
            if env == 'prod':
                for component in ('argo-rollouts/argo-rollouts', 'docs/site'):
                    with self.subTest(env=env, component=component):
                        docs = self.render(env, component)
                        self.assertNotIn('blackstorm.dev', '\n'.join(strings(docs)))
                        if component == 'docs/site':
                            deployment = next(doc for doc in docs if doc['kind'] == 'Deployment')
                            image = deployment['spec']['template']['spec']['containers'][0]['image']
                            self.assertTrue(image.startswith('docker.io/example-user/blackstorm-infra-docs@sha256:'))


if __name__ == '__main__':
    unittest.main()
