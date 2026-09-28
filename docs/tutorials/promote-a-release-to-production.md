# Promote a release to production

Staging receives every release automatically. Production only changes when someone promotes a
release that staging already verified.

## Steps

1. Each application has its own Kargo project. Open the one to release.
2. Staging receives every release automatically, as soon as CI publishes it.
3. Production only changes when someone promotes a release to it.
4. Review what changes: the image and the configuration commit travel together.
5. Only a release verified in staging can reach production.
6. Kargo renders the manifests, pushes them and Argo CD synchronizes production.
7. Production now runs the promoted release. Kargo marks it healthy once the rollout finishes.

<video controls preload="metadata" width="100%" src="../../videos/promote-a-release-to-production.mp4"></video>

## Source

`tests/tutorials/test_kargo_promote.py`
