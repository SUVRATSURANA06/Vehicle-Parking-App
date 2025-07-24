<template>
  <div>
    <!-- Flash Messages -->
    <div v-if="flashMessage" class="container mt-3">
      <div :class="`alert alert-${flashMessage.type} alert-dismissible fade show`" role="alert">
        {{ flashMessage.message }}
        <button type="button" class="btn-close" @click="clearFlashMessage"></button>
      </div>
    </div>
    <!-- Main Content -->
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const userData = ref(null)
    const flashMessage = ref(null)

    const logout = async () => {
      try {
        await authAPI.logout()
        userData.value = null
        router.push('/login')
        showFlashMessage('Logged out successfully', 'success')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    const showFlashMessage = (message, type = 'info') => {
      flashMessage.value = { message, type }
      setTimeout(() => {
        clearFlashMessage()
      }, 5000)
    }

    const clearFlashMessage = () => {
      flashMessage.value = null
    }

    // On mount, check session-based auth
    const checkAuth = async () => {
      try {
        const response = await authAPI.checkAuth()
        if (response.data.authenticated) {
          userData.value = response.data.user
        } else {
          userData.value = null
        }
      } catch (error) {
        userData.value = null
      }
    }

    onMounted(() => {
      checkAuth()
    })

    return {
      userData,
      flashMessage,
      logout,
      showFlashMessage,
      clearFlashMessage
    }
  }
}
</script>

<style>
/* Global styles */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
}

.navbar-brand {
  font-weight: bold;
  color: #2c3e50 !important;
}

.navbar-brand i {
  color: #3498db;
  margin-right: 8px;
}

.alert {
  border-radius: 8px;
  border: none;
}

.btn-close {
  opacity: 0.7;
}

.btn-close:hover {
  opacity: 1;
}
</style>
