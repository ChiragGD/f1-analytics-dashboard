document.addEventListener("DOMContentLoaded", function() {
  const ctx = document.getElementById("leaderboardChart");
  if (!ctx) return;

  const labels = window.chartNames || [];
  const points = window.chartPoints || [];

  const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, "#ff1e1e");
  gradient.addColorStop(0.5, "#ff8c00");
  gradient.addColorStop(1, "#ffd700");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Points",
        data: points,
        borderWidth: 2,
        backgroundColor: gradient,
        borderColor: "#fff",
        borderRadius: 6,
        hoverBorderWidth: 3,
        hoverBackgroundColor: "#00bfff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#fff", font: { family: "Orbitron", size: 14 } } },
        tooltip: { backgroundColor: "#000", titleColor: "#fff", bodyColor: "#ffd700" }
      },
      scales: {
        x: {
          ticks: { color: "#fff", font: { size: 12, family: "Inter" } },
          grid: { color: "rgba(255,255,255,0.03)" }
        },
        y: {
          beginAtZero: true,
          ticks: { color: "#fff" },
          grid: { color: "rgba(255,255,255,0.03)" }
        }
      }
    }
  });
});
