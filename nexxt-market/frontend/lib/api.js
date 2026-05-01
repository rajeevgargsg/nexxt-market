import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token on each request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('nexxt_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ─── Auth ──────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) =>
    api.post('/auth/token', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
}

// ─── Listings ──────────────────────────────────────────────────────────────
export const listingsAPI = {
  getFeed: (params) => api.get('/listing/feed', { params }),
  getListing: (id) => api.get(`/listing/${id}`),
  createListing: (data) => api.post('/listing/create', data),
  saveListing: (id) => api.post(`/listing/${id}/save`),
  boostListing: (id, type) => api.post('/listing/boost', null, { params: { listing_id: id, boost_type: type } }),
  getActivity: (id) => api.get(`/listing/${id}/activity`),
}

// ─── AI ────────────────────────────────────────────────────────────────────
export const aiAPI = {
  optimizeListing: (id) => api.post('/ai/optimize-listing', null, { params: { listing_id: id } }),
  getReplySuggestion: (id, role) => api.get('/ai/reply-suggestion', { params: { listing_id: id, role } }),
}

// ─── Messages ──────────────────────────────────────────────────────────────
export const messagesAPI = {
  send: (data) => api.post('/messages', data),
  getThread: (listingId) => api.get(`/messages/${listingId}`),
}

// ─── Recommendations ───────────────────────────────────────────────────────
export const recAPI = {
  get: () => api.get('/recommendations'),
}

// ─── Notifications ─────────────────────────────────────────────────────────
export const notifAPI = {
  get: () => api.get('/notifications'),
}

export default api
