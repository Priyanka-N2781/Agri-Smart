/* AgriSmart - main.js */

document.addEventListener("DOMContentLoaded", () => {
  AOS.init({ duration: 700, once: true, offset: 60 });

  const isStaticPreview =
    window.location.hostname.endsWith("github.io") ||
    window.location.protocol === "file:";

  const showStaticResult = form => {
    const page = window.location.pathname;
    const resultArea = form.closest(".row")?.querySelector(".col-lg-7");
    if (!resultArea) return;

    const getValue = name => {
      const field = form.querySelector(`[name="${name}"]`);
      return field ? field.value : "";
    };

    let icon = "bi-check-circle-fill";
    let color = "#22c55e";
    let title = "Demo Result";
    let body =
      "This preview is running on GitHub Pages, so it shows a demo output. The full Flask backend runs when the project is deployed on a Python host.";

    if (page.includes("yield-prediction")) {
      const rainfall = Number(getValue("rainfall") || 800);
      const temp = Number(getValue("avg_temp") || 22);
      const pesticides = Number(getValue("pesticides") || 50);
      const estimate = Math.max(
        1.2,
        Math.min(9.8, rainfall / 320 + temp / 12 - pesticides / 850)
      ).toFixed(2);

      title = "Crop Yield Demo Result";
      body = `
        <div class="yield-number text-center my-4">
          <div class="yield-value">${estimate}</div>
          <div class="yield-unit">tonnes / hectare</div>
          <div class="yield-crop">${getValue("crop") || "Selected crop"}</div>
        </div>
      `;
    } else if (page.includes("disease-prediction")) {
      icon = "bi-bug-fill";
      color = "#f59e0b";
      title = "Disease Detection Demo Result";
      body =
        "Leaf image received in the preview. Full AI image classification requires the Flask backend.";
    } else if (page.includes("fertilizer-recommendation")) {
      icon = "bi-droplet-fill";
      color = "#8b5cf6";
      title = "Fertilizer Demo Recommendation";
      body = `Recommended plan for ${getValue("crop") || "selected crop"} in ${
        getValue("soil_type") || "selected soil"
      } soil: use a balanced NPK schedule and adjust after soil testing.`;
    } else if (page.includes("weather-prediction")) {
      icon = "bi-cloud-rain-fill";
      color = "#06b6d4";
      title = "Weather Demo Prediction";
      body = `Demo forecast generated for ${
        getValue("target_year") || "selected year"
      }. Full forecast calculation requires the Flask backend.`;
    }

    resultArea.innerHTML = `
      <div class="result-card">
        <div class="result-header" style="--res-color:${color}">
          <i class="bi ${icon} me-2"></i>${title}
        </div>
        <div class="result-body">
          ${body}
          <div class="alert alert-info mb-0">
            Static website preview is active. Backend ML predictions need Python hosting such as Render.
          </div>
        </div>
      </div>
    `;
  };

  // Active nav highlight
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === path) link.classList.add("active");
  });

  // Form behavior
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", event => {
      const btn = form.querySelector('[type="submit"]');

      if (isStaticPreview) {
        event.preventDefault();
        showStaticResult(form);
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<i class="bi bi-cpu me-2"></i>Run Demo Again';
        }
        return;
      }

      if (btn) {
        btn.disabled = true;
        btn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
      }
    });
  });

  // Navbar shrink on scroll
  const navbar = document.querySelector(".ag-navbar");
  window.addEventListener("scroll", () => {
    navbar.style.background =
      window.scrollY > 40 ? "rgba(10,16,13,0.97)" : "rgba(10,16,13,0.82)";
  });
});
