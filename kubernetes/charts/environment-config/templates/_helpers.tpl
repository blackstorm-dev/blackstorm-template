{{- define "environment.host" -}}
{{- printf "%s.%s" .name .config.domain -}}
{{- end -}}
{{- define "environment.url" -}}
{{- $host := include "environment.host" . -}}
{{- $port := int (default 443 .config.cluster.httpsPort) -}}
{{- if eq $port 443 -}}https://{{ $host }}{{- else -}}https://{{ $host }}:{{ $port }}{{- end -}}
{{- end -}}
{{- define "environment.repoURL" -}}
{{- printf "git@github.com:%s/%s.git" .Values.github.organization .Values.github.infrastructureRepository -}}
{{- end -}}
