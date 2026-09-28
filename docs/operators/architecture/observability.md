# Observability

![Metrics, logs, traces, and alerts](../../resources/observability.png){ loading=lazy }

## Components

| Component | Role | Defined in |
|---|---|---|
| Alloy | One per node. Reads pod logs and receives OTLP traces | `kubernetes/apps/o11y/alloy/` |
| Loki | Stores logs | `kubernetes/apps/o11y/loki/` |
| Tempo | Stores traces | `kubernetes/apps/o11y/tempo/` |
| Prometheus | Collects metrics from every `ServiceMonitor` labelled `release: monitoring` | `kubernetes/apps/o11y/kube-prometheus-stack/` |
| Alertmanager | Routes alerts to the configured receivers | `kubernetes/apps/o11y/kube-prometheus-stack/` |
| Grafana | Queries and dashboards | `kubernetes/apps/o11y/kube-prometheus-stack/` |
| Gatus | Checks every published `HTTPRoute` | `kubernetes/apps/o11y/gatus/` |

## Settings

| Setting | Value |
|---|---|
| Log retention | 72 hours |
| Trace retention | 72 hours |
| Metric retention | 7 days, up to 4 GB |
| OTLP endpoints | `alloy.o11y.svc.cluster.local`, gRPC `4317` and HTTP `4318` |

## Logs and traces are linked

| From | To | How |
|---|---|---|
| A log line | Its trace | The `trace_id` field of the line |
| A trace | The logs of its pod | The attributes `k8s.namespace.name` and `k8s.pod.name` |

```yaml title="kubernetes/apps/o11y/loki/grafana-datasource.yaml"
jsonData:
  derivedFields:
    - name: TraceID
      matcherRegex: '"trace_id"\s*:\s*"([a-f0-9]{32})"' # (1)!
      datasourceUid: tempo
```

1.  Applications must log JSON with a 32-character `trace_id`.

## Dashboards

Dashboards ship as ConfigMaps labelled `grafana_dashboard: "1"`.

```yaml title="kubernetes/apps/o11y/kube-prometheus-stack/kustomization.yaml"
configMapGenerator:
  - name: monitoring-extra-dashboards
    files:
      - dashboards/gatus.json
      - dashboards/velero.json
    options:
      labels:
        grafana_dashboard: "1"
```

!!! warning "Alerts have no receiver yet"

    Alertmanager runs, but no channel is configured.
