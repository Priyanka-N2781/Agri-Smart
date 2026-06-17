/* AgriSmart – main.js */

// Init AOS
document.addEventListener("DOMContentLoaded", () => {
  AOS.init({ duration: 700, once: true, offset: 60 });

  // Active nav highlight
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === path) link.classList.add("active");
  });

  // Form loading state
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
      }
    });
  });

  // Navbar shrink on scroll
  const navbar = document.querySelector(".ag-navbar");
  window.addEventListener("scroll", () => {
    navbar.style.background = window.scrollY > 40
      ? "rgba(10,16,13,0.97)"
      : "rgba(10,16,13,0.82)";
  });
});
