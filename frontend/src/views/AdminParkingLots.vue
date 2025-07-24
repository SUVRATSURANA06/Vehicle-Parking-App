<template>
  <DashboardLayout :isAdmin="true">
    <div
      class="main-content container-fluid d-flex flex-column align-items-center justify-content-start"
      style="max-width: 1100px; min-height: 80vh; margin: 0 auto;"
    >
      <h1 class="h3 mb-4 mt-3">
        <i class="bi bi-building"></i> Parking Lot Management
      </h1>

      <div v-if="lotDeleteError" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ lotDeleteError }}
        <button type="button" class="btn-close" @click="lotDeleteError = ''"></button>
      </div>

      <div class="card w-100 mb-4" style="max-width: 1000px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">All Parking Lots</h5>
          <button class="btn btn-primary" @click="openAddLotModal">
            <i class="bi bi-plus-circle"></i> Add Lot
          </button>
        </div>

        <div class="card-body table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Lot_ID</th>
                <th>Name</th>
                <th>Address</th>
                <th>Pin Code</th>
                <th>Total Spots</th>
                <th>Available Spots</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="lot in parkingLots"
                :key="lot?.id"
                v-if="lot"
              >
                <td>{{ lot.id }}</td>
                <td>{{ lot.name }}</td>
                <td>{{ lot.address }}</td>
                <td>{{ lot.pin_code }}</td>
                <td>{{ lot.number_of_spots }}</td>
                <td>{{ lot.available_spots }}</td>
                <td>
                  <button class="btn btn-sm btn-info me-1" @click="openEditLotModal(lot)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-danger me-1" @click="deleteLot(lot.id)">
                    <i class="bi bi-trash"></i>
                  </button>
                  <button class="btn btn-sm btn-secondary" @click="openSpotsModal(lot)">
                    <i class="bi bi-list-ul"></i> Spots
                  </button>
                </td>
              </tr>
              <tr v-if="!parkingLots || parkingLots.length === 0">
                <td colspan="7" class="text-center text-muted">No parking lots found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add Lot Modal -->
      <div class="modal fade custom-lot-modal" id="lotModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content custom-modal-content">
            <div class="custom-modal-header">
              <h5 class="custom-modal-title">
                {{ editingLot ? 'Edit Parking Lot' : 'New Parking Lot' }}
              </h5>
              <button type="button" class="btn-close" @click="closeLotModal"></button>
            </div>
            <div class="custom-modal-body">
              <form @submit.prevent="submitLot">
                <div class="mb-3">
                  <label class="custom-label">Prime Location Name :</label>
                  <input v-model="lotForm.name" class="custom-input" required />
                </div>
                <div class="mb-3">
                  <label class="custom-label">Address :</label>
                  <textarea v-model="lotForm.address" class="custom-input" rows="3" required></textarea>
                </div>
                <div class="mb-3">
                  <label class="custom-label">Pin code :</label>
                  <input v-model="lotForm.pin_code" class="custom-input" required />
                </div>
                <div class="mb-3">
                  <label class="custom-label">Price (per hour) :</label>
                  <input v-model.number="lotForm.price" type="number" min="0" class="custom-input" required />
                </div>
                <div class="mb-3">
                  <label class="custom-label">Maximum spots :</label>
                  <input v-model.number="lotForm.number_of_spots" type="number" min="1" class="custom-input" required />
                </div>
                <div style="text-align:left; margin-bottom: 10px;">
                  <span style="color: #e74c3c; font-family: 'Indie Flower', 'Comic Sans MS', cursive; font-size: 1.1rem;">
                  </span>
                </div>
                <div class="d-flex justify-content-center" style="gap: 16px;">
                  <button type="submit" class="custom-add-btn">
                    {{ editingLot ? 'Save Changes' : 'Add' }}
                  </button>
                  <button type="button" class="custom-cancel-btn" @click="closeLotModal">Cancel</button>
                </div>
              </form>
              <div v-if="lotError" class="alert alert-danger mt-3">{{ lotError }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spots Modal -->
      <div class="modal fade" id="spotsModal" tabindex="-1" v-if="selectedLot">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Spots for {{ selectedLot.name }}</h5>
              <button type="button" class="btn-close" @click="closeSpotsModal"></button>
            </div>
            <div class="modal-body">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Spot</th>
                    <th>Status</th>
                    <th>Vehicle Number</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="spot in lotSpots" :key="spot.id">
                    <td>
                      <div
                        class="spot-icon-custom"
                        :class="{'available': spot.status === 'A', 'occupied': spot.status === 'O'}"
                        @click="openSpotDetailModal(spot)"
                        title="View spot details"
                      >
                        {{ spot.status === 'A' ? 'A' : 'O' }}
                      </div>
                    </td>
                    <td>
                      <span v-if="spot.status === 'A'" class="badge bg-success">Available</span>
                      <span v-else class="badge bg-danger">Occupied</span>
                    </td>
                    <td>{{ spot.vehicle_number || '-' }}</td>
                    <td>
                      <button
                        class="btn btn-sm btn-danger"
                        @click.stop="deleteSpot(spot.id)"
                      >
                        <i class="bi bi-trash"></i> Delete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="modal-footer px-0">
                <button type="button" class="btn btn-secondary" @click="closeSpotsModal">Close</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spot Detail Modal -->
      <div v-if="showSpotDetailModal && selectedSpot" class="modal-backdrop-custom">
        <div class="modal-frame-custom">
          <div class="modal-header-custom">View/Delete Parking Spot</div>
          <div class="modal-body-custom">
            <div class="mb-2"><strong>ID :</strong> <span>{{ selectedSpot.spot_number }}</span></div>
            <div class="mb-2"><strong>Status :</strong>
              <span :style="{ color: selectedSpot.status === 'O' ? '#e53935' : '#388e3c', fontWeight: 'bold', cursor: selectedSpot.status === 'O' ? 'pointer' : 'default' }"
                @click="selectedSpot.status === 'O' && openOccupiedDetailModal()">
                {{ selectedSpot.status }}
              </span>
              <span v-if="selectedSpot.status === 'O'" style="color: #e53935; font-size: 0.95rem; margin-left: 8px;">(Click 'O' for details)</span>
            </div>
            <div class="mb-2"><strong>Vehicle Number :</strong> <span>{{ selectedSpot.vehicle_number || '-' }}</span></div>
            <div class="mb-2"><strong>Price (per hour) :</strong> <span>{{ selectedSpot.price || '-' }}</span></div>
            <div class="mb-2"><strong>Parking Cost :</strong> <span>{{ selectedSpot.parking_cost || '-' }}</span></div>
            <div class="mb-2"><strong>Parking Timestamp :</strong> <span>{{ selectedSpot.parking_timestamp || '-' }}</span></div>
            <div class="mb-2"><strong>Booking ID :</strong> <span>{{ selectedSpot.booking_id || '-' }}</span></div>
            <div class="d-flex justify-content-center mt-3" style="gap: 16px;">
              <button class="btn btn-primary" :disabled="selectedSpot.status === 'O'" @click="deleteSpot(selectedSpot.id)">Delete</button>
              <button class="btn btn-secondary" @click="closeSpotDetailModal">Close</button>
            </div>
            <div v-if="selectedSpot.status === 'O'" style="color: #e53935; font-size: 1.05rem; margin-top: 8px;">Note: Can't delete the occupied parking spot</div>
            <div v-if="spotDetailError" class="alert alert-danger mt-2">{{ spotDetailError }}</div>
          </div>
        </div>
      </div>

      <!-- Occupied Spot Details Modal -->
      <div v-if="showOccupiedDetailModal && occupiedReservation" class="modal-backdrop-custom">
        <div class="modal-frame-custom">
          <div class="modal-header-custom">Occupied Parking Spot Details</div>
          <div class="modal-body-custom">
            <div class="mb-2"><strong>ID :</strong> <span>{{ occupiedReservation.spot?.spot_number || selectedSpot.spot_number }}</span></div>
            <div class="mb-2"><strong>Customer ID :</strong> <span>{{ occupiedReservation.user_id }}</span></div>
            <div class="mb-2"><strong>Vehicle number :</strong> <span>{{ occupiedReservation.vehicle_number }}</span></div>
            <div class="mb-2"><strong>Date/time of parking :</strong> <span>{{ occupiedReservation.parking_timestamp }}</span></div>
            <div class="mb-2"><strong>Est. parking cost :</strong> <span>{{ occupiedReservation.parking_cost }}</span></div>
            <div class="d-flex justify-content-center mt-3" style="gap: 16px;">
              <button class="btn btn-info" @click="showFullOccupiedDetailModal = true">Show Full Details</button>
              <button class="btn btn-secondary" @click="closeOccupiedDetailModal">Close</button>
            </div>
          </div>
        </div>
      </div>
      <!-- Full Occupied Spot Details Modal (NEW) -->
      <div v-if="showFullOccupiedDetailModal && occupiedReservation" class="modal-backdrop-custom">
        <div class="modal-frame-custom">
          <div class="modal-header-custom">Full Occupied Spot & User Details</div>
          <div class="modal-body-custom">
            <div class="mb-2"><strong>Spot Number:</strong> <span>{{ occupiedReservation.spot?.spot_number || selectedSpot.spot_number }}</span></div>
            <div class="mb-2"><strong>User Name:</strong> <span>{{ occupiedReservation.user?.full_name || '-' }}</span></div>
            <div class="mb-2"><strong>User Email:</strong> <span>{{ occupiedReservation.user?.email || '-' }}</span></div>
            <div class="mb-2"><strong>User Phone:</strong> <span>{{ occupiedReservation.user?.phone || '-' }}</span></div>
            <div class="mb-2"><strong>Vehicle Number:</strong> <span>{{ occupiedReservation.vehicle_number || '-' }}</span></div>
            <div class="mb-2"><strong>Parking Time:</strong> <span>{{ occupiedReservation.parking_timestamp || '-' }}</span></div>
            <div class="mb-2"><strong>Estimated Cost:</strong> <span>{{ occupiedReservation.parking_cost || '-' }}</span></div>
            <div class="mb-2"><strong>Status:</strong> <span>{{ occupiedReservation.status || '-' }}</span></div>
            <div class="mb-2"><strong>Booking ID:</strong> <span>{{ occupiedReservation.id || '-' }}</span></div>
            <div class="d-flex justify-content-center mt-3">
              <button class="btn btn-secondary" @click="showFullOccupiedDetailModal = false">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { adminAPI } from '@/services/api'
import * as bootstrap from 'bootstrap'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'AdminParkingLots',
  components: { DashboardLayout },
  setup() {
    const parkingLots = ref([])
    const lotForm = ref({ name: '', address: '', pin_code: '', number_of_spots: 1, price: 0 })
    const lotError = ref('')
    const editingLot = ref(false)
    const selectedLot = ref(null)
    const lotSpots = ref([])
    const lotDeleteError = ref('')
    const route = useRoute()
    const router = useRouter()
    const selectedSpot = ref(null)
    const showSpotDetailModal = ref(false)
    const showOccupiedDetailModal = ref(false)
    const occupiedReservation = ref(null)
    const spotDetailError = ref('')
    const showFullOccupiedDetailModal = ref(false)

    const loadLots = async () => {
      try {
        const response = await adminAPI.getParkingLots()
        parkingLots.value = (response.data || []).filter(lot => lot && lot.name)
      } catch (error) {
        parkingLots.value = []
      }
    }

    const openEditLotModal = (lot) => {
      editingLot.value = true
      lotForm.value = { ...lot }
      lotError.value = ''
      const modal = new bootstrap.Modal(document.getElementById('lotModal'))
      modal.show()
    }

    const closeLotModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('lotModal'))
      if (modal) modal.hide()
    }

    const submitLot = async () => {
      lotError.value = ''
      try {
        if (editingLot.value) {
          await adminAPI.editParkingLot(lotForm.value.id, lotForm.value)
        } else {
          await adminAPI.createParkingLot(lotForm.value)
        }
        closeLotModal()
        await loadLots()
      } catch (error) {
        lotError.value = error.response?.data?.message || 'Error saving lot.'
      }
    }

    const deleteLot = async (lotId) => {
      lotDeleteError.value = ''
      // Find the lot object
      const lot = parkingLots.value.find(l => l.id === lotId)
      if (!lot) return

      // Show confirmation dialog
      if (!window.confirm('Are you sure you want to delete this parking lot?')) return

      try {
        const response = await adminAPI.deleteParkingLot(lotId)
        console.log('Delete response:', response.data)
        if (response.data.success) {
          // Remove the lot from the frontend list immediately
          parkingLots.value = parkingLots.value.filter(l => l.id !== lotId)
          showFlashMessage('Parking lot deleted successfully', 'success')
        } else {
          lotDeleteError.value = response.data.message || 'Cannot delete lot.'
        }
      } catch (error) {
        lotDeleteError.value = 'Failed to delete parking lot. Please try again.'
      }
    }

    const openAddLotModal = () => {
      editingLot.value = false
      lotForm.value = { name: '', address: '', pin_code: '', number_of_spots: 1, price: 0 }
      lotError.value = ''
      const modal = new bootstrap.Modal(document.getElementById('lotModal'))
      modal.show()
    }

    const openSpotsModal = async (lot) => {
      selectedLot.value = lot
      try {
        const response = await adminAPI.getParkingSpots({ lot_id: lot.id })
        lotSpots.value = response.data
      } catch (error) {
        lotSpots.value = []
      }
      const modal = new bootstrap.Modal(document.getElementById('spotsModal'))
      modal.show()
    }

    const closeSpotsModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('spotsModal'))
      if (modal) modal.hide()
      selectedLot.value = null
    }

    // Open spot detail modal
    const openSpotDetailModal = async (spot) => {
      selectedSpot.value = spot
      spotDetailError.value = ''
      showSpotDetailModal.value = true
      // If occupied, fetch reservation details for the occupied modal
      if (spot.status === 'O') {
        try {
          const response = await adminAPI.getBookings({ spot_id: spot.id, status: 'active' })
          occupiedReservation.value = response.data && response.data.length > 0 ? response.data[0] : null
        } catch (e) {
          occupiedReservation.value = null
        }
      } else {
        occupiedReservation.value = null
      }
    }
    const closeSpotDetailModal = () => {
      showSpotDetailModal.value = false
      selectedSpot.value = null
    }
    const openOccupiedDetailModal = () => {
      showOccupiedDetailModal.value = true
    }
    const closeOccupiedDetailModal = () => {
      showOccupiedDetailModal.value = false
    }
    // Update deleteSpot to close modal after delete
    const deleteSpot = async (spotId) => {
      if (!confirm('Are you sure you want to delete this spot?')) return
      try {
        await adminAPI.deleteParkingSpot(spotId)
        await openSpotsModal(selectedLot.value)
        closeSpotDetailModal()
      } catch (error) {}
    }

    onMounted(() => {
      loadLots()
      if (route.query.add === '1' || route.query.add === 1) {
        setTimeout(() => {
          openAddLotModal()
          router.replace({ path: '/admin/parking-lots' })
        }, 300)
      }
    })

    return {
      parkingLots,
      lotForm,
      lotError,
      editingLot,
      selectedLot,
      lotSpots,
      openEditLotModal,
      deleteLot,
      openSpotsModal,
      closeSpotsModal,
      deleteSpot,
      openAddLotModal,
      submitLot,
      closeLotModal,
      lotDeleteError,
      selectedSpot,
      showSpotDetailModal,
      showOccupiedDetailModal,
      occupiedReservation,
      spotDetailError,
      openSpotDetailModal,
      closeSpotDetailModal,
      openOccupiedDetailModal,
      closeOccupiedDetailModal,
      showFullOccupiedDetailModal
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
.modal-backdrop-custom {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.13);
  z-index: 4000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-frame-custom {
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
.modal-header-custom {
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
.modal-body-custom {
  padding: 18px 28px 0 28px;
}
/* .spot-icon-custom styles removed, now in main.css */
</style>
