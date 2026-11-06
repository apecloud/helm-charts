# Casdoor Helm chart

Chart version `v1.753.1` adds a configurable startup probe to the Casdoor chart without upgrading the application. `appVersion` remains `v1.753.0`, and the default image remains `casbin/casdoor:v1.753.0`. Existing image overrides continue to apply.

## Startup probe

The startup probe requests HTTP `/` on the container's named `http` port.

| Value | Description | Default |
| --- | --- | --- |
| `probe.startup.enabled` | Render the startup probe | `true` |
| `probe.startup.failureThreshold` | Consecutive failed startup checks before the container is restarted | `60` |
| `probe.startup.periodSeconds` | Seconds between startup checks | `10` |
| `probe.startup.timeoutSeconds` | Timeout in seconds for each startup check | `5` |

The defaults provide a bounded, nominal 600-second startup allowance (`60 × 10s`). Kubernetes holds off liveness and readiness checks until the startup probe succeeds. If the failure threshold is reached, Kubernetes restarts the container. This allowance does not guarantee initialization will finish in every environment; tune it for the expected startup conditions.

Existing liveness and readiness probes remain enabled by default and unchanged, requesting HTTP `/` on the same named port. They resume their normal behavior after startup succeeds. Setting `probe.startup.enabled: false` omits only the startup probe.

Override startup settings in a values file, for example:

```yaml
probe:
  startup:
    enabled: true
    failureThreshold: 60
    periodSeconds: 10
    timeoutSeconds: 5
```

## Source and license

The chart is based on the upstream [Casdoor Helm chart](https://github.com/casdoor/casdoor-helm) at chart version `v1.753.0`, with a chart-only startup-probe backport. Other runtime templates and configuration are retained. Upstream source provenance is recorded in `Chart.yaml`; the Apache-2.0 license is included in [LICENSE](LICENSE).

The functional Helm connection-test hook is retained. Generated repository indexes and manifest snapshot fixtures are not included.

## Manual publication

The repository's **Release Chart** workflow (`.github/workflows/release-chart.yml`) includes `casdoor-helm-charts` in its `chart_dir` choices. Select that chart and leave `chart_version` empty to package the source version `v1.753.1` from `Chart.yaml`, preserving `appVersion: v1.753.0`.

Publication uses the existing shared release workflow at `apecloud/apecloud-cd/.github/workflows/release-charts.yml@v0.1.40` and the Helm repository at <https://apecloud.github.io/helm-charts>. A source change alone does not publish a chart; publication is a separate authorized workflow action.
