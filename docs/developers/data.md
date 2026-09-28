# Data and backups

| Your data lives in | Backed up when you |
|---|---|
| A volume | Annotate the Pod |
| PostgreSQL | Declare the database and its backup schedule |
| An external bucket | Nothing to do: it is outside the cluster |

## Back up a volume

```yaml title="deploy/base/deployment.yaml" hl_lines="5"
spec:
  template:
    metadata:
      annotations:
        backup.velero.io/backup-volumes: data # (1)!
    spec:
      containers:
        - name: app
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: app-data
```

1.  The name of the volume in the Pod, not of the claim. Volumes without it are not backed up.

## Declare a database

```yaml title="deploy/staging/database.yaml"
apiVersion: stackgres.io/v1
kind: SGCluster
metadata:
  name: postgres
spec:
  instances: 1
  postgres:
    version: "16"
  pods:
    persistentVolume:
      size: 10Gi
  configurations:
    backups:
      - sgObjectStorage: spaces # (1)!
        cronSchedule: "30 6 * * *" # (2)!
        retention: 7
```

1.  The bucket, declared in `objectstorage.yaml` with its credentials in `secrets/`.
2.  In UTC.

## Restore a database to a moment

```yaml title="deploy/staging/database.yaml"
apiVersion: stackgres.io/v1
kind: SGCluster
metadata:
  name: postgres-restored # (1)!
spec:
  initialData:
    restore:
      fromBackup:
        name: <backup>
        pointInTimeRecovery:
          restoreToTimestamp: "2026-09-27T14:32:00Z" # (2)!
```

1.  A restore creates a new database. The original is left untouched.
2.  In UTC.

## How far back you can go

| Data | Restore point |
|---|---|
| PostgreSQL | Any moment |
| A volume | The moment of each backup |

!!! warning "Restoring a volume needs an operator"
