// Los tutoriales arrancan a 1,5x; el reproductor deja cambiar la velocidad.
const speedUp = () =>
  document.querySelectorAll("video").forEach((video) => {
    video.defaultPlaybackRate = 1.5;
    video.playbackRate = 1.5;
  });

// La galería muestra la duración real de cada video, leída del propio archivo.
const showDurations = () =>
  document.querySelectorAll(".bs-duration[data-video]").forEach((label) => {
    const probe = document.createElement("video");
    probe.preload = "metadata";
    probe.addEventListener("loadedmetadata", () => {
      const seconds = Math.round(probe.duration);
      label.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
    });
    probe.src = label.dataset.video;
  });

const setUp = () => {
  speedUp();
  showDurations();
};

if (window.document$) document$.subscribe(setUp);
else document.addEventListener("DOMContentLoaded", setUp);
