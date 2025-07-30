<template>
  <div class="admin-dashboard-mockup">
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

    <!-- Parking Lots Section -->
    <div class="lots-section">
      <div class="lots-title">Parking Lots</div>
      <div class="lots-cards">
        <div v-for="lot in parkingLots" :key="lot.id" class="lot-card">
          <div class="lot-header">
            <span class="lot-name">{{ lot.name }}</span>
            <span class="lot-actions">
              <a href="#" class="edit-link" @click.prevent="openEditLotModal(lot)">Edit</a> |
              <a href="#" class="delete-link" @click.prevent="deleteLot(lot)">Delete</a>
            </span>
          </div>
          <div class="lot-occupancy">(Occupied : {{ lot.occupied_spots }}/{{ lot.number_of_spots }})</div>
          <div class="lot-spots-grid">
            <span
              v-for="spot in lot.parking_spots"
              :key="spot.id"
              class="spot-icon-custom"
              :class="{ available: spot.status === 'A', occupied: spot.status === 'O' }"
              @click="openSpotDetailModal(spot, lot)"
              title="View spot details"
              style="display:inline-flex;margin:4px;vertical-align:middle;cursor:pointer;"
            >
              {{ spot.status === 'A' ? 'A' : 'O' }}
            </span>
          </div>
          <div class="lot-legend">
            <span class="legend-item"><span class="legend-box spot-available">A</span> = Available</span>
            <span class="legend-item"><span class="legend-box spot-occupied">O</span> = Occupied</span>
          </div>
        </div>
      </div>
      <div class="add-lot-btn-row">
        <button class="add-lot-btn" @click="addLot">+ Add Lot</button>
      </div>
    </div>

    <!-- Edit Parking Lot Modal -->
    <div v-if="showEditModal" class="edit-lot-modal-backdrop">
      <div class="edit-lot-modal-frame">
        <div class="edit-lot-modal-header">Edit Parking Lot</div>
        <div class="edit-lot-modal-body">
          <form @submit.prevent="submitEditLot">
            <div class="edit-lot-row">
              <label>Prime Location Name :</label>
              <input v-model="editLotForm.name" required />
            </div>
            <div class="edit-lot-row">
              <label>Address :</label>
              <textarea v-model="editLotForm.address" rows="3" required></textarea>
            </div>
            <div class="edit-lot-row">
              <label>Pin code :</label>
              <input v-model="editLotForm.pin_code" required />
            </div>
            <div class="edit-lot-row">
              <label>Price(per hour) :</label>
              <input v-model.number="editLotForm.price" type="number" min="0" required />
            </div>
            <div class="edit-lot-row">
              <label>Maximum spots :</label>
              <input v-model.number="editLotForm.number_of_spots" type="number" min="1" required />
            </div>
            <div class="edit-lot-etc"></div>
            <div class="edit-lot-modal-footer">
              <button type="submit" class="edit-lot-update-btn">Update</button>
              <button type="button" class="edit-lot-cancel-btn" @click="closeEditLotModal">Cancel</button>
            </div>
            <div v-if="editLotError" class="edit-lot-error">{{ editLotError }}</div>
          </form>
        </div>
      </div>
    </div>

    <!-- Spot Detail Modal -->
    <div v-if="showSpotDetailModal && selectedSpot" class="modal-backdrop-custom">
      <div class="modal-frame-custom">
        <div class="modal-header-custom" :style="selectedSpot.status === 'O' ? 'background: #ffe082; font-family: Indie Flower, Comic Sans MS, cursive; font-size: 1.35rem;' : ''">
          {{ selectedSpot.status === 'O' ? 'Occupied Parking Spot Details' : 'Parking Spot Details' }}
        </div>
        <div class="modal-body-custom">
          <template v-if="selectedSpot.status === 'O' && occupiedReservation">
            <div class="mb-2"><strong>Spot ID :</strong> <span class="modal-field">{{ selectedSpot.id }}</span></div>
            <div class="mb-2"><strong>Spot Number :</strong> <span class="modal-field">{{ selectedSpot.spot_number || 'N/A' }}</span></div>
            <div class="mb-2"><strong>Reservation ID :</strong> <span class="modal-field">{{ occupiedReservation.id }}</span></div>
            <div class="mb-2"><strong>Customer ID :</strong> <span class="modal-field">{{ occupiedReservation.user_id }}</span></div>
            <div class="mb-2"><strong>Customer Name :</strong> <span class="modal-field">{{ occupiedReservation.user?.full_name || 'N/A' }}</span></div>
            <div class="mb-2"><strong>Customer Email :</strong> <span class="modal-field">{{ occupiedReservation.user?.email || 'N/A' }}</span></div>
            <div class="mb-2"><strong>Vehicle number :</strong> <span class="modal-field">{{ occupiedReservation.vehicle_number || 'N/A' }}</span></div>
            <div class="mb-2"><strong>Date/time of parking :</strong> <span class="modal-field">{{ formatDateTime(occupiedReservation.parking_timestamp) }}</span></div>
            <div class="mb-2"><strong>Est. parking cost :</strong> <span class="modal-field">₹{{ occupiedReservation.parking_cost || 0 }}</span></div>
            <div class="mb-2"><strong>Status :</strong> <span class="modal-field">{{ occupiedReservation.status }}</span></div>
            <div class="d-flex justify-content-center mt-3">
              <button class="btn btn-secondary" @click="closeSpotDetailModal">Close</button>
            </div>
          </template>
          <template v-else>
            <div class="mb-2"><strong>Spot ID :</strong> <span class="modal-field">{{ selectedSpot.id }}</span></div>
            <div class="mb-2"><strong>Spot Number :</strong> <span class="modal-field">{{ selectedSpot.spot_number || 'N/A' }}</span></div>
            <div class="mb-2"><strong>Status :</strong>
              <span :style="{ color: selectedSpot.status === 'O' ? '#e53935' : '#388e3c', fontWeight: 'bold' }">
                {{ selectedSpot.status === 'A' ? 'Available' : 'Occupied' }}
              </span>
            </div>
            <div class="d-flex justify-content-center mt-3">
              <button class="btn btn-secondary" @click="closeSpotDetailModal">Close</button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminAPI } from '@/services/api'

export default {
  name: 'AdminDashboard',
  setup() {
    const parkingLots = ref([])
    const router = useRouter()
    const logout = async () => {
      // Implement logout logic or use global
      window.location.href = '/login'
    }
    const loadLots = async () => {
      try {
        const response = await adminAPI.getParkingLots()
        console.log('Parking lots response:', response.data)
        // If backend provides real spot status, use it. Otherwise, simulate based on occupied_spots/number_of_spots
        parkingLots.value = (response.data || []).map(lot => {
          let spots = []
          if (lot.parking_spots && Array.isArray(lot.parking_spots) && lot.parking_spots.length === lot.number_of_spots) {
            // Use real spot status from backend
            spots = lot.parking_spots.map(s => ({ 
              id: s.id, 
              status: s.status, 
              spot_number: s.spot_number 
            }))
            console.log(`Lot ${lot.name} spots:`, spots)
          } else {
            // Simulate: first N = 'O', rest = 'A'
            const occupied = lot.occupied_spots || 0
            const total = lot.number_of_spots
            spots = Array.from({ length: total }, (_, i) => ({ 
              id: i, 
              status: i < occupied ? 'O' : 'A',
              spot_number: `${lot.name}-${String(i+1).padStart(3, '0')}`
            }))
          }
          return {
            ...lot,
            occupied_spots: lot.occupied_spots || (spots.filter(s => s.status === 'O').length),
            parking_spots: spots
          }
        })
        console.log('Processed parking lots:', parkingLots.value)
      } catch (e) {
        console.error('Error loading lots:', e)
        parkingLots.value = []
      }
    }
    const editLot = (lot) => {
      // Navigate or open modal for editing
      window.location.href = `/admin/parking-lots?edit=${lot.id}`
    }
    const deleteLot = async (lot) => {
      if (!confirm(`Are you ready to delete the parking lot "${lot.name}"?`)) return
      try {
        const response = await adminAPI.deleteParkingLot(lot.id)
        console.log('Delete response:', response.data)
        if (response.data.success) {
          // Remove the lot from the frontend list immediately
          parkingLots.value = parkingLots.value.filter(l => l.id !== lot.id)
        } else {
          alert(response.data.message || 'Error deleting lot.')
        }
      } catch (error) {
        alert(error.response?.data?.message || 'Error deleting lot.')
      }
    }
    const addLot = () => {
      router.push({ path: '/admin/parking-lots', query: { add: 1 } })
    }
    onMounted(() => {
      loadLots()
    })

    // Edit Lot Modal State
    const showEditModal = ref(false)
    const editLotForm = ref({ name: '', address: '', pin_code: '', price: 0, number_of_spots: 1 })
    const editLotId = ref(null)
    const editLotError = ref('')
    const openEditLotModal = (lot) => {
      showEditModal.value = true
      editLotId.value = lot.id
      editLotForm.value = { name: lot.name, address: lot.address, pin_code: lot.pin_code, price: lot.price, number_of_spots: lot.number_of_spots }
      editLotError.value = ''
    }
    const closeEditLotModal = () => {
      showEditModal.value = false
      editLotId.value = null
      editLotError.value = ''
    }
    const submitEditLot = async () => {
      editLotError.value = ''
      try {
        await adminAPI.updateParkingLot(editLotId.value, editLotForm.value)
        await loadLots() // Ensure data is refreshed before closing modal
        closeEditLotModal()
      } catch (error) {
        editLotError.value = error.response?.data?.message || 'Error updating lot.'
      }
    }

    // Spot Detail Modal State
    const showSpotDetailModal = ref(false)
    const selectedSpot = ref(null)
    const occupiedReservation = ref(null)
    const openSpotDetailModal = async (spot, lot) => {
      console.log('Opening spot detail modal for spot:', spot)
      console.log('Spot ID:', spot.id)
      console.log('Spot status:', spot.status)
      console.log('Lot:', lot)
      
      selectedSpot.value = spot
      showSpotDetailModal.value = true
      if (spot.status === 'O') {
        try {
          // Use the new specific endpoint for spot reservations
          console.log('Fetching reservation for spot_id:', spot.id)
          const response = await adminAPI.getSpotReservation(spot.id)
          console.log('Spot reservation response:', response.data)
          
          if (response.data.success && response.data.reservation) {
            occupiedReservation.value = response.data.reservation
            console.log('Found reservation:', occupiedReservation.value)
          } else {
            console.log('No reservation found for spot:', spot.id)
            occupiedReservation.value = null
          }
        } catch (e) {
          console.error('Error fetching spot details:', e)
          occupiedReservation.value = null
        }
      } else {
        occupiedReservation.value = null
      }
    }
    const closeSpotDetailModal = () => {
      showSpotDetailModal.value = false
      selectedSpot.value = null
      occupiedReservation.value = null
    }

    // Add a date formatter for the modal
    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${day}/${month}/${year} ${hours}:${minutes}`
    }

    return { parkingLots, logout, editLot, deleteLot, addLot, showEditModal, editLotForm, openEditLotModal, closeEditLotModal, submitEditLot, editLotError, showSpotDetailModal, selectedSpot, openSpotDetailModal, closeSpotDetailModal, occupiedReservation, formatDateTime }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.admin-dashboard-mockup {
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
.lots-section {
  margin: 0 auto;
  max-width: 1100px;
  padding: 0 18px;
}
.lots-title {
  font-size: 2rem;
  color: #1976d2;
  font-family: inherit;
  font-weight: bold;
  text-align: center;
  margin-bottom: 18px;
  border-bottom: 3px solid #1976d2;
  border-radius: 12px;
  padding-bottom: 6px;
}
.lots-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  justify-content: flex-start;
  margin-bottom: 32px;
}
.lot-card {
  border: 2.5px solid #1976d2;
  border-radius: 24px;
  background: #f8faff;
  min-width: 220px;
  max-width: 260px;
  padding: 18px 18px 12px 18px;
  margin-bottom: 12px;
  font-family: inherit;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.15rem;
  margin-bottom: 4px;
}
.lot-name {
  font-weight: bold;
  color: #222;
}
.lot-actions {
  font-size: 1rem;
}
.edit-link {
  color: #ff9800;
  font-weight: bold;
  cursor: pointer;
}
.delete-link {
  color: #e53935;
  font-weight: bold;
  cursor: pointer;
}
.lot-occupancy {
  color: #388e3c;
  font-size: 1.05rem;
  margin-bottom: 8px;
  font-weight: bold;
}
.lot-spots-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 4px;
  min-height: 48px;
}
.spot-cell {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-family: inherit;
  font-weight: bold;
  border: 2px solid #1976d2;
}
.spot-available {
  background: #e0ffe0;
  color: #1976d2;
}
.spot-occupied {
  background: #ffe0e0;
  color: #e53935;
}
.more-spots {
  font-size: 1.2rem;
  color: #1976d2;
  margin-left: 6px;
}
.add-lot-btn-row {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
.add-lot-btn {
  background: #e3f2fd;
  color: #1976d2;
  border: 2.5px solid #ff9800;
  border-radius: 18px;
  font-size: 1.3rem;
  font-family: inherit;
  font-weight: bold;
  padding: 12px 38px;
  box-shadow: 0 2px 0 #ff9800;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}
.add-lot-btn:hover {
  background: #bbdefb;
  box-shadow: 0 4px 0 #ff9800;
}
.lot-legend {
  display: flex;
  gap: 18px;
  margin-top: 6px;
  font-size: 1rem;
  font-family: inherit;
  align-items: center;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.legend-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  border: 2px solid #1976d2;
  margin-right: 3px;
}

.edit-lot-modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.13);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.edit-lot-modal-frame {
  background: #fffbe7;
  border: 3px solid #222;
  border-radius: 28px;
  min-width: 340px;
  max-width: 480px;
  width: 100%;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 0 0 18px 0;
  position: relative;
}
.edit-lot-modal-header {
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
.edit-lot-modal-body {
  padding: 18px 28px 0 28px;
}
.edit-lot-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.edit-lot-row label {
  flex: 1.2;
  font-size: 1.1rem;
  color: #222;
  font-family: inherit;
  font-weight: 500;
}
.edit-lot-row input, .edit-lot-row textarea {
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
.edit-lot-row textarea {
  min-height: 60px;
  resize: vertical;
}
.edit-lot-etc {
  color: #e53935;
  font-size: 1.1rem;
  font-family: inherit;
  font-style: italic;
  margin-left: 8px;
  margin-bottom: 8px;
}
.edit-lot-modal-footer {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 18px;
}
.edit-lot-update-btn, .edit-lot-cancel-btn {
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
.edit-lot-update-btn:hover, .edit-lot-cancel-btn:hover {
  background: #63b3ed;
}
.edit-lot-cancel-btn {
  background: #fff;
  color: #222;
  border: 2.5px solid #90cdf4;
  box-shadow: 0 2px 0 #90cdf4;
}
.edit-lot-error {
  color: #e53935;
  font-size: 1rem;
  font-family: inherit;
  margin-top: 8px;
  text-align: center;
}

.modal-backdrop-custom {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.13);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-frame-custom {
  background: #fffbe7;
  border: 3px solid #222;
  border-radius: 28px;
  min-width: 340px;
  max-width: 480px;
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
.mb-2 {
  margin-bottom: 12px;
}
.d-flex {
  display: flex;
}
.justify-content-center {
  justify-content: center;
}
.mt-3 {
  margin-top: 18px;
}
.btn {
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
.btn:hover {
  background: #63b3ed;
}
.btn-secondary {
  background: #fff;
  color: #222;
  border: 2.5px solid #90cdf4;
  box-shadow: 0 2px 0 #90cdf4;
}
.modal-field {
  display: inline-block;
  min-width: 80px;
  padding: 4px 18px;
  border: 2px solid #222;
  border-radius: 10px;
  background: #fff;
  color: #e67e22;
  font-family: 'Indie Flower', 'Comic Sans MS', cursive;
  font-size: 1.1rem;
  margin-left: 8px;
  margin-bottom: 2px;
  text-align: center;
}
</style> 