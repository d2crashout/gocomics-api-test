const DEFAULT_BACKEND_BASE_URL = "https://your-render-backend.onrender.com";
const storedBackendUrl = localStorage.getItem("backendBaseUrl");

const backendInput = document.getElementById("backend-url");
const saveBackendButton = document.getElementById("save-backend-url");
const checkBackendButton = document.getElementById("check-backend");
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

function normalizedBackendUrl(raw) {
  return raw.trim().replace(/\/+$/, "");
}

async function parseJsonSafely(response) {
  try {
    return await response.json();
  } catch {
    return {};
  }
}

saveBackendButton.addEventListener("click", () => {
  backendBaseUrl = normalizedBackendUrl(backendInput.value);
  localStorage.setItem("backendBaseUrl", backendBaseUrl);
  statusEl.textContent = `Saved backend URL: ${backendBaseUrl}`;
});

checkBackendButton.addEventListener("click", async () => {
  backendBaseUrl = normalizedBackendUrl(backendInput.value);
  statusEl.textContent = "Checking backend health...";
  try {
    const response = await fetch(`${backendBaseUrl}/health`);
    const body = await parseJsonSafely(response);
    if (!response.ok) {
      throw new Error(body.error || `Health check failed with status ${response.status}`);
    }
    statusEl.textContent = `Backend is reachable (${body.status || "ok"}).`;
  } catch (error) {
    statusEl.textContent = `Backend check failed: ${error.message}`;
  }
});

button.addEventListener("click", async () => {
  backendBaseUrl = normalizedBackendUrl(backendInput.value);
  statusEl.textContent = "Loading a random Big Nate comic...";

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    const response = await fetch(`${backendBaseUrl}/api/random-big-nate`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const body = await parseJsonSafely(response);
    if (!response.ok) {
      throw new Error(body.error || `Backend returned status ${response.status}`);
    }

    titleEl.textContent = body.title || "Big Nate";
    dateEl.textContent = body.published_date ? `Published: ${body.published_date}` : "";
    imageEl.src = body.image_url;
    linkEl.href = body.page_url || body.image_url;
    comicSection.hidden = false;
    statusEl.textContent = "Comic loaded successfully.";
  } catch (error) {
    const timeoutMessage = "Request timed out after 15s.";
    const message = error?.name === "AbortError"
      ? `${timeoutMessage} Check backend logs and /api/debug/comics.`
      : `Could not load a comic: ${error.message}`;
    statusEl.textContent = message;
  }
});
