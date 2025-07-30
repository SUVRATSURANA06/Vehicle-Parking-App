<template>
  <div class="container-fluid py-4">
    <!-- Top Bar -->
    <div class="custom-topbar d-flex align-items-center justify-content-between mb-3">
      <div class="custom-welcome">Welcome to {{ userData?.first_name || userData?.username || 'User' }}</div>
      <div class="custom-center-links">
        <router-link to="/user/dashboard">Home</router-link>
        <span class="bar">|</span>
        <router-link to="/user/history">Summary</router-link>
        <span class="bar">|</span>
        <a href="#" @click.prevent="logout">Logout</a>
      </div>
      <div class="custom-edit-profile">
        <router-link to="/user/profile">Edit Profile</router-link>
      </div>
    </div>

    <!-- Recent Parking History -->
    <div class="mb-4">
      <h4 class="text-primary mb-2">Recent parking history</h4>
      <div class="card p-3">
        <div class="table-responsive">
          <table class="table table-bordered align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Location</th>
                <th>Vehicle No</th>
                <th>Timestamp</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reservation in recentReservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.lot?.name || 'N/A' }}</td>
                <td>{{ reservation.vehicle_number }}</td>
                <td>{{ formatDateTime(reservation.parking_timestamp) }}</td>
                <td>
                  <span v-if="reservation.released_time" class="badge bg-success">Parked Out</span>
                  <span v-else-if="reservation.parked_in_time" class="badge bg-info text-dark">Parked In</span>
                  <span v-else class="badge bg-warning text-dark">Booked</span>
                </td>
                <td>
                  <button v-if="!reservation.parked_in_time && !reservation.released_time" class="btn btn-sm btn-primary me-2" @click="markParkedIn(reservation)">Parked In</button>
                  <button v-else-if="reservation.parked_in_time" class="btn btn-sm btn-secondary me-2" disabled>Parked In</button>
                  <button v-if="reservation.parked_in_time && !reservation.released_time" class="btn btn-sm btn-danger" @click="releaseReservation(reservation)">Release</button>
                  <button v-else class="btn btn-sm btn-secondary" disabled>Release</button>
                  <span v-if="reservation.released_time" class="badge bg-success ms-2">Parked Out</span>
                </td>
              </tr>
              <tr v-if="recentReservations.length === 0">
                <td colspan="5" class="text-center text-muted">No recent parking history</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Search Parking -->
    <div class="mb-4">
      <span class="fw-bold text-danger">Search parking @location/pin code :</span>
      <input v-model="searchQuery" class="form-control d-inline-block w-auto ms-2" style="max-width: 250px; display: inline-block;" placeholder="UJJAIN" @input="filterLots" />
    </div>

    <!-- Parking Lots Table -->
    <div>
      <h4 class="text-primary mb-2">Parking Lots <span v-if="searchQuery">@ {{ searchQuery }}</span></h4>
      <div class="card p-3">
        <div class="table-responsive">
          <table class="table table-bordered align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Address</th>
                <th>Availability</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lot in filteredLots" :key="lot.id">
                <td>{{ lot.id }}</td>
                <td>{{ lot.address }}</td>
                <td>{{ lot.available_spots }}</td>
                <td>
                  <button class="btn btn-sm btn-primary" :disabled="lot.available_spots === 0" @click="openBookingModal(lot)">Book</button>
                </td>
              </tr>
              <tr v-if="filteredLots.length === 0">
                <td colspan="4" class="text-center text-muted">No parking lots found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Booking Modal (reuse from ParkingLots.vue) -->
    <div class="modal fade" id="bookingModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-p-circle"></i> Book Parking Spot
            </h5>
            <button type="button" class="btn-close" @click="closeBookingModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitBooking">
              <div class="mb-3">
                <label class="form-label">Parking Lot</label>
                <input class="form-control" :value="selectedLot?.name" readonly />
              </div>
              <div class="mb-3">
                <label class="form-label">Select Spot</label>
                <select v-model="bookingForm.spot_id" class="form-select" required>
                  <option value="" disabled>Choose a parking spot</option>
                  <option v-for="spot in availableSpots" :key="spot.id" :value="spot.id">
                    {{ spot.spot_number }}
                  </option>
                </select>
                <small class="text-muted">{{ availableSpots.length }} spots available</small>
              </div>
              <div v-if="bookingForm.spot_id">
                <div class="mb-3">
                  <label class="form-label">Spot ID</label>
                  <input class="form-control" :value="bookingForm.spot_id" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">Lot ID</label>
                  <input class="form-control" :value="selectedLot?.id" readonly />
                </div>
                <div class="mb-3">
                  <label class="form-label">User ID</label>
                  <input class="form-control" :value="userData?.id" readonly />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Vehicle Number</label>
                <input 
                  v-model="bookingForm.vehicle_number" 
                  class="form-control" 
                  required 
                  placeholder="Enter your vehicle number (e.g., MH12AB1234)"
                  pattern="[A-Z0-9]+"
                  title="Please enter a valid vehicle number"
                />
                <small class="text-muted">Enter your vehicle registration number</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Hourly Rate</label>
                <input class="form-control" :value="`${formatINR(selectedLot?.price)}/hour`" readonly />
              </div>
              <div class="modal-footer px-0">
                <button type="button" class="btn btn-secondary" @click="closeBookingModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="bookingLoading">
                  <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-circle me-2"></i>
                  {{ bookingLoading ? 'Reserving...' : 'Reserve Spot' }}
                </button>
              </div>
            </form>
            <div v-if="bookingError" class="alert alert-danger mt-3">
              <i class="bi bi-exclamation-triangle"></i> {{ bookingError }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Release Modal -->
    <div class="release-modal-backdrop" v-if="showReleaseModal">
      <div class="release-modal-frame">
        <div class="release-modal-header">
          Release the parking spot
        </div>
        <div class="release-modal-body">
          <div class="release-modal-row">
            <label>Spot_ID :</label>
            <input type="text" :value="releaseData.spot_id" readonly />
          </div>
          <div class="release-modal-row">
            <label>Vehicle Number :</label>
            <input type="text" :value="releaseData.vehicle_number" readonly />
          </div>
          <div class="release-modal-row">
            <label>Parking time :</label>
            <input type="text" :value="formatDateTime(releaseData.parked_in_time)" readonly />
          </div>
          <div class="release-modal-row">
            <label>Releasing time :</label>
            <input type="text" :value="formatDateTime(now)" readonly />
          </div>
          <div class="release-modal-row">
            <label>Total cost :</label>
            <input type="text" :value="releaseData.total_cost != null ? `₹${releaseData.total_cost}` : '---'" readonly />
          </div>
        </div>
        <div class="release-modal-footer">
          <button class="release-btn" @click="confirmRelease" :disabled="releaseLoading || releaseData.total_cost != null">Release</button>
          <button class="cancel-btn" @click="closeReleaseModal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI, authAPI } from '@/services/api'
import * as bootstrap from 'bootstrap'

export default {
  name: 'UserDashboard',
  setup() {
    const router = useRouter()
    // Robust user data check
    let storedUser = null
    try { storedUser = JSON.parse(localStorage.getItem('userData') || '{}') } catch { storedUser = null }
    const userData = ref(storedUser)
    if (!userData.value || !userData.value.id) {
      localStorage.removeItem('userData')
      router.push('/login')
    }
    const recentReservations = ref([])
    const allLots = ref([])
    const filteredLots = ref([])
    const searchQuery = ref('')
    // Booking modal state
    const selectedLot = ref(null)
    const availableSpots = ref([])
    const bookingForm = ref({ spot_id: '', vehicle_number: '' })
    const bookingLoading = ref(false)
    const bookingError = ref('')
    const dashboardLoading = ref(false)
    const actionLoading = ref(false)
    const actionMessage = ref('')
    const actionError = ref('')
    const showReleaseModal = ref(false)
    const releaseData = ref({})
    const releaseLoading = ref(false)
    const now = ref(new Date())
    const selectedReleaseReservation = ref(null)
    const totalSpent = ref(0)

    // Load dashboard data
    const loadDashboardData = async () => {
      dashboardLoading.value = true
      try {
        const response = await userAPI.getDashboard()
        if (response.data) {
          recentReservations.value = response.data.recent_reservations || []
          allLots.value = response.data.lots || []
          filteredLots.value = allLots.value
          totalSpent.value = response.data.total_spent || 0
        }
      } catch (error) {
        recentReservations.value = []
        allLots.value = []
        filteredLots.value = []
        totalSpent.value = 0
        actionError.value = 'Failed to load dashboard. Please try again.'
      } finally {
        dashboardLoading.value = false
      }
    }

    // Filter lots by search
    const filterLots = () => {
      if (!searchQuery.value) {
        filteredLots.value = allLots.value
      } else {
        const q = searchQuery.value.toLowerCase()
        filteredLots.value = allLots.value.filter(lot =>
          lot.address.toLowerCase().includes(q) ||
          lot.name.toLowerCase().includes(q) ||
          (lot.pin_code && lot.pin_code.toLowerCase().includes(q))
        )
      }
    }

    // Booking modal logic
    const openBookingModal = async (lot) => {
      selectedLot.value = lot
      bookingForm.value = { spot_id: '', vehicle_number: '' }
      bookingError.value = ''
      bookingLoading.value = false
      try {
        const response = await userAPI.getAvailableSpots(lot.id)
        availableSpots.value = response.data || []
        if (availableSpots.value.length === 0) {
          bookingError.value = 'No available spots in this lot.'
        }
      } catch (error) {
        availableSpots.value = []
        bookingError.value = 'Failed to load available spots'
      }
      const modal = new bootstrap.Modal(document.getElementById('bookingModal'))
      modal.show()
    }
    const closeBookingModal = () => {
      const modalEl = document.getElementById('bookingModal')
      const modal = bootstrap.Modal.getInstance(modalEl)
      if (modal) modal.hide()
      bookingForm.value = { spot_id: '', vehicle_number: '' }
      bookingError.value = ''
    }
    const submitBooking = async () => {
      if (!bookingForm.value.spot_id || !bookingForm.value.vehicle_number) {
        bookingError.value = 'Please fill in all required fields'
        return
      }
      if (availableSpots.value.length === 0) {
        bookingError.value = 'No available spots to book.'
        return
      }
      bookingLoading.value = true
      bookingError.value = ''
      try {
        const response = await userAPI.reserveSpot(selectedLot.value.id, bookingForm.value)
        if (response.data.success) {
          const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'))
          modal.hide()
          actionMessage.value = '🎉 Parking spot reserved successfully!'
          await loadDashboardData()
        } else {
          bookingError.value = response.data.message || 'Booking failed. Please try again.'
        }
      } catch (error) {
        bookingError.value = error.response?.data?.message || 'Booking failed. Please try again.'
      } finally {
        bookingLoading.value = false
      }
    }

    // Add methods for Parked In and Release actions
    const markParkedIn = async (reservation) => {
      if (actionLoading.value) return
      actionLoading.value = true
      actionError.value = ''
      try {
        const response = await userAPI.parkedIn(reservation.id)
        if (response.data.success) {
          actionMessage.value = 'Parked In time recorded.'
          await loadDashboardData()
        } else {
          actionError.value = response.data.message || 'Failed to mark Parked In.'
        }
      } catch (error) {
        actionError.value = error.response?.data?.message || 'Error marking Parked In'
      } finally {
        actionLoading.value = false
      }
    }
    const openReleaseModal = (reservation) => {
      releaseData.value = {
        spot_id: reservation.spot?.spot_number || reservation.spot_id,
        vehicle_number: reservation.vehicle_number,
        parked_in_time: reservation.parked_in_time,
        total_cost: reservation.total_cost
      }
      now.value = new Date()
      showReleaseModal.value = true
    }
    const closeReleaseModal = () => {
      showReleaseModal.value = false
      releaseLoading.value = false
    }
    const confirmRelease = async () => {
      if (releaseLoading.value || releaseData.value.total_cost != null) return
      releaseLoading.value = true
      try {
        const response = await userAPI.releaseReservation(selectedReleaseReservation.value.id)
        if (response.data.success) {
          // Show the calculated cost in the modal
          releaseData.value.total_cost = response.data.total_cost
          actionMessage.value = `Parking session released. Duration: ${response.data.duration} hours. Total cost: ₹${response.data.total_cost}`
          // Optionally, close the modal after a short delay
          setTimeout(() => {
            closeReleaseModal()
            loadDashboardData()
          }, 1800)
        } else {
          actionError.value = response.data.message || 'Failed to release reservation.'
        }
      } catch (error) {
        actionError.value = error.response?.data?.message || 'Error releasing reservation'
      } finally {
        releaseLoading.value = false
      }
    }
    const releaseReservation = (reservation) => {
      selectedReleaseReservation.value = reservation
      openReleaseModal(reservation)
    }

    // Logout
    const logout = async () => {
      try {
        await authAPI.logout()
        localStorage.removeItem('userData')
        router.push('/login')
      } catch (error) {}
    }

    // Format date/time
    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }
    // INR currency formatter
    const formatINR = (amount) => {
      return amount != null
        ? amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
        : '₹0.00'
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      userData,
      recentReservations,
      allLots,
      filteredLots,
      searchQuery,
      openBookingModal,
      closeBookingModal,
      submitBooking,
      selectedLot,
      availableSpots,
      bookingForm,
      bookingLoading,
      bookingError,
      filterLots,
      markParkedIn,
      releaseReservation,
      logout,
      formatDateTime,
      formatINR,
      dashboardLoading,
      actionLoading,
      actionMessage,
      actionError,
      showReleaseModal,
      releaseData,
      releaseLoading,
      now,
      selectedReleaseReservation,
      openReleaseModal,
      closeReleaseModal,
      confirmRelease
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.custom-topbar {
  background: #c6f7c3;
  border-radius: 18px 18px 0 0;
  padding: 12px 24px 12px 24px;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
}
.custom-welcome {
  color: #e53935;
  font-weight: bold;
  font-size: 1.2rem;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
}
.custom-center-links {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 1.2rem;
  color: #222;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
}
.custom-center-links .bar {
  margin: 0 10px;
  color: #222;
  font-weight: bold;
}
.custom-center-links a, .custom-center-links router-link {
  color: #222;
  text-decoration: none;
  font-family: inherit;
}
.custom-center-links a:hover, .custom-center-links router-link:hover {
  text-decoration: underline;
}
.custom-edit-profile {
  font-size: 1.2rem;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
}
.custom-edit-profile a, .custom-edit-profile router-link {
  color: #1976d2;
  font-weight: bold;
  text-decoration: none;
  font-family: inherit;
}
.custom-edit-profile a:hover, .custom-edit-profile router-link:hover {
  text-decoration: underline;
}
.table th, .table td {
  vertical-align: middle;
}
.table th {
  background-color: #f8f9fa;
}
.card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.bg-light {
  background-color: #eaf6ea !important;
}
.release-modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.release-modal-frame {
  background: #fffbe7;
  border: 3px solid #222;
  border-radius: 28px;
  min-width: 340px;
  max-width: 420px;
  width: 100%;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 0 0 18px 0;
  position: relative;
}
.release-modal-header {
  background: #ffe082;
  border-radius: 24px 24px 0 0;
  font-size: 1.4rem;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  font-weight: bold;
  color: #222;
  text-align: center;
  padding: 18px 0 12px 0;
  border-bottom: 2px solid #222;
}
.release-modal-body {
  padding: 18px 28px 0 28px;
}
.release-modal-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.release-modal-row label {
  flex: 1.2;
  font-size: 1.1rem;
  color: #222;
  font-family: inherit;
  font-weight: 500;
}
.release-modal-row input {
  flex: 2;
  border: 2px solid #222;
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 1.1rem;
  font-family: inherit;
  background: #fff;
  color: #e67e22;
  font-weight: bold;
  margin-left: 12px;
}
.release-modal-note {
  color: #e53935;
  font-size: 1rem;
  font-family: inherit;
  margin-top: 8px;
  margin-left: 8px;
}
.release-modal-footer {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 18px;
}
.release-btn, .cancel-btn {
  min-width: 120px;
  background: #90cdf4;
  color: #222;
  border: 2.5px solid #222;
  border-radius: 12px;
  font-size: 1.15rem;
  font-family: inherit;
  font-weight: bold;
  padding: 7px 0;
  margin-top: 0;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 0 #63b3ed;
}
.release-btn:hover, .cancel-btn:hover {
  background: #63b3ed;
}
</style> 