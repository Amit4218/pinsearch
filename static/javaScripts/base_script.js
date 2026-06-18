document.addEventListener("DOMContentLoaded", () => {
  // 1. Theme Toggle Configuration (Runs on ALL pages)
  const themeToggle = document.getElementById("themeToggle");

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      }
    });
  }

  // 2. Search Dynamic Form Configuration
  const form = document.getElementById("searchForm");
  const btn = document.getElementById("searchBtn");
  const mainContainer = document.getElementById("mainContainer");
  const searchBlock = document.getElementById("searchBlock");
  const resultState = document.getElementById("resultState");
  const errorBox = document.getElementById("error");

  const fields = [
    "circlename",
    "regionname",
    "divisionname",
    "officename",
    "pincode",
    "officetype",
    "delivery",
    "district",
    "statename",
    "latitude",
    "longitude",
  ];

  // Exit quietly here if the user is on documentation pages so it doesn't break
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const pincodeInput = document.getElementById("pincode");
    const pincode = pincodeInput?.value?.trim();

    if (!pincode) return;

    if (errorBox) errorBox.classList.add("hidden");
    if (btn) {
      btn.disabled = true;
      btn.innerText = "WAIT...";
    }

    try {
      const response = await fetch(
        `/api/v1/pincode?q=${encodeURIComponent(pincode)}`,
      );
      if (!response.ok) throw new Error();

      const data = await response.json();

      // Update text details fields
      fields.forEach((field) => {
        const el = document.getElementById(`res-${field}`);
        if (el) el.textContent = data[field] ?? "-";
      });

      // DYNAMIC MAP BUTTON CONFIGURATION (Now safely inside the success loop)
      const mapBtn = document.getElementById("res-mapBtn");
      if (mapBtn) {
        const lat = data.latitude;
        const lng = data.longitude;

        if (lat && lng && lat !== "-" && lng !== "-") {
          mapBtn.href = `https://www.google.com/maps?q=${lat},${lng}`;
          mapBtn.classList.remove("hidden");
          mapBtn.classList.add("inline-flex");
        } else {
          mapBtn.classList.add("hidden");
          mapBtn.classList.remove("inline-flex");
          mapBtn.href = "#";
        }
      }

      // Transition layouts
      if (mainContainer)
        mainContainer.classList.remove("justify-center", "min-h-[60vh]");
      if (searchBlock)
        searchBlock.classList.add(
          "border-b",
          "border-slate-100",
          "dark:border-slate-900",
          "pb-4",
        );

      if (resultState) {
        resultState.classList.remove("hidden");
        setTimeout(() => resultState.classList.add("opacity-100"), 50);
      }
    } catch (err) {
      if (resultState) {
        resultState.classList.add("hidden");
        resultState.classList.remove("opacity-100");
      }
      if (searchBlock)
        searchBlock.classList.remove(
          "border-b",
          "border-slate-100",
          "dark:border-slate-900",
          "pb-4",
        );
      if (mainContainer)
        mainContainer.classList.add("justify-center", "min-h-[60vh]");
      if (errorBox) errorBox.classList.remove("hidden");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "SEARCH";
      }
    }
  });
});
