/**
 * Analytics Charts Initialization using Chart.js
 */

function initAnalyticsCharts(analytics) {
  if (!analytics) return;

  // 1. Status Distribution Chart
  const statusCtx = document.getElementById('analyticsStatusChart');
  if (statusCtx && analytics.status_distribution) {
    const statusColors = {
      'Applied': '#0284c7',
      'Shortlisted': '#4f46e5',
      'Interview': '#f59e0b',
      'Offer': '#10b981',
      'Rejected': '#ef4444',
      'Withdrawn': '#64748b'
    };
    const bgColors = analytics.status_distribution.labels.map(l => statusColors[l] || '#94a3b8');

    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: analytics.status_distribution.labels,
        datasets: [{
          data: analytics.status_distribution.data,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, padding: 12, font: { family: "'Inter', sans-serif" } }
          }
        }
      }
    });
  }

  // 2. Monthly Applications Trend (Bar)
  const appTrendCtx = document.getElementById('monthlyAppsChart');
  if (appTrendCtx && analytics.monthly_applications) {
    new Chart(appTrendCtx, {
      type: 'bar',
      data: {
        labels: analytics.monthly_applications.labels,
        datasets: [{
          label: 'Applications Submitted',
          data: analytics.monthly_applications.data,
          backgroundColor: 'rgba(79, 70, 229, 0.85)',
          borderRadius: 6,
          hoverBackgroundColor: '#4338ca'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 3. Monthly Interviews Trend (Line)
  const ivTrendCtx = document.getElementById('monthlyInterviewsChart');
  if (ivTrendCtx && analytics.monthly_interviews) {
    new Chart(ivTrendCtx, {
      type: 'line',
      data: {
        labels: analytics.monthly_interviews.labels,
        datasets: [{
          label: 'Interviews Held',
          data: analytics.monthly_interviews.data,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 5,
          pointBackgroundColor: '#0284c7'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 4. Conversion Comparison: Offers vs Rejections vs Total
  const convCtx = document.getElementById('conversionComparisonChart');
  if (convCtx) {
    new Chart(convCtx, {
      type: 'bar',
      data: {
        labels: ['Total Applications', 'Reached Interview', 'Job Offers', 'Rejections'],
        datasets: [{
          data: [
            analytics.total_applications,
            analytics.apps_with_interviews,
            analytics.offers,
            analytics.rejections
          ],
          backgroundColor: [
            '#64748b',
            '#f59e0b',
            '#10b981',
            '#ef4444'
          ],
          borderRadius: 6
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
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 5. Work Mode Distribution (Polar/Pie)
  const workModeCtx = document.getElementById('workModeChart');
  if (workModeCtx && analytics.work_mode_distribution) {
    new Chart(workModeCtx, {
      type: 'pie',
      data: {
        labels: analytics.work_mode_distribution.labels,
        datasets: [{
          data: analytics.work_mode_distribution.data,
          backgroundColor: ['#4f46e5', '#06b6d4', '#8b5cf6'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
        }
      }
    });
  }
}
