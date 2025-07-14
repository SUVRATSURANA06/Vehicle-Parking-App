<template>
  <div class="admin-summary-mockup">
    <!-- Playful Top Bar -->
    <div class="admin-topbar">
      <div class="admin-welcome">Welcome to Admin</div>
      <div class="admin-center-links">
        <router-link to="/admin/dashboard">Home</router-link>
        <span class="bar">|</span>
        <router-link to="/admin/users">Users</router-link>
        <span class="bar">|</span>
        <router-link to="/admin/search">Search</router-link>
        <span class="bar">|</span>
        <router-link to="/admin/analytics">Summary</router-link>
        <span class="bar">|</span>
        <a href="#" @click.prevent="logout">Logout</a>
      </div>
      <div class="admin-edit-profile">
        <router-link to="/admin/profile">Edit Profile</router-link>
      </div>
    </div>
    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">Revenue from each parking lot</div>
        <canvas ref="revenueChart"></canvas>
        <div class="custom-legend mt-3">
          <div v-for="(lot, idx) in lotNames" :key="lot" class="legend-row">
            <span class="legend-color-box" :style="{ backgroundColor: chartColors[idx % chartColors.length], borderColor: '#222' }"></span>
            <span class="legend-label">{{ lot }}</span>
            <span class="legend-value">{{ formatINR(lotRevenue[idx] || 0) }}</span>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Summary on available and occupied parking lots</div>
        <canvas ref="occupancyChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminAnalytics',
  setup() {
    const revenueChart = ref(null)
    const occupancyChart = ref(null)
    const logout = () => { window.location.href = '/login' }
    // Data
    const lotNames = ref([])
    const lotRevenue = ref([])
    const availableSpots = ref([])
    const occupiedSpots = ref([])
    const chartColors = ['#90cdf4', '#a3e635', '#fbbf24', '#f87171', '#f472b6']
    // Load analytics and lots
    const loadCharts = async () => {
      try {
        const analyticsRes = await adminAPI.getAnalytics()
        const lotsRes = await adminAPI.getParkingLots()
        // --- Sort lots by total spots (descending) ---
        let lotsSorted = lotsRes.data.slice().sort((a, b) => b.number_of_spots - a.number_of_spots)
        // --- Prepare chart data arrays in this order ---
        lotNames.value = lotsSorted.map(lot => lot.name)
        availableSpots.value = lotsSorted.map(lot => lot.available_spots)
        occupiedSpots.value = lotsSorted.map(lot => lot.occupied_spots)
        // For revenue, match the order to lotNames
        lotRevenue.value = lotNames.value.map(name => (analyticsRes.data.lot_revenue || {})[name] || 0)
        // Draw charts
        drawRevenueChart()
        drawOccupancyChart()
      } catch (e) {}
    }
    // Draw donut chart for revenue
    const drawRevenueChart = () => {
      if (revenueChart.value && revenueChart.value._chart) revenueChart.value._chart.destroy()
      const ctx = revenueChart.value.getContext('2d')
      revenueChart.value._chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: lotNames.value,
          datasets: [{
            data: lotRevenue.value,
            backgroundColor: chartColors,
            borderWidth: 3,
            borderColor: '#222',
          }]
        },
        options: {
          plugins: { legend: { labels: { font: { family: 'Comic Neue, Indie Flower, cursive' } } } },
          cutout: '65%',
        }
      })
    }
    // Draw bar chart for occupancy
    const drawOccupancyChart = () => {
      if (occupancyChart.value && occupancyChart.value._chart) occupancyChart.value._chart.destroy()
      const ctx = occupancyChart.value.getContext('2d')
      occupancyChart.value._chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: lotNames.value,
          datasets: [
            {
              label: 'Available',
              data: availableSpots.value,
              backgroundColor: '#a3e635',
              borderColor: '#222',
              borderWidth: 2
            },
            {
              label: 'Occupied',
              data: occupiedSpots.value,
              backgroundColor: '#f87171',
              borderColor: '#222',
              borderWidth: 2
            }
          ]
        },
        options: {
          plugins: { legend: { labels: { font: { family: 'Comic Neue, Indie Flower, cursive' } } } },
          scales: { x: { ticks: { font: { family: 'Comic Neue, Indie Flower, cursive' } } }, y: { beginAtZero: true } }
        }
      })
    }
    const formatINR = (amount) => {
      return amount != null
        ? amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
        : '₹0.00'
    }
    onMounted(() => {
      loadCharts()
    })
    return { revenueChart, occupancyChart, logout, lotNames, lotRevenue, chartColors, formatINR }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.admin-summary-mockup {
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  background: #fff;
  min-height: 100vh;
  padding: 0;
}
.admin-topbar {
  background: #c6f7c3;
  border-radius: 18px 18px 0 0;
  padding: 14px 28px 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: inherit;
  margin-bottom: 18px;
}
.admin-welcome {
  color: #e53935;
  font-weight: bold;
  font-size: 1.3rem;
}
.admin-center-links {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 1.15rem;
  color: #222;
  gap: 10px;
}
.admin-center-links .bar {
  color: #222;
  font-weight: bold;
}
.admin-center-links a, .admin-center-links router-link {
  color: #222;
  text-decoration: none;
  font-family: inherit;
}
.admin-center-links a:hover, .admin-center-links router-link:hover {
  text-decoration: underline;
}
.admin-edit-profile {
  font-size: 1.15rem;
  font-family: inherit;
}
.admin-edit-profile a, .admin-edit-profile router-link {
  color: #1976d2;
  font-weight: bold;
  text-decoration: none;
  font-family: inherit;
}
.admin-edit-profile a:hover, .admin-edit-profile router-link:hover {
  text-decoration: underline;
}
.summary-title {
  color: #ff9800;
  font-size: 2.1rem;
  font-family: inherit;
  font-weight: bold;
  text-align: center;
  margin-bottom: 18px;
  margin-top: 12px;
}
.charts-row {
  display: flex;
  gap: 48px;
  justify-content: center;
  align-items: flex-start;
  margin-top: 18px;
}
.chart-card {
  border: 2.5px solid #1976d2;
  border-radius: 24px;
  background: #f8faff;
  min-width: 340px;
  max-width: 420px;
  padding: 18px 18px 12px 18px;
  margin-bottom: 12px;
  font-family: inherit;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.chart-title {
  font-size: 1.2rem;
  color: #222;
  font-family: inherit;
  font-weight: bold;
  text-align: center;
  margin-bottom: 12px;
}
canvas {
  width: 320px !important;
  height: 220px !important;
  background: #fff;
  border-radius: 18px;
  border: 2px dashed #1976d2;
  margin-bottom: 8px;
}
.custom-legend {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 8px;
  margin-left: 12px;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.08rem;
  font-family: inherit;
  margin-bottom: 4px;
}
.legend-color-box {
  width: 32px;
  height: 14px;
  border-radius: 4px;
  border: 2px solid #222;
  display: inline-block;
  margin-right: 6px;
}
.legend-label {
  font-weight: bold;
  color: #555;
  min-width: 120px;
}
.legend-value {
  color: #888;
  font-size: 1rem;
  margin-left: 8px;
}
</style> 