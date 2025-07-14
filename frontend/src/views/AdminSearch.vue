<template>
  <div class="admin-search-mockup">
    <div v-if="feedbackMessage" :class="['feedback-banner', feedbackType === 'error' ? 'feedback-error' : 'feedback-success']">
      {{ feedbackMessage }}
    </div>
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
    <!-- Search Bar Section -->
    <div class="search-bar-section">
      <label class="search-by-label">Search by</label>
      <select v-model="searchType" class="search-type-dropdown">
        <option value="location">Location</option>
        <option value="user_id">User ID</option>
        <option value="spot">Parking Spot</option>
      </select>
      <input v-model="searchString" class="search-input" placeholder="search string" @keyup.enter="performSearch" />
      <button class="search-btn" @click="performSearch">🔍</button>
    </div>
    <!-- Example Search Result Section -->
    <div v-if="searchType === 'location' && searchString" class="search-context-box">
      Example search parking lots @<span class="search-location">{{ searchString }}</span> location
    </div>
    <div v-else-if="searchType === 'user_id' && searchString" class="search-context-box">
      Example search parking lots for user ID <span class="search-location">{{ searchString }}</span>
    </div>
    <div v-else-if="searchType === 'spot' && searchString" class="search-context-box">
      Example search parking lots with spot <span class="search-location">{{ searchString }}</span>
    </div>
    <div v-if="searchResults.length === 0 && searchString" class="text-center text-danger mt-4" style="font-size:1.1rem; font-family:inherit;">No results found.</div>
    <div class="lots-cards">
      <div v-for="lot in searchResults" :key="lot.id" class="lot-card">
        <div class="lot-header">
          <span class="lot-name">{{ lot.name }}</span>
          <span class="lot-actions">
            <a href="#" class="edit-link" @click.prevent="editLot(lot)">Edit</a> |
            <a href="#" class="delete-link" @click.prevent="deleteLot(lot)">Delete</a>
          </span>
        </div>
        <div class="lot-occupancy">(Occupied : {{ lot.occupied_spots }}/{{ lot.number_of_spots }})</div>
        <div class="lot-spots-grid">
          <span v-for="spot in lot.parking_spots" :key="spot.id" :class="['spot-cell', spot.status === 'A' ? 'spot-available' : 'spot-occupied']">
            {{ spot.status }}
          </span>
        </div>
        <div class="lot-legend">
          <span class="legend-item"><span class="legend-box spot-available">A</span> = Available</span>
          <span class="legend-item"><span class="legend-box spot-occupied">O</span> = Occupied</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { adminAPI } from '@/services/api'

export default {
  name: 'AdminSearch',
  setup() {
    const searchType = ref('location')
    const searchString = ref('')
    const searchResults = ref([])
    const logout = () => {
      window.location.href = '/login'
    }
    const performSearch = async () => {
      if (!searchString.value) {
        searchResults.value = []
        return
      }
      let params = {}
      if (searchType.value === 'location') {
        params.location = searchString.value
      } else if (searchType.value === 'user_id') {
        params.user_id = searchString.value
      } else if (searchType.value === 'spot') {
        params.spot = searchString.value
      }
      try {
        const response = await adminAPI.getParkingLots(params)
        searchResults.value = (response.data || []).map(lot => {
          let spots = []
          if (lot.parking_spots && Array.isArray(lot.parking_spots) && lot.parking_spots.length === lot.number_of_spots) {
            spots = lot.parking_spots.map(s => ({ id: s.id, status: s.status }))
          } else {
            const occupied = lot.occupied_spots || 0
            const total = lot.number_of_spots
            spots = Array.from({ length: total }, (_, i) => ({ id: i, status: i < occupied ? 'O' : 'A' }))
          }
          return {
            ...lot,
            occupied_spots: lot.occupied_spots || (spots.filter(s => s.status === 'O').length),
            parking_spots: spots
          }
        })
      } catch (e) {
        searchResults.value = []
      }
    }
    const editLot = (lot) => {
      window.location.href = `/admin/parking-lots?edit=${lot.id}`
    }
    const feedbackMessage = ref('')
    const feedbackType = ref('') // 'success' or 'error'
    const showFeedback = (msg, type = 'success') => {
      feedbackMessage.value = msg
      feedbackType.value = type
      setTimeout(() => { feedbackMessage.value = '' }, 3000)
    }
    const deleteLot = async (lot) => {
      if (!confirm(`Are you ready to delete the parking lot "${lot.name}"?`)) return
      try {
        const response = await adminAPI.deleteParkingLot(lot.id)
        if (response.data && response.data.success) {
          alert('Parking lot deleted successfully!')
          await performSearch()
        } else {
          alert(response.data?.message || 'Error deleting lot.')
        }
      } catch (error) {
        alert(error.response?.data?.message || 'Error deleting lot.')
      }
    }
    return { searchType, searchString, searchResults, logout, performSearch, editLot, deleteLot, feedbackMessage, feedbackType }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.admin-search-mockup {
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
.search-bar-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 32px auto 18px auto;
  max-width: 600px;
  background: #fff;
  border: 2.5px solid #1976d2;
  border-radius: 18px;
  padding: 18px 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  position: relative;
}
.search-by-label {
  color: #ff9800;
  font-weight: bold;
  font-size: 1.2rem;
  font-family: inherit;
  margin-right: 6px;
}
.search-type-dropdown {
  font-family: inherit;
  font-size: 1.1rem;
  border-radius: 8px;
  border: 2px solid #1976d2;
  padding: 4px 10px;
  margin-right: 6px;
}
.search-input {
  font-family: inherit;
  font-size: 1.1rem;
  border-radius: 8px;
  border: 2px solid #1976d2;
  padding: 4px 10px;
  width: 180px;
  margin-right: 6px;
}
.search-btn {
  background: #e3f2fd;
  color: #1976d2;
  border: 2.5px solid #ff9800;
  border-radius: 10px;
  font-size: 1.1rem;
  font-family: inherit;
  font-weight: bold;
  padding: 4px 16px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}
.search-btn:hover {
  background: #bbdefb;
}
.search-dropdown-hint {
  position: absolute;
  left: 0;
  top: 54px;
  width: 100%;
  background: #fffbe7;
  border: 2px dashed #1976d2;
  border-radius: 12px;
  font-size: 1rem;
  color: #222;
  font-family: inherit;
  padding: 10px 18px;
  margin-top: 6px;
  z-index: 2;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.search-context-box {
  margin: 18px auto 18px auto;
  max-width: 700px;
  background: #e3f2fd;
  border: 2.5px solid #1976d2;
  border-radius: 18px;
  font-size: 1.3rem;
  color: #1976d2;
  font-family: inherit;
  font-weight: bold;
  text-align: center;
  padding: 12px 0;
}
.search-location {
  color: #1976d2;
  font-weight: bold;
  font-family: inherit;
}
.lots-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  justify-content: flex-start;
  margin-bottom: 32px;
  margin-left: 32px;
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
.feedback-banner {
  position: fixed;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  min-width: 320px;
  max-width: 90vw;
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-family: inherit;
  font-weight: bold;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.13);
}
.feedback-success {
  background: #e0ffe0;
  color: #388e3c;
  border: 2px solid #388e3c;
}
.feedback-error {
  background: #ffe0e0;
  color: #e53935;
  border: 2px solid #e53935;
}
</style> 