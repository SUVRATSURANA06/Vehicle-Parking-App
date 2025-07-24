<template>
  <div class="admin-users-mockup">
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
    <!-- Registered Users Section -->
    <div class="users-section">
      <div class="users-title">Registered Users</div>
      <div class="users-table-wrapper">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>E_Mail</th>
              <th>Full name</th>
              <th>Address</th>
              <th>Pin code</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.full_name }}</td>
              <td>{{ user.address || 'N/A' }}</td>
              <td>{{ user.pin_code || 'N/A' }}</td>
              <td>
                <span :style="{ color: user.is_active ? 'green' : 'red', fontWeight: 'bold' }">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button
                  :class="user.is_active ? 'btn btn-danger btn-sm' : 'btn btn-success btn-sm'"
                  @click="toggleUserStatus(user)"
                >
                  {{ user.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="7" class="users-empty">etc., users....</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'

export default {
  name: 'AdminUsers',
  setup() {
    const users = ref([])
    const logout = async () => {
      window.location.href = '/login'
    }
    const loadUsers = async () => {
      try {
        const response = await adminAPI.getUsers()
        users.value = response.data || []
      } catch (error) {
        users.value = []
      }
    }
    const toggleUserStatus = async (user) => {
      try {
        await adminAPI.toggleUserStatus(user.id)
        await loadUsers()
      } catch (error) {
        alert('Failed to update user status.')
      }
    }
    onMounted(() => {
      loadUsers()
    })
    return { users, logout, toggleUserStatus }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.admin-users-mockup {
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
.users-section {
  margin: 0 auto;
  max-width: 900px;
  padding: 0 18px;
}
.users-title {
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
.users-table-wrapper {
  border: 2.5px solid #1976d2;
  border-radius: 24px;
  background: #f8faff;
  padding: 18px 18px 12px 18px;
  margin-bottom: 12px;
  font-family: inherit;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.users-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 1.1rem;
  font-family: inherit;
}
.users-table th, .users-table td {
  border-bottom: 1.5px solid #1976d2;
  padding: 10px 14px;
  text-align: left;
}
.users-table th {
  color: #1976d2;
  font-weight: bold;
  font-size: 1.1rem;
  background: #e3f2fd;
}
.users-table td {
  color: #222;
  font-size: 1.08rem;
}
.users-empty {
  color: #e53935;
  font-style: italic;
  text-align: left;
  font-size: 1.1rem;
}
</style> 