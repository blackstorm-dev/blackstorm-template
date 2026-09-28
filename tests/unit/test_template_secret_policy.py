"""Official repository restrictions must not leak into users' repositories."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/check-template-secrets.py'


class TemplateSecretPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ('GITHUB_ACTIONS', 'GITHUB_REPOSITORY', 'GIT_DIR', 'GIT_WORK_TREE')}
        self.git('init', '-q')
        self.git('remote', 'add', 'origin', 'https://github.com/blackstorm-dev/blackstorm-template.git')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, env=self.env, stderr=subprocess.DEVNULL)

    def stage(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        self.git('add', name)

    def run_check(self, all_files=False):
        result = subprocess.run([sys.executable, str(SCRIPT), *(['--all'] if all_files else [])],
                                cwd=self.root, env=self.env, text=True, capture_output=True)
        return result.returncode, result.stdout

    def example(self):
        return (ROOT / 'live/prod/secrets/dockerhub.env.example').read_text()

    def test_official_rejects_real_secrets_for_ssh_and_https_origins(self):
        self.stage('secrets/actual.env', 'TOKEN=test-value\n')
        for url in ['https://github.com/blackstorm-dev/blackstorm-template.git',
                    'git@github.com:blackstorm-dev/blackstorm-project-template.git',
                    'ssh://git@github.com/blackstorm-dev/blackstorm-project-template.git']:
            with self.subTest(url=url):
                self.git('remote', 'set-url', 'origin', url)
                self.assertEqual(self.run_check()[0], 1)

    def test_official_rejects_even_encrypted_file(self):
        self.stage('live/local/secrets/token.yaml', 'sops:\n  mac: encrypted-test-fixture\n')
        self.assertEqual(self.run_check()[0], 1)

    def test_user_repository_is_not_subject_to_examples_only(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/example-user/my-app.git')
        self.stage('secrets/token.env', 'TOKEN=test-value\n')
        # The existing SOPS hook performs encryption/decryption validation separately.
        self.assertEqual(self.run_check()[0], 0)

    def test_actions_identity_takes_precedence_over_remote(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/example-user/my-app.git')
        self.stage('secrets/token.env', 'TOKEN=test-value\n')
        self.env.update(GITHUB_ACTIONS='true', GITHUB_REPOSITORY='blackstorm-dev/blackstorm-template')
        self.assertEqual(self.run_check(True)[0], 1)
        self.env['GITHUB_REPOSITORY'] = 'example-user/my-app'
        self.assertEqual(self.run_check(True)[0], 0)

    def test_missing_header_or_nonplaceholder_example_is_rejected(self):
        path = 'live/prod/secrets/dockerhub.env.example'
        for text in [self.example().split('\n', 1)[1],
                     self.example().replace('DOCKERHUB_TOKEN=REPLACE_ME', 'DOCKERHUB_TOKEN=test-value')]:
            self.stage(path, text)
            code, output = self.run_check()
            self.assertEqual(code, 1)
            self.assertNotIn('test-value', output)
        self.stage(path, self.example())
        self.assertEqual(self.run_check()[0], 0)

    def test_checks_index_not_unstaged_repairs(self):
        path = 'live/prod/secrets/dockerhub.env.example'
        self.stage(path, self.example().replace('DOCKERHUB_TOKEN=REPLACE_ME', 'DOCKERHUB_TOKEN=test-value'))
        (self.root / path).write_text(self.example())
        self.assertEqual(self.run_check()[0], 1)

    def test_yaml_and_embedded_docker_credentials(self):
        path = 'live/prod/secrets/docs/dockerhub.yaml.example'
        example = (ROOT / path).read_text()
        self.stage(path, example)
        self.assertEqual(self.run_check()[0], 0)
        self.stage(path, example.replace('"password": "REPLACE_ME"', '"password": "test-value"'))
        self.assertEqual(self.run_check()[0], 1)

    def test_kustomization_cannot_hide_secret_generator(self):
        path = 'live/local/secrets/kustomization.yaml'
        safe = 'apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nnamespace: project-template\nresources: []\n'
        self.stage(path, safe)
        self.assertEqual(self.run_check()[0], 0)
        self.stage(path, safe + 'secretGenerator:\n- name: hidden\n  literals: [password=test-value]\n')
        self.assertEqual(self.run_check()[0], 1)

    def test_all_mode_checks_previously_committed_files(self):
        self.stage('secrets/token.env', 'TOKEN=test-value\n')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'fixture')
        self.assertEqual(self.run_check()[0], 0)
        self.assertEqual(self.run_check(True)[0], 1)


if __name__ == '__main__':
    unittest.main()
