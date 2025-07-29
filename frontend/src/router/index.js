import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import UserDashboard from '@/views/UserDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import ParkingLots from '@/views/ParkingLots.vue'
import UserHistory from '@/views/UserHistory.vue'
import UserProfile from '@/views/UserProfile.vue'
import AdminUsers from '@/views/AdminUsers.vue'
import AdminAnalytics from '@/views/AdminAnalytics.vue'
import AdminParkingSpots from '@/views/AdminParkingSpots.vue'
import AdminBookings from '@/views/AdminBookings.vue'
import AdminParkingLots from '@/views/AdminParkingLots.vue'
import AdminSearch from '@/views/AdminSearch.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/user/dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, requiresUser: true } },
  { path: '/user/parking-lots', name: 'UserParkingLots', component: ParkingLots, meta: { requiresAuth: true, requiresUser: true } },
  { path: '/user/history', name: 'UserHistory', component: UserHistory, meta: { requiresAuth: true, requiresUser: true } },
  { path: '/user/profile', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true, requiresUser: true } },
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/users', name: 'AdminUsers', component: AdminUsers, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/analytics', name: 'AdminAnalytics', component: AdminAnalytics, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/parking-spots', name: 'AdminParkingSpots', component: AdminParkingSpots, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/bookings', name: 'AdminBookings', component: AdminBookings, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/parking-lots', name: 'AdminParkingLots', component: AdminParkingLots, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/search', name: 'AdminSearch', component: AdminSearch, meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards (session-based, minimal)

export default router 