# Continuous integration

Pushes to `main` or `master` run the checks and publish a validated release. Documentation-only
changes are excluded; unchanged application images can be reused.

Opening or updating a pull request does not run workflows. Maintainers can review the proposal
and manually run checks on a branch in their repository before merging it. Manual runs do not
publish images or release tags.

## Set it up, once

| Item | Command |
|---|---|
| Key for CI | `make init` |
| Registry namespace | `gh variable set DOCKERHUB_NAMESPACE --body '<namespace>'` |
| Registry credentials | `make secrets FILE=secrets/dockerhub.env` |

## What your workflow must publish

A release is one Git tag plus one image per entry in `deploy/platform.yaml`.

=== "commit-sha"

    | Output | Name |
    |---|---|
    | Image | `<namespace>/my-app:<commit-sha>` |
    | Git tag | `ci-<run>-<attempt>-<commit-sha>` |

    The template workflow already does this.

=== "coordinated-tags"

    | Output | Name |
    |---|---|
    | Every image | `<image>:blackstorm-ci-<run>-<attempt>` |
    | Git tag | `blackstorm-ci-<run>-<attempt>` |

    Use it when a release has several images. It is the default.

`<run>` has ten digits and `<attempt>` has three: `ci-0000000022-001-…`.

!!! info "Staging only receives complete releases"

    If the tag or one image is missing, nothing is promoted.

## Run checks manually

```bash
gh workflow run ci.yaml --ref main
gh run watch <run-id> --exit-status
```

## Try it before pushing

```bash
python3 -m unittest discover -s tests -v
docker build -t my-app .
docker run --rm -p 127.0.0.1:8080:8080 my-app
curl --fail http://127.0.0.1:8080/healthz
```
