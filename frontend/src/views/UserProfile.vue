<template>
  <DashboardLayout :isAdmin="false">
    <div class="main-content d-flex flex-column align-items-center justify-content-start" style="max-width: 1000px; min-height: 80vh; margin: 0 auto;">
      <h1 class="h3 mb-4 mt-3">
        <i class="bi bi-person"></i> User Profile
      </h1>
      
      <div class="row w-100">
        <!-- Profile Form -->
        <div class="col-lg-8 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-pencil-square"></i> Edit Profile Information
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="updateProfile">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">
                      <i class="bi bi-person"></i> First Name
                    </label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="profile.first_name"
                      placeholder="Enter your first name"
                      maxlength="50"
                    >
                    <div class="form-text">Your first name as it appears on your ID</div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">
                      <i class="bi bi-person"></i> Last Name
                    </label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="profile.last_name"
                      placeholder="Enter your last name"
                      maxlength="50"
                    >
                    <div class="form-text">Your last name as it appears on your ID</div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">
                    <i class="bi bi-telephone"></i> Phone Number
                  </label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="profile.phone"
                    placeholder="Enter your phone number (e.g., +91 98765 43210)"
                    pattern="[\+]?[0-9\s\-\(\)]+"
                    title="Please enter a valid phone number"
                  >
                  <div class="form-text">Your contact number for parking notifications</div>
                </div>
                <div class="d-flex gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="loading || !hasChanges">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    {{ loading ? 'Updating...' : 'Update Profile' }}
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="resetForm" :disabled="loading || !hasChanges">
                    <i class="bi bi-arrow-clockwise me-2"></i>Reset
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <!-- Account Info -->
        <div class="col-lg-4 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">
                <i class="bi bi-info-circle"></i> Account Information
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="form-label text-muted">Username</label>
                <div class="form-control-plaintext">
                  <i class="bi bi-person-badge me-2"></i>
                  <strong>{{ userData.username }}</strong>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label text-muted">Email Address</label>
                <div class="form-control-plaintext">
                  <i class="bi bi-envelope me-2"></i>
                  <strong>{{ userData.email }}</strong>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label text-muted">Member Since</label>
                <div class="form-control-plaintext">
                  <i class="bi bi-calendar me-2"></i>
                  <strong>{{ formatDate(userData.created_at) }}</strong>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label text-muted">Last Login</label>
                <div class="form-control-plaintext">
                  <i class="bi bi-clock-history me-2"></i>
                  <strong>{{ formatDate(userData.last_login) }}</strong>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label text-muted">Account Status</label>
                <div class="form-control-plaintext">
                  <i class="bi bi-shield-check me-2"></i>
                  <span :class="userData.is_active ? 'text-success' : 'text-danger'">
                    <strong>{{ userData.is_active ? 'Active' : 'Inactive' }}</strong>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="card border-0 shadow-sm mt-4">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">
                <i class="bi bi-graph-up"></i> Quick Stats
              </h5>
            </div>
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span>Total Bookings:</span>
                <span class="badge bg-primary">{{ quickStats.totalBookings }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span>Total Spent:</span>
                <span class="badge bg-success">{{ formatINR(quickStats.totalSpent) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span>This Month:</span>
                <span class="badge bg-info">{{ quickStats.thisMonth }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" class="alert w-100" :class="messageClass" role="alert">
        <i :class="messageIcon"></i> {{ message }}
        <button type="button" class="btn-close" @click="clearMessage"></button>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { userAPI } from '@/services/api'
import DashboardLayout from '@/components/DashboardLayout.vue'

export default {
  name: 'UserProfile',
  components: { DashboardLayout },
  setup() {
    const userData = ref(JSON.parse(localStorage.getItem('userData') || '{}'))
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')
    
    const originalProfile = {
      first_name: userData.value.first_name || '',
      last_name: userData.value.last_name || '',
      phone: userData.value.phone || ''
    }
    
    const profile = reactive({
      first_name: originalProfile.first_name,
      last_name: originalProfile.last_name,
      phone: originalProfile.phone
    })

    const quickStats = ref({
      totalBookings: 0,
      totalSpent: 0,
      thisMonth: 0
    })

    const hasChanges = computed(() => {
      return profile.first_name !== originalProfile.first_name ||
             profile.last_name !== originalProfile.last_name ||
             profile.phone !== originalProfile.phone
    })

    const messageClass = computed(() => {
      return messageType.value === 'success' ? 'alert-success' : 'alert-danger'
    })

    const messageIcon = computed(() => {
      return messageType.value === 'success' ? 'bi bi-check-circle' : 'bi bi-exclamation-triangle'
    })

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      return `${day}/${month}/${year}`
    }

    const formatINR = (amount) => {
      return amount != null
        ? amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 })
        : '₹0.00'
    }

    const loadQuickStats = async () => {
      try {
        const response = await userAPI.getParkingStats()
        if (response.data) {
          quickStats.value = {
            totalBookings: response.data.total_reservations || 0,
            totalSpent: response.data.total_spent || 0,
            thisMonth: response.data.this_month || 0
          }
        }
      } catch (error) {
        console.error('Error loading quick stats:', error)
      }
    }

    const updateProfile = async () => {
      if (!hasChanges.value) return
      
      loading.value = true
      message.value = ''
      
      try {
        const response = await userAPI.updateProfile(profile)
        if (response.data.success) {
          // Fetch latest user info from backend
          const fresh = await userAPI.getProfile()
          if (fresh.data) {
            Object.assign(userData.value, fresh.data)
            localStorage.setItem('userData', JSON.stringify(userData.value))
            Object.assign(originalProfile, fresh.data)
            Object.assign(profile, fresh.data)
          }
          showMessage('Profile updated successfully!', 'success')
        } else {
          showMessage(response.data.message || 'Failed to update profile', 'error')
        }
      } catch (error) {
        console.error('Error updating profile:', error)
        showMessage(error.response?.data?.message || 'Error updating profile', 'error')
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      profile.first_name = originalProfile.first_name
      profile.last_name = originalProfile.last_name
      profile.phone = originalProfile.phone
      message.value = ''
    }

    const showMessage = (msg, type) => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        clearMessage()
      }, 5000)
    }

    const clearMessage = () => {
      message.value = ''
      messageType.value = ''
    }

    onMounted(() => {
      loadQuickStats()
    })

    return {
      userData,
      profile,
      loading,
      message,
      messageClass,
      messageIcon,
      hasChanges,
      quickStats,
      formatDate,
      formatINR,
      updateProfile,
      resetForm,
      clearMessage
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

.form-control-plaintext {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  margin: 0;
}

.form-control:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
}

.alert {
  border-radius: 8px;
  border: none;
}

.badge {
  font-size: 0.875rem;
}

.btn {
  border-radius: 6px;
}

.form-text {
  font-size: 0.875rem;
  color: #6c757d;
}
</style> 