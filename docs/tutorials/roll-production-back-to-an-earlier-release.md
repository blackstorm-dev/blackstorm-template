# Roll production back to an earlier release

Rolling back means promoting the release that ran before. It restores the image and its
configuration together.

## Steps

1. A release misbehaves in production. Open its Kargo project to roll it back.
2. Check which release production runs.
3. Kargo keeps every release, newest first, each with its image and configuration.
4. The release that came before is still there. Rolling back means promoting it again.
5. The review shows what production goes back to: the earlier image and its configuration.
6. Kargo publishes the earlier manifests again and Argo CD synchronizes production.
7. Production runs the earlier release again. Staging keeps the newer release.

<video controls preload="metadata" width="100%" src="../../videos/roll-production-back-to-an-earlier-release.mp4"></video>

## Source

`tests/tutorials/test_kargo_rollback.py`
