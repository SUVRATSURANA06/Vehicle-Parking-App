<template>
  <div class="container-fluid">
    <div class="row">
      <!-- Sidebar -->
      <div class="col-md-3 col-lg-2 px-0">
        <div class="sidebar p-3">
          <h5 class="text-white mb-4">
            <i v-if="isAdmin" class="bi bi-shield-check"></i>
            <i v-else class="bi bi-person"></i>
            {{ isAdmin ? 'Admin Panel' : 'User Panel' }}
          </h5>
          <nav class="nav flex-column">
            <template v-if="isAdmin">
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminDashboard' }" to="/admin/dashboard">
                <i class="bi bi-speedometer2"></i> Dashboard
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminParkingLots' }" to="/admin/parking-lots">
                <i class="bi bi-building"></i> Parking Lots
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminParkingSpots' }" to="/admin/parking-spots">
                <i class="bi bi-p-square"></i> Parking Spots
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminBookings' }" to="/admin/bookings">
                <i class="bi bi-calendar-check"></i> Bookings
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminUsers' }" to="/admin/users">
                <i class="bi bi-people"></i> Users
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'AdminAnalytics' }" to="/admin/analytics">
                <i class="bi bi-graph-up"></i> Analytics
              </router-link>
            </template>
            <template v-else>
              <router-link class="nav-link" :class="{ active: $route.name === 'UserDashboard' }" to="/user/dashboard">
                <i class="bi bi-speedometer2"></i> Dashboard
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'UserParkingLots' }" to="/user/parking-lots">
                <i class="bi bi-building"></i> Parking Lots
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'UserHistory' }" to="/user/history">
                <i class="bi bi-clock-history"></i> History
              </router-link>
              <router-link class="nav-link" :class="{ active: $route.name === 'UserProfile' }" to="/user/profile">
                <i class="bi bi-person"></i> Profile
              </router-link>
            </template>
          </nav>
        </div>
      </div>
      <!-- Main Content Area -->
      <div class="col-md-9 col-lg-10">
        <div class="main-content p-4">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardLayout',
  props: {
    isAdmin: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.sidebar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 76px);
  color: white;
}
.sidebar .nav-link {
  color: rgba(255, 255, 255, 0.8);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.3s ease;
}
.sidebar .nav-link:hover,
.sidebar .nav-link.active {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}
.sidebar .nav-link i {
  margin-right: 8px;
  width: 16px;
}
.main-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 76px);
}
@media (max-width: 768px) {
  .sidebar {
    min-height: auto;
    margin-bottom: 20px;
  }
  .main-content {
    min-height: auto;
  }
}
</style> 