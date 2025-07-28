<template>
  <DashboardLayout :isAdmin="true">
    <div class="container-fluid">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0">
          <i class="bi bi-p-square"></i> Parking Spot Management
        </h1>
        <button class="btn btn-primary" @click="openAddSpotModal">
          <i class="bi bi-plus-circle"></i> Add Spot
        </button>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-3">
              <label class="form-label">Parking Lot</label>
              <select v-model="filters.lot_id" class="form-select" @change="loadSpots">
                <option value="">All Lots</option>
                <option v-for="lot in parkingLots" :key="lot.id" :value="lot.id">
                  {{ lot.name }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="loadSpots">
                <option value="">All Status</option>
                <option value="A">Available</option>
                <option value="O">Occupied</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">&nbsp;</label>
              <button class="btn btn-outline-secondary w-100" @click="loadSpots">
                <i class="bi bi-search"></i> Filter
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Spots Table -->
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Parking Spots</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Spot Number</th>
                  <th>Lot</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="spot in spots" :key="spot.id">
                  <td>{{ spot.spot_number }}</td>
                  <td>{{ getLotName(spot.lot_id) }}</td>
                  <td>
                    <span :class="`badge ${spot.status === 'A' ? 'bg-success' : 'bg-danger'}`">
                      {{ spot.status === 'A' ? 'Available' : 'Occupied' }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-2" @click="editSpot(spot)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning me-2" @click="overrideStatus(spot)">
                      <i class="bi bi-arrow-repeat"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteSpot(spot)" :disabled="spot.status === 'O'">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Add/Edit Spot Modal -->
      <div class="modal fade" id="spotModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-p-square"></i> {{ editingSpot ? 'Edit' : 'Add' }} Parking Spot
              </h5>
              <button type="button" class="btn-close" @click="closeSpotModal"></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="saveSpot">
                <div class="mb-3">
                  <label class="form-label">Parking Lot</label>
                  <select v-model="spotForm.lot_id" class="form-select" required>
                    <option value="">Select Lot</option>
                    <option v-for="lot in parkingLots" :key="lot.id" :value="lot.id">
                      {{ lot.name }}
                    </option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">Spot Number</label>
                  <input v-model="spotForm.spot_number" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Status</label>
                  <select v-model="spotForm.status" class="form-select">
                    <option value="A">Available</option>
                    <option value="O">Occupied</option>
                  </select>
                </div>
                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  <i class="bi bi-check-circle"></i> {{ editingSpot ? 'Update' : 'Add' }} Spot
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Override Modal -->
      <div class="modal fade" id="statusModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-arrow-repeat"></i> Override Spot Status
              </h5>
              <button type="button" class="btn-close" @click="closeStatusModal"></button>
            </div>
            <div class="modal-body">
              <p>Current Status: <strong>{{ selectedSpot?.status === 'A' ? 'Available' : 'Occupied' }}</strong></p>
              <div class="mb-3">
                <label class="form-label">New Status</label>
                <select v-model="newStatus" class="form-select">
                  <option value="A">Available</option>
                  <option value="O">Occupied</option>
                </select>
              </div>
              <button @click="confirmStatusOverride" class="btn btn-warning w-100" :disabled="loading">
                <i class="bi bi-arrow-repeat"></i> Override Status
              </button>
            </div>
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
  name: 'AdminParkingSpots',
  components: { DashboardLayout },
  setup() {
    const spots = ref([])
    const parkingLots = ref([])
    const filters = ref({ lot_id: '', status: '' })
    const loading = ref(false)
    
    // Modal state
    const editingSpot = ref(null)
    const spotForm = ref({ lot_id: '', spot_number: '', status: 'A' })
    const selectedSpot = ref(null)
    const newStatus = ref('A')

    const loadSpots = async () => {
      loading.value = true
      try {
        const response = await adminAPI.getParkingSpots(filters.value)
        spots.value = response.data
      } catch (error) {
        console.error('Error loading spots:', error)
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

    const getLotName = (lotId) => {
      const lot = parkingLots.value.find(l => l.id === lotId)
      return lot ? lot.name : 'Unknown'
    }

    const openAddSpotModal = () => {
      editingSpot.value = null
      spotForm.value = { lot_id: '', spot_number: '', status: 'A' }
      const modal = new bootstrap.Modal(document.getElementById('spotModal'))
      modal.show()
    }

    const editSpot = (spot) => {
      editingSpot.value = spot
      spotForm.value = { ...spot }
      const modal = new bootstrap.Modal(document.getElementById('spotModal'))
      modal.show()
    }

    const closeSpotModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('spotModal'))
      if (modal) modal.hide()
    }

    const saveSpot = async () => {
      loading.value = true
      try {
        if (editingSpot.value) {
          await adminAPI.updateParkingSpot(editingSpot.value.id, spotForm.value)
        } else {
          await adminAPI.addParkingSpot(spotForm.value)
        }
        closeSpotModal()
        await loadSpots()
      } catch (error) {
        console.error('Error saving spot:', error)
        alert(error.response?.data?.message || 'Error saving spot')
      } finally {
        loading.value = false
      }
    }

    const deleteSpot = async (spot) => {
      if (!confirm('Are you sure you want to delete this spot?')) return
      
      try {
        await adminAPI.deleteParkingSpot(spot.id)
        await loadSpots()
      } catch (error) {
        console.error('Error deleting spot:', error)
        alert(error.response?.data?.message || 'Error deleting spot')
      }
    }

    const overrideStatus = (spot) => {
      selectedSpot.value = spot
      newStatus.value = spot.status === 'A' ? 'O' : 'A'
      const modal = new bootstrap.Modal(document.getElementById('statusModal'))
      modal.show()
    }

    const closeStatusModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('statusModal'))
      if (modal) modal.hide()
    }

    const confirmStatusOverride = async () => {
      loading.value = true
      try {
        await adminAPI.overrideSpotStatus(selectedSpot.value.id, newStatus.value)
        closeStatusModal()
        await loadSpots()
      } catch (error) {
        console.error('Error overriding status:', error)
        alert(error.response?.data?.message || 'Error overriding status')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadParkingLots()
      loadSpots()
    })

    return {
      spots,
      parkingLots,
      filters,
      loading,
      editingSpot,
      spotForm,
      selectedSpot,
      newStatus,
      loadSpots,
      getLotName,
      openAddSpotModal,
      editSpot,
      closeSpotModal,
      saveSpot,
      deleteSpot,
      overrideStatus,
      closeStatusModal,
      confirmStatusOverride
    }
  }
}
</script> 