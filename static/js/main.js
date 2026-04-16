// Theme toggle — persists in localStorage
(function () {
  const btn   = document.getElementById("themeToggle");
  const html  = document.documentElement;
  const saved = localStorage.getItem("theme") || "dark";

  html.setAttribute("data-theme", saved);
  if (btn) btn.textContent = saved === "dark" ? "🌙" : "☀️";

  if (btn) {
    btn.addEventListener("click", () => {
      const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      btn.textContent = next === "dark" ? "🌙" : "☀️";
    });
  }
})();
