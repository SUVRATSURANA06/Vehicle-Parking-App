<template>
  <DashboardLayout :isAdmin="true">
    <div class="container-fluid">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0">
          <i class="bi bi-calendar-check"></i> Booking Management
        </h1>
        <button class="btn btn-outline-secondary" @click="loadBookings">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-2">
              <label class="form-label">Parking Lot</label>
              <select v-model="filters.lot_id" class="form-select" @change="loadBookings">
                <option value="">All Lots</option>
                <option v-for="lot in parkingLots" :key="lot.id" :value="lot.id">
                  {{ lot.name }}
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="loadBookings">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Date From</label>
              <input v-model="filters.date_from" type="date" class="form-control" @change="loadBookings" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Date To</label>
              <input v-model="filters.date_to" type="date" class="form-control" @change="loadBookings" />
            </div>
            <div class="col-md-2">
              <label class="form-label">&nbsp;</label>
              <button class="btn btn-outline-secondary w-100" @click="clearFilters">
                <i class="bi bi-x-circle"></i> Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Bookings Table -->
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">All Bookings ({{ bookings.length }})</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Vehicle</th>
                  <th>Lot</th>
                  <th>Spot</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Duration</th>
                  <th>Cost</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in bookings" :key="booking.id">
                  <td>#{{ booking.id }}</td>
                  <td>{{ booking.user?.full_name || 'Unknown' }}</td>
                  <td>{{ booking.vehicle_number || 'N/A' }}</td>
                  <td>{{ booking.lot?.name || 'Unknown' }}</td>
                  <td>{{ booking.spot?.spot_number || 'Unknown' }}</td>
                  <td>{{ formatDateTime(booking.parking_timestamp) }}</td>
                  <td>{{ formatDateTime(booking.leaving_timestamp) }}</td>
                  <td>{{ booking.duration_hours }}h</td>
                  <td>${{ booking.parking_cost?.toFixed(2) || '0.00' }}</td>
                  <td>
                    <span :class="`badge ${getStatusBadgeClass(booking.status)}`">
                      {{ booking.status }}
                    </span>
                  </td>
                  <td>
                    <button 
                      v-if="booking.status === 'active'"
                      class="btn btn-sm btn-outline-danger" 
                      @click="cancelBooking(booking)"
                    >
                      <i class="bi bi-x-circle"></i> Cancel
                    </button>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="bookings.length === 0" class="text-center py-5">
            <i class="bi bi-calendar-x" style="font-size: 3rem; color: #ccc;"></i>
            <h5 class="mt-3 text-muted">No bookings found</h5>
            <p class="text-muted">Try adjusting your filters or check back later.</p>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import DashboardLayout from '@/components/DashboardLayout.vue'

export default {
  name: 'AdminBookings',
  components: { DashboardLayout },
  setup() {
    const bookings = ref([])
    const parkingLots = ref([])
    const filters = ref({ lot_id: '', status: '', date_from: '', date_to: '' })
    const loading = ref(false)

    const loadBookings = async () => {
      loading.value = true
      try {
        const response = await adminAPI.getBookings(filters.value)
        bookings.value = response.data
      } catch (error) {
        console.error('Error loading bookings:', error)
      } finally {
        loading.value = false
      }
    }

    const loadParkingLots = async () => {
      try {
        const response = await adminAPI.getParkingLots()
        parkingLots.value = response.data
      } catch (error) {
        console.error('Error loading parking lots:', error)
      }
    }

    const clearFilters = () => {
      filters.value = { lot_id: '', status: '', date_from: '', date_to: '' }
      loadBookings()
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
        case 'active': return 'bg-success'
        case 'completed': return 'bg-primary'
        case 'cancelled': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const cancelBooking = async (booking) => {
      if (!confirm(`Are you sure you want to cancel booking #${booking.id}?`)) return
      
      try {
        await adminAPI.cancelBooking(booking.id)
        await loadBookings()
        alert('Booking cancelled successfully')
      } catch (error) {
        console.error('Error cancelling booking:', error)
        alert(error.response?.data?.message || 'Error cancelling booking')
      }
    }

    onMounted(() => {
      loadParkingLots()
      loadBookings()
    })

    return {
      bookings,
      parkingLots,
      filters,
      loading,
      loadBookings,
      clearFilters,
      formatDateTime,
      getStatusBadgeClass,
      cancelBooking
    }
  }
}
</script> 