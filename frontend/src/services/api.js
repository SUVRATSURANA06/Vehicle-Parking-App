import axios from 'axios'


const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Important: allow cookies to be sent
})


// Auth API
export const authAPI = {
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/register', userData),
  logout: () => api.get('/logout'),
  checkAuth: () => api.get('/check-auth'),
  createAdmin: () => api.post('/create-admin', {})
}

// User
export const userAPI = {
  getDashboard: () => api.get('/user/dashboard'),
  getParkingLots: () => api.get('/user/parking-lots'),
  getAvailableSpots: (lotId) => api.get(`/user/available-spots/${lotId}`),
  reserveSpot: (lotId, data) => api.post(`/user/reserve/${lotId}`, data),
  endSession: () => api.post('/user/end-session'),
  getHistory: (page = 1) => api.get(`/user/history?page=${page}`),
  exportCSV: () => api.post('/user/export-csv'),
  exportStatus: (taskId) => api.get(`/user/export-status/${taskId}`),
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.post('/user/profile/edit', data),
  getActiveReservation: () => api.get('/user/api/active-reservation'),
  getParkingStats: () => api.get('/user/api/parking-stats'),
  parkedIn: (reservationId) => api.post(`/user/parked-in/${reservationId}`),
  releaseReservation: (reservationId) => api.post(`/user/release/${reservationId}`)
}

// Admin
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getStats: () => api.get('/admin/api/stats'),
  getParkingLots: (filters = {}) => {
    const params = new URLSearchParams(filters)
    return api.get(`/admin/parking-lots?${params}`)
  },
  createParkingLot: (data) => api.post('/admin/parking-lots/create', data),
  updateParkingLot: (id, data) => api.post(`/admin/parking-lots/${id}/edit`, data),
  deleteParkingLot: (id) => api.post(`/admin/parking-lots/${id}/delete`, {}),
  getUsers: () => api.get('/admin/users'),
  toggleUserStatus: (userId) => api.post(`/admin/users/${userId}/toggle-status`, {}),
  getAnalytics: () => api.get('/admin/analytics'),
  generateMonthlyReport: () => api.post('/admin/reports/generate-monthly', {}),
  getReportStatus: (taskId) => api.get(`/admin/reports/status/${taskId}`),
  downloadReport: (filename) => api.get(`/admin/reports/download/${filename}`),
  listReports: () => api.get('/admin/reports/list'),
  // Parking Spot Management
  getParkingSpots: (filters = {}) => {
    const params = new URLSearchParams(filters)
    return api.get(`/admin/parking-spots?${params}`)
  },
  addParkingSpot: (data) => api.post('/admin/parking-spots/add', data),
  editParkingSpot: (spotId, data) => api.post(`/admin/parking-spots/${spotId}/edit`, data),
  deleteParkingSpot: (spotId) => api.post(`/admin/parking-spots/${spotId}/delete`, {}),
  overrideSpotStatus: (spotId, status) => api.post(`/admin/parking-spots/${spotId}/override-status`, { status }),
  // Booking Management
  getBookings: (filters = {}) => {
    const params = new URLSearchParams(filters)
    return api.get(`/admin/bookings?${params}`)
  },
  cancelBooking: (bookingId) => api.post(`/admin/bookings/${bookingId}/cancel`, {}),
  getSpotReservation: (spotId) => api.get(`/admin/spot/${spotId}/reservation`)
}

export default api 