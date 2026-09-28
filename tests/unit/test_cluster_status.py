"""The creation command must never report success for an incomplete platform."""
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('cluster_status', Path(__file__).parents[2] / 'scripts/cluster-status.py')
cluster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cluster)

READY = {'metadata': {'name': 'argocd-argocd'}, 'status': {
    'sync': {'status': 'Synced', 'revision': 'current'}, 'health': {'status': 'Healthy'},
    'operationState': {'phase': 'Succeeded'}}}
ROUTE = {'metadata': {'name': 'argocd', 'namespace': 'argocd', 'generation': 2,
                      'annotations': {'argocd.argoproj.io/tracking-id': 'argocd-argocd:route'}},
         'spec': {'hostnames': ['argocd.localhost']},
         'status': {'parents': [{'conditions': [
             {'type': kind, 'status': 'True', 'observedGeneration': 2}
             for kind in ['Accepted', 'ResolvedRefs']]}]}}


class ReadinessTests(unittest.TestCase):
    def test_failed_or_running_sync_is_not_ready_even_when_health_is_green(self):
        for phase in ['Running', 'Failed', 'Error']:
            app = copy.deepcopy(READY)
            app['status']['operationState']['phase'] = phase
            self.assertFalse(cluster.application_ready(app))

    def test_old_git_revision_does_not_finish_a_new_deployment(self):
        self.assertFalse(cluster.application_ready(READY, revision="new-commit"))

    def test_manifest_error_is_not_hidden_by_stale_healthy_status(self):
        app = copy.deepcopy(READY)
        app['status']['conditions'] = [{'type': 'ComparisonError', 'message': 'missing manifest'}]
        self.assertFalse(cluster.application_ready(app))

    def test_routes_require_current_gateway_acceptance(self):
        route = copy.deepcopy(ROUTE)
        route['metadata']['generation'] = 3
        self.assertEqual(cluster.route_urls([route], {'argocd-argocd'}, ':8443'), {})

    def test_environment_port_and_platform_scope(self):
        self.assertEqual(cluster.route_urls([ROUTE], {'argocd-argocd'}, ':8443'),
                         {'argocd/argocd': 'https://argocd.localhost:8443/'})
        self.assertEqual(cluster.route_urls([ROUTE], {'other-app'}, ''), {})

    def wait(self, names, routes, reachable=True):
        def response(*args):
            return json.dumps({'items': [READY] if 'applications' in args else routes})
        with patch.object(cluster, 'expected_apps', return_value=names), \
             patch.object(cluster, 'platform_application_set', return_value={
                 'metadata': {'annotations': {'blackstorm.dev/public-https-port': '8443'}}}), \
             patch.object(cluster, 'run', side_effect=response), \
             patch.object(cluster, 'remote_revision', return_value='current'), \
             patch.object(cluster, 'reachable', return_value=reachable), \
             patch('sys.stdout', new_callable=io.StringIO) as output, \
             patch('sys.stderr', new_callable=io.StringIO):
            cluster.wait_for_platform('local', timeout=0, interval=1)
            return output.getvalue()

    def test_missing_application_times_out_with_resume_command(self):
        with self.assertRaisesRegex(RuntimeError, 'make cluster-wait ENV=local'):
            self.wait({'argocd-argocd', 'identity-dex'}, [ROUTE])

    def test_healthy_apps_with_unattached_route_do_not_succeed(self):
        route = copy.deepcopy(ROUTE)
        route['status'] = {}
        with self.assertRaises(RuntimeError):
            self.wait({'argocd-argocd'}, [route])

    def test_healthy_apps_with_unreachable_url_do_not_succeed(self):
        with self.assertRaises(RuntimeError):
            self.wait({'argocd-argocd'}, [ROUTE], reachable=False)

    def test_ready_platform_prints_urls(self):
        output = self.wait({'argocd-argocd'}, [ROUTE])
        self.assertIn('Plataforma lista', output)
        self.assertIn('https://argocd.localhost:8443/', output)


if __name__ == '__main__':
    unittest.main()
