# Tutorials

Each tutorial is a recording of a browser test that runs against the local cluster. If the process
changes, the test fails and the video is recorded again.

<div class="bs-gallery">
  <a class="bs-tutorial" href="promote-a-release-to-production/">
    <span class="bs-thumb">
      <img class="off-glb" src="../videos/promote-a-release-to-production.jpg" alt="" loading="lazy">
      <span class="bs-duration" data-video="../videos/promote-a-release-to-production.mp4"></span>
    </span>
    <span class="bs-tutorial__meta">Kargo · Developers</span>
    <span class="bs-tutorial__title">Promote a release to production</span>
    <span class="bs-tutorial__note">Production moves to the release that staging runs.</span>
  </a>
  <a class="bs-tutorial" href="roll-production-back-to-an-earlier-release/">
    <span class="bs-thumb">
      <img class="off-glb" src="../videos/roll-production-back-to-an-earlier-release.jpg" alt="" loading="lazy">
      <span class="bs-duration" data-video="../videos/roll-production-back-to-an-earlier-release.mp4"></span>
    </span>
    <span class="bs-tutorial__meta">Kargo · Developers</span>
    <span class="bs-tutorial__title">Roll production back to an earlier release</span>
    <span class="bs-tutorial__note">Production goes back one release, then is restored.</span>
  </a>
</div>

## Run them yourself

```bash
make test-tutorials ENV=local     # run every tutorial as a test, without recording
make tutorial-videos ENV=local    # record them: one MP4 per tutorial in var/tutorials/
```

!!! warning "Tutorials change the cluster"

    They promote for real, so they only run against the local cluster.
