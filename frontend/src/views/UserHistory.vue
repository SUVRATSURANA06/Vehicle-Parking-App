<template>
  <DashboardLayout :isAdmin="false">
    <div class="main-content d-flex flex-column align-items-center justify-content-start" style="max-width: 1000px; min-height: 80vh; margin: 0 auto;">
      <h1 class="h3 mb-4 mt-3">
        <i class="bi bi-clock-history"></i> Parking History
      </h1>
      <!-- Summary Graph -->
      <div class="card w-100 mb-4">
        <div class="card-header">
          <h5 class="mb-0">Summary on already used parking spots</h5>
        </div>
        <div class="card-body">
          <canvas id="summaryChart" height="80"></canvas>
        </div>
      </div>
      
      <!-- Stats Cards -->
      <div class="row w-100 mb-4">
        <div class="col-md-4 mb-3">
          <div class="card text-center shadow-sm">
            <div class="card-body">
              <i class="bi bi-list-check" style="font-size: 2rem; color: #3498db;"></i>
              <h5 class="card-title mt-2">Total Sessions</h5>
              <p class="card-text display-6 fw-bold">{{ totalSessions }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="card text-center shadow-sm">
            <div class="card-body">
              <i class="bi bi-currency-rupee" style="font-size: 2rem; color: #27ae60;"></i>
              <h5 class="card-title mt-2">Total Spent</h5>
              <p class="card-text display-6 fw-bold">{{ formatINR(totalSpent) }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="card text-center shadow-sm">
            <div class="card-body">
              <i class="bi bi-clock" style="font-size: 2rem; color: #e74c3c;"></i>
              <h5 class="card-title mt-2">This Month</h5>
              <p class="card-text display-6 fw-bold">{{ thisMonthSessions }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card w-100 mb-4">
        <div class="card-body">
          <div class="row align-items-end">
            <div class="col-md-3 mb-2">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="loadHistory">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="col-md-3 mb-2">
              <label class="form-label">Sort By</label>
              <select v-model="filters.sort" class="form-select" @change="loadHistory">
                <option value="created_at">Date Created</option>
                <option value="parking_timestamp">Start Time</option>
                <option value="parking_cost">Cost</option>
              </select>
            </div>
            <div class="col-md-3 mb-2">
              <label class="form-label">Order</label>
              <select v-model="filters.order" class="form-select" @change="loadHistory">
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
            <div class="col-md-3 mb-2">
              <button class="btn btn-outline-secondary w-100" @click="exportHistory" :disabled="exporting">
                <i class="bi bi-download"></i> {{ exporting ? 'Exporting...' : 'Export CSV' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- History Table -->
      <div class="card w-100 mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Your Parking Sessions</h5>
          <div>
            <button class="btn btn-sm btn-outline-primary me-2" @click="loadHistory" :disabled="loading">
              <i class="bi bi-arrow-clockwise"></i> {{ loading ? 'Loading...' : 'Refresh' }}
            </button>
            <a v-if="exportDownloadUrl" :href="exportDownloadUrl" class="btn btn-sm btn-success" download>
              <i class="bi bi-download"></i> Download CSV
            </a>
            <span v-if="exportError" class="text-danger ms-2">{{ exportError }}</span>
          </div>
        </div>
        <div class="card-body">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading parking history...</p>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="history.length === 0" class="text-center py-5">
            <i class="bi bi-clock-history" style="font-size: 3rem; color: #ccc;"></i>
            <h5 class="mt-3 text-muted">No parking history found</h5>
            <p class="text-muted">Start by booking your first parking spot!</p>
            <router-link to="/user/parking-lots" class="btn btn-primary">
              <i class="bi bi-p-circle"></i> Book Parking Spot
            </router-link>
          </div>
          
          <!-- History Table -->
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Location</th>
                  <th>Spot</th>
                  <th>Vehicle</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Duration</th>
                  <th>Cost</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="session in history" :key="session.id">
                  <td>
                    <span class="badge bg-secondary">#{{ session.id }}</span>
                  </td>
                  <td>
                    <strong>{{ session.lot?.name || 'N/A' }}</strong>
                    <br>
                    <small class="text-muted">{{ session.lot?.address || 'N/A' }}</small>
                  </td>
                  <td>
                    <span class="badge bg-info">{{ session.spot?.spot_number || 'N/A' }}</span>
                  </td>
                  <td>
                    <code>{{ session.vehicle_number }}</code>
                  </td>
                  <td>{{ formatDateTime(session.parking_timestamp) }}</td>
                  <td>{{ formatDateTime(session.released_time || session.leaving_timestamp) }}</td>
                  <td>
                    <span v-if="session.duration_hours" class="badge bg-light text-dark">
                      {{ session.duration_hours }}h
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <strong class="text-success">{{ formatINR(session.total_cost ?? session.parking_cost ?? 0) }}</strong>
                  </td>
                  <td>
                    <span :class="getStatusBadgeClass(session.status)">
                      {{ session.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > pagination.per_page" class="d-flex justify-content-center w-100">
        <nav aria-label="Parking history pagination">
          <ul class="pagination">
            <li class="page-item" :class="{ disabled: pagination.current_page === 1 }">
              <button class="page-link" @click="changePage(pagination.current_page - 1)" :disabled="pagination.current_page === 1">
                Previous
              </button>
            </li>
            <li v-for="page in getPageNumbers()" :key="page" class="page-item" :class="{ active: page === pagination.current_page }">
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: pagination.current_page === pagination.pages }">
              <button class="page-link" @click="changePage(pagination.current_page + 1)" :disabled="pagination.current_page === pagination.pages">
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { userAPI } from '@/services/api'
import DashboardLayout from '@/components/DashboardLayout.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'UserHistory',
  components: { DashboardLayout },
  setup() {
    const history = ref([])
    const loading = ref(false)
    const totalSessions = ref(0)
    const totalSpent = ref(0)
    const thisMonthSessions = ref(0)
    
    const pagination = reactive({
      current_page: 1,
      per_page: 10,
      total: 0,
      pages: 0
    })
    
    const filters = reactive({
      status: '',
      sort: 'created_at',
      order: 'desc'
    })
    const exportDownloadUrl = ref('')
    const exportError = ref('')
    const exporting = ref(false)

    let summaryChart = null

    const loadHistory = async () => {
      loading.value = true
      try {
        // Send filters as query params
        const params = new URLSearchParams({
          page: pagination.current_page,
          status: filters.status,
          sort: filters.sort,
          order: filters.order
        })
        const response = await userAPI.getHistory(params.toString())
        if (response.data) {
          history.value = response.data.items || []
          pagination.total = response.data.total || 0
          pagination.pages = response.data.pages || 0
          pagination.current_page = response.data.current_page || 1
        }
      } catch (error) {
        console.error('Error loading history:', error)
        history.value = []
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        const response = await userAPI.getParkingStats()
        if (response.data) {
          totalSessions.value = response.data.total_reservations || 0
          totalSpent.value = response.data.total_spent || 0
          thisMonthSessions.value = response.data.this_month || 0
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= pagination.pages) {
        pagination.current_page = page
        loadHistory()
      }
    }

    const getPageNumbers = () => {
      const pages = []
      const start = Math.max(1, pagination.current_page - 2)
      const end = Math.min(pagination.pages, pagination.current_page + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    }

    // CSV Export logic
    const exportHistory = async () => {
      exportError.value = ''
      exportDownloadUrl.value = ''
      try {
        console.log('Starting CSV export...')
        const response = await userAPI.exportCSV()
        console.log('Export response:', response.data)
        if (response.data.success && response.data.download_url) {
          exportDownloadUrl.value = response.data.download_url
          alert('CSV export completed! Click the download link.')
        } else {
          alert('Failed to export: ' + (response.data.message || 'Unknown error'))
        }
      } catch (error) {
        console.error('Export error:', error)
        alert('Failed to export history: ' + error.message)
      }
    }


    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${day}/${month}/${year} ${hours}:${minutes}`
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'active':
          return 'badge bg-success'
        case 'completed':
          return 'badge bg-primary'
        case 'cancelled':
          return 'badge bg-danger'
        default:
          return 'badge bg-secondary'
      }
    }

    // INR currency formatter
    const formatINR = (amount) => {
      return amount != null
        ? amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
        : '₹0.00'
    }

    // Draw summary chart
    const drawSummaryChart = () => {
      // Aggregate sessions per lot
      const lotCounts = {}
      history.value.forEach(session => {
        const lotName = session.lot?.name || 'Unknown'
        lotCounts[lotName] = (lotCounts[lotName] || 0) + 1
      })
      const labels = Object.keys(lotCounts)
      const data = Object.values(lotCounts)
      const ctx = document.getElementById('summaryChart').getContext('2d')
      if (summaryChart) summaryChart.destroy()
      summaryChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Sessions per Lot',
            data,
            backgroundColor: ['#6fcf97', '#56ccf2', '#eb5757', '#f2c94c', '#bb6bd9'],
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: false }
          },
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1 } }
          }
        }
      })
    }
    // Redraw chart when history changes
    watch(history, () => {
      setTimeout(drawSummaryChart, 100) // Wait for DOM
    })

    onMounted(() => {
      loadHistory()
      loadStats()
      setTimeout(drawSummaryChart, 500)
    })

    return {
      history,
      loading,
      totalSessions,
      totalSpent,
      thisMonthSessions,
      pagination,
      filters,
      loadHistory,
      changePage,
      getPageNumbers,
      exportHistory,
      formatDateTime,
      getStatusBadgeClass,
      formatINR,
      exportDownloadUrl,
      exportError,
      summaryChart
    }
  }
}
</script>

<style scoped>
.main-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 76px);
  padding: 2rem 1.5rem;
}

.card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
}

code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875rem;
}

.pagination .page-link {
  color: #3498db;
  border-color: #dee2e6;
}

.pagination .page-item.active .page-link {
  background-color: #3498db;
  border-color: #3498db;
}

.pagination .page-link:hover {
  color: #2980b9;
  background-color: #e9ecef;
}
</style> 