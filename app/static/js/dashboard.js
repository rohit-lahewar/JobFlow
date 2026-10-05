/**
 * Dashboard Charts Initialization using Chart.js
 */

function initDashboardCharts(statusData, monthlyData) {
  // 1. Status Donut Chart
  const statusCtx = document.getElementById('statusChart');
  if (statusCtx && statusData) {
    const statusColors = {
      'Applied': '#0284c7',
      'Shortlisted': '#4f46e5',
      'Interview': '#f59e0b',
      'Offer': '#10b981',
      'Rejected': '#ef4444',
      'Withdrawn': '#64748b'
    };

    const backgroundColors = statusData.labels.map(l => statusColors[l] || '#94a3b8');

    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: statusData.labels,
        datasets: [{
          data: statusData.data,
          backgroundColor: backgroundColors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { family: "'Inter', sans-serif", size: 12 }
            }
          }
        }
      }
    });
  }

  // 2. Monthly Application Bar Chart
  const monthlyCtx = document.getElementById('monthlyChart');
  if (monthlyCtx && monthlyData) {
    new Chart(monthlyCtx, {
      type: 'bar',
      data: {
        labels: monthlyData.labels,
        datasets: [{
          label: 'Applications',
          data: monthlyData.data,
          backgroundColor: 'rgba(79, 70, 229, 0.85)',
          borderRadius: 6,
          hoverBackgroundColor: '#4338ca'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
              font: { family: "'Inter', sans-serif" }
            },
            grid: {
              color: '#f1f5f9'
            }
          },
          x: {
            ticks: {
              font: { family: "'Inter', sans-serif" }
            },
            grid: { display: false }
          }
        }
      }
    });
  }
}
