---
title: Blackstorm Infra
hide:
  - navigation
  - toc
  - path
  - footer
---

<div class="bs-hero" markdown>

<p class="bs-eyebrow">GitOps platform for Kubernetes</p>

# Deploy, operate, and recover your applications

<p class="bs-lead">Push to main. Staging updates on its own and production is one click away. New
versions can take traffic gradually next to the stable one and back out on their own if they fail
to become healthy. Any release can be brought back.</p>

[Deploy your application](developers/first-release.md){ .md-button .md-button--primary }
[Run the platform](operators/quick-start.md){ .md-button }

</div>

<div class="bs-demo" markdown>

<p class="bs-demo-title">Promote a release to production</p>

<a href="tutorials/promote-a-release-to-production/"><img class="off-glb" src="resources/tutorials/promote-a-release-to-production.gif" alt="Promoting a release to production in Kargo"></a>

<p class="bs-caption">Recorded from a test that runs against the cluster.
<a href="tutorials/promote-a-release-to-production/">Watch the full tutorial</a> ·
<a href="tutorials/">More tutorials</a></p>

<p class="bs-demo-title">Roll out gradually with a canary</p>

<img class="off-glb" src="resources/tutorials/canary-deployment.gif" alt="A canary rollout in the Argo Rollouts dashboard" loading="lazy">

<p class="bs-caption">A real rollout in the Argo Rollouts dashboard; the two-minute pause is shortened.
<a href="developers/releases/#roll-out-gradually">Configure a canary</a></p>

</div>

## What you get

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Releases without rebuilding__

    ---

    The image that staging verified is the one production runs. Rolling back is promoting an
    earlier release.

-   :material-source-branch:{ .lg .middle } __Everything in Git__

    ---

    Components, environments, and secrets are declared in repositories. Argo CD keeps the cluster
    equal to them.

-   :material-key-variant:{ .lg .middle } __Encrypted secrets__

    ---

    Secrets live next to the code, encrypted with SOPS and age, and are decrypted only inside the
    cluster.

-   :material-chart-line:{ .lg .middle } __Observability built in__

    ---

    Logs, traces, metrics, and availability checks for every application, read from Grafana.

-   :material-shield-lock:{ .lg .middle } __No inbound ports__

    ---

    Public traffic arrives through an outbound tunnel. Dashboards sit behind an identity check.

-   :material-backup-restore:{ .lg .middle } __Backups__

    ---

    Volumes and Kubernetes resources with Velero. PostgreSQL to any point in time with StackGres.

</div>

## Start in one command

=== "I deploy an application"

    ```bash
    gh repo create blackstorm-dev/my-app --private \
      --template blackstorm-dev/project-template --clone
    ```

    Then follow [Your first release](developers/first-release.md).

=== "I run the platform"

    ```bash
    make init && make cluster ENV=local
    ```

    Then follow the [Quick start](operators/quick-start.md).

## Find your way

<div class="grid cards" markdown>

-   :material-code-braces:{ .lg .middle } __[Developers](developers/index.md)__

    ---

    What you do to ship, observe, and protect your application.

-   :material-server-network:{ .lg .middle } __[Operators](operators/index.md)__

    ---

    How the platform is built and how to keep it healthy.

-   :material-play-circle:{ .lg .middle } __[Tutorials](tutorials/index.md)__

    ---

    Recorded walkthroughs that are also tests.

-   :material-book-open-variant:{ .lg .middle } __[Reference](reference/index.md)__

    ---

    Components, interfaces, and the deployment contract.

</div>
