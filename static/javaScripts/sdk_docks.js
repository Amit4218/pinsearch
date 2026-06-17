async function loadMarkdown() {
  const contentDiv = document.getElementById("markdown-content");
  const loadingDiv = document.getElementById("loading");

  try {
    // Fetches directly from your file system tree setup /static/sdk-docs.md
    const response = await fetch("/static/sdk-docs.md");
    if (!response.ok)
      throw new Error("Could not resolve markdown asset target.");

    const markdownText = await response.text();

    // Safely interpret data payload into compiled template nodes
    contentDiv.innerHTML = marked.parse(markdownText);

    // Swap presentation states
    if (loadingDiv) loadingDiv.classList.add("hidden");
    if (contentDiv) contentDiv.classList.remove("hidden");
  } catch (error) {
    console.error("Documentation stream failed:", error);
    if (loadingDiv) {
      loadingDiv.textContent =
        "ERROR // Failed to render specifications document.";
      loadingDiv.classList.add("text-red-500");
    }
  }
}

// Attach directly to DOM structure loader lifecycle
window.addEventListener("DOMContentLoaded", loadMarkdown);
