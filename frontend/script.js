const BACKEND_BASE_URL = window.BACKEND_BASE_URL || "https://your-render-backend.onrender.com";

const button = document.getElementById("fetch-comic");
const statusEl = document.getElementById("status");
const comicSection = document.getElementById("comic");
const titleEl = document.getElementById("comic-title");
const dateEl = document.getElementById("comic-date");
const imageEl = document.getElementById("comic-image");
const linkEl = document.getElementById("comic-link");

button.addEventListener("click", async () => {
  statusEl.textContent = "Loading a random Big Nate comic...";

  try {
    const response = await fetch(`${BACKEND_BASE_URL}/api/random-big-nate`);
    if (!response.ok) throw new Error("Request failed");

    const comic = await response.json();
    titleEl.textContent = comic.title || "Big Nate";
    dateEl.textContent = comic.published_date ? `Published: ${comic.published_date}` : "";
    imageEl.src = comic.image_url;
    linkEl.href = comic.page_url || comic.image_url;
    comicSection.hidden = false;
    statusEl.textContent = "";
  } catch {
    statusEl.textContent = "Could not load a comic. Check your backend URL and try again.";
  }
});
