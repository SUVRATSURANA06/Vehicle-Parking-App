<template>
  <DashboardLayout :isAdmin="false">
    <div class="container-fluid">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0">
          <i class="bi bi-building"></i> Available Parking Lots
        </h1>
        <button class="btn btn-primary" @click="loadParkingLots" :disabled="loading">
          <i class="bi bi-arrow-clockwise"></i> {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading parking lots...</p>
      </div>

      <!-- Parking Lots Grid -->
      <div v-else class="row">
        <div v-for="lot in parkingLots" :key="lot.id" class="col-lg-4 col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">{{ lot.name }}</h5>
            </div>
            <div class="card-body">
              <p class="card-text text-muted">
                <i class="bi bi-geo-alt"></i> {{ lot.address }}
              </p>
              <div class="d-flex justify-content-between align-items-center mb-3">
                <span :class="getAvailabilityBadgeClass(lot)">
                  {{ lot.available_spots }} spots available
                </span>
                <span class="text-primary fw-bold">{{ formatINR(lot.price) }}/hour</span>
              </div>
              <div class="progress mb-3" style="height: 8px;">
                <div 
                  class="progress-bar" 
                  :class="getProgressBarClass(lot)"
                  :style="{ width: `${(lot.available_spots / lot.number_of_spots) * 100}%` }"
                ></div>
              </div>
              <small class="text-muted">
                {{ lot.available_spots }} of {{ lot.number_of_spots }} spots available
              </small>
              
              <div class="mt-3">
                <button 
                  v-if="lot.available_spots > 0" 
                  class="btn btn-primary w-100"
                  @click="openBookingModal(lot)"
                  :disabled="bookingLoading"
                >
                  <i class="bi bi-p-circle"></i> Reserve Spot
                </button>
                <button 
                  v-else 
                  class="btn btn-secondary w-100" 
                  disabled
                >
                  <i class="bi bi-x-circle"></i> No Spots Available
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && parkingLots.length === 0" class="text-center py-5">
        <i class="bi bi-building" style="font-size: 4rem; color: #ccc;"></i>
        <h4 class="mt-3 text-muted">No Parking Lots Available</h4>
        <p class="text-muted">Check back later for available parking lots.</p>
        <button class="btn btn-primary" @click="loadParkingLots">
          <i class="bi bi-arrow-clockwise"></i> Try Again
        </button>
      </div>

      <!-- Booking Modal -->
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
                    <input class="form-control" :value="userId" readonly />
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
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userAPI } from '@/services/api'
import DashboardLayout from '@/components/DashboardLayout.vue'
import * as bootstrap from 'bootstrap'

// Demo/mock data for quick UI testing
const demoParkingLots = [
  {
    id: 1,
    name: 'Central Mall Parking',
    price: 30,
    address: '123 Main St, Downtown',
    pin_code: '400001',
    number_of_spots: 10,
    available_spots: 4,
    occupied_spots: 6
  },
  {
    id: 2,
    name: 'Airport Lot A',
    price: 50,
    address: 'Airport Road, Terminal 1',
    pin_code: '400099',
    number_of_spots: 20,
    available_spots: 12,
    occupied_spots: 8
  },
  {
    id: 3,
    name: 'Tech Park Basement',
    price: 25,
    address: 'IT Park, Block B',
    pin_code: '400076',
    number_of_spots: 15,
    available_spots: 0,
    occupied_spots: 15
  }
]

export default {
  name: 'ParkingLots',
  components: { DashboardLayout },
  setup() {
    const parkingLots = ref([])
    const loading = ref(false)
    const usingMock = ref(false)
    // Booking modal state
    const selectedLot = ref(null)
    const availableSpots = ref([])
    const bookingForm = ref({ spot_id: '', vehicle_number: '' })
    const bookingLoading = ref(false)
    const bookingError = ref('')
    const userId = JSON.parse(localStorage.getItem('userData') || '{}').id

    const loadParkingLots = async () => {
      loading.value = true
      try {
        const response = await userAPI.getParkingLots()
        if (response.data && response.data.length > 0) {
          parkingLots.value = response.data
          usingMock.value = false
        } else {
          parkingLots.value = demoParkingLots.map(lot => ({ ...lot }))
          usingMock.value = true
        }
      } catch (error) {
        console.error('Error loading parking lots:', error)
        parkingLots.value = demoParkingLots.map(lot => ({ ...lot }))
        usingMock.value = true
      } finally {
        loading.value = false
      }
    }

    const openBookingModal = async (lot) => {
      console.log('Opening booking modal for lot:', lot)
      selectedLot.value = lot
      bookingForm.value = { spot_id: '', vehicle_number: '' }
      bookingError.value = ''
      bookingLoading.value = false
      
      try {
        console.log('Fetching available spots for lot:', lot.id)
        const response = await userAPI.getAvailableSpots(lot.id)
        console.log('Available spots response:', response)
        availableSpots.value = response.data || []
        console.log('Available spots:', availableSpots.value)
      } catch (error) {
        console.error('Error loading available spots:', error)
        console.error('Error response:', error.response)
        availableSpots.value = []
        bookingError.value = 'Failed to load available spots'
      }
      
      // Show modal
      const modal = new bootstrap.Modal(document.getElementById('bookingModal'))
      modal.show()
    }

    const closeBookingModal = () => {
      const modalEl = document.getElementById('bookingModal')
      const modal = bootstrap.Modal.getInstance(modalEl)
      if (modal) modal.hide()
      
      // Reset form
      bookingForm.value = { spot_id: '', vehicle_number: '' }
      bookingError.value = ''
    }

    const submitBooking = async () => {
      console.log('Submit booking called with:', bookingForm.value)
      
      if (!bookingForm.value.spot_id || !bookingForm.value.vehicle_number) {
        bookingError.value = 'Please fill in all required fields'
        console.log('Form validation failed - missing fields')
        return
      }

      bookingLoading.value = true
      bookingError.value = ''
      
      try {
        console.log('Sending reservation request for lot:', selectedLot.value.id)
        console.log('Form data:', bookingForm.value)
        
        const response = await userAPI.reserveSpot(selectedLot.value.id, bookingForm.value)
        console.log('Reservation response:', response)
        
        if (response.data.success) {
          // Show success message
          const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'))
          modal.hide()
          
          // Show success alert
          alert('🎉 Parking spot reserved successfully!\n\nVehicle: ' + bookingForm.value.vehicle_number + '\nLocation: ' + selectedLot.value.name)
          
          // Update available spots for the selected lot immediately
          const lotIdx = parkingLots.value.findIndex(l => l.id === selectedLot.value.id)
          if (lotIdx !== -1 && parkingLots.value[lotIdx].available_spots > 0) {
            parkingLots.value[lotIdx].available_spots -= 1
          }
          
          // Refresh data from backend
          await loadParkingLots()
        } else {
          bookingError.value = response.data.message || 'Booking failed. Please try again.'
          console.log('Booking failed:', response.data.message)
        }
      } catch (error) {
        console.error('Booking error:', error)
        console.error('Error response:', error.response)
        bookingError.value = error.response?.data?.message || 'Booking failed. Please try again.'
      } finally {
        bookingLoading.value = false
      }
    }

    const getAvailabilityBadgeClass = (lot) => {
      const percentage = (lot.available_spots / lot.number_of_spots) * 100
      if (percentage === 0) return 'badge bg-danger'
      if (percentage < 25) return 'badge bg-warning'
      return 'badge bg-success'
    }

    const getProgressBarClass = (lot) => {
      const percentage = (lot.available_spots / lot.number_of_spots) * 100
      if (percentage === 0) return 'bg-danger'
      if (percentage < 25) return 'bg-warning'
      return 'bg-success'
    }

    // INR currency formatter
    const formatINR = (amount) => {
      return amount != null
        ? amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
        : '₹0.00'
    }

    onMounted(() => {
      loadParkingLots()
    })

    return {
      parkingLots,
      loading,
      loadParkingLots,
      // Booking modal state
      selectedLot,
      availableSpots,
      bookingForm,
      bookingLoading,
      bookingError,
      openBookingModal,
      closeBookingModal,
      submitBooking,
      getAvailabilityBadgeClass,
      getProgressBarClass,
      formatINR,
      userId
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.progress {
  border-radius: 10px;
}

.badge {
  font-size: 0.8rem;
}

.modal-content {
  border-radius: 12px;
  border: none;
}

.form-control:focus,
.form-select:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
}

.alert {
  border-radius: 8px;
  border: none;
}
</style> 