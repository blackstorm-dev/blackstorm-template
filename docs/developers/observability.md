# Observability

You add four things to your application. Everything else is already running.

| To get | You add |
|---|---|
| Logs | Nothing: write to standard output |
| Traces | Three environment variables |
| Metrics | A `/metrics` endpoint and a `ServiceMonitor` |
| Availability checks | One annotation |

## Logs

Write one JSON object per line. Add `trace_id` to jump from a line to its trace.

```json
{"level": "info", "message": "request served", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"}
```

## Traces

```yaml title="deploy/base/deployment.yaml"
env:
  - name: OTEL_SERVICE_NAME
    value: my-app
  - name: OTEL_RESOURCE_ATTRIBUTES
    value: k8s.namespace.name=$(POD_NAMESPACE),k8s.pod.name=$(POD_NAME) # (1)!
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: http://alloy.o11y.svc.cluster.local:4318
```

1.  Lets you jump from a trace to the logs of the same pod.

## Metrics

```yaml title="deploy/base/servicemonitor.yaml" hl_lines="6"
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: app
  labels:
    release: monitoring # (1)!
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: app
  endpoints:
    - port: metrics
      path: /metrics
```

1.  Without this label your metrics are not collected.

## Availability checks

```yaml title="deploy/staging/kustomization.yaml"
metadata:
  name: app
  annotations:
    gatus.home-operations.com/endpoint: |
      name: my-app-staging
      path: /healthz
```

## Where to look

| Question | Open |
|---|---|
| Is it up? | [Gatus](https://gatus.localhost:8443/) |
| What did it log? | [Grafana](https://grafana.localhost:8443/) → Explore → Loki |
| Why was this request slow? | Grafana → Explore → Tempo |
| How is it trending? | Grafana → Dashboards |

```text title="Logs of your application, in Loki"
{namespace="my-app-staging"}
```
