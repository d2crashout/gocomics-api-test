const DEFAULT_BACKEND_BASE_URL = "https://your-render-backend.onrender.com";
const storedBackendUrl = localStorage.getItem("backendBaseUrl");

const backendInput = document.getElementById("backend-url");
const saveBackendButton = document.getElementById("save-backend-url");
const button = document.getElementById("fetch-comic");
const statusEl = document.getElementById("status");
const comicSection = document.getElementById("comic");
const titleEl = document.getElementById("comic-title");
const dateEl = document.getElementById("comic-date");
const imageEl = document.getElementById("comic-image");
const linkEl = document.getElementById("comic-link");

let backendBaseUrl =
  window.BACKEND_BASE_URL || storedBackendUrl || DEFAULT_BACKEND_BASE_URL;
backendInput.value = backendBaseUrl;

saveBackendButton.addEventListener("click", () => {
  backendBaseUrl = backendInput.value.trim().replace(/\/+$/, "");
  localStorage.setItem("backendBaseUrl", backendBaseUrl);
  statusEl.textContent = `Saved backend URL: ${backendBaseUrl}`;
});

button.addEventListener("click", async () => {
  statusEl.textContent = "Loading a random Big Nate comic...";

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    const response = await fetch(`${backendBaseUrl}/api/random-big-nate`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error || "Backend request failed");
    }

    titleEl.textContent = body.title || "Big Nate";
    dateEl.textContent = body.published_date ? `Published: ${body.published_date}` : "";
    imageEl.src = body.image_url;
    linkEl.href = body.page_url || body.image_url;
    comicSection.hidden = false;
    statusEl.textContent = "Comic loaded successfully.";
  } catch (error) {
    const message = error?.name === "AbortError"
      ? "Request timed out after 15s. Check backend logs on Render."
      : `Could not load a comic: ${error.message}`;
    statusEl.textContent = message;
  }
});
