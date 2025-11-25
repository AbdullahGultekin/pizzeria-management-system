import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Skip auth token for public endpoints
    if (config.url && !config.url.includes('/public') && !config.url.includes('/addresses') && !config.url.includes('/settings')) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },
  getMe: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

// Customer API
export const customerAPI = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await api.get('/customers', { params })
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/customers/${id}`)
    return response.data
  },
  getByPhone: async (phone: string) => {
    try {
      const response = await api.get(`/customers/phone/${phone}`)
      return response.data
    } catch (err: any) {
      // If 404, return null instead of throwing
      if (err.response?.status === 404) {
        return null
      }
      throw err
    }
  },
  create: async (data: any) => {
    const response = await api.post('/customers', data)
    return response.data
  },
  update: async (id: number, data: any) => {
    const response = await api.put(`/customers/${id}`, data)
    return response.data
  },
  // Public customer endpoints
  register: async (data: {
    email: string
    password: string
    telefoon: string
    naam: string
    straat?: string
    huisnummer?: string
    plaats?: string
  }) => {
    const response = await axios.post(`${API_BASE_URL}/customers/public/register`, data, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
  login: async (email: string, password: string) => {
    const response = await axios.post(
      `${API_BASE_URL}/customers/public/login`,
      { email, password },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  },
  getMe: async () => {
    const token = localStorage.getItem('customer_token')
    if (!token) {
      throw new Error('Niet ingelogd')
    }
    const response = await axios.get(`${API_BASE_URL}/customers/public/me`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  },
  verifyEmail: async (token: string) => {
    const response = await axios.get(
      `${API_BASE_URL}/customers/public/verify-email?token=${token}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  },
  resendVerification: async (email: string) => {
    const response = await axios.post(
      `${API_BASE_URL}/customers/public/resend-verification`,
      { email },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    return response.data
  },
}

// Order API
export const orderAPI = {
  getAll: async (params?: { skip?: number; limit?: number; customer_id?: number }) => {
    const response = await api.get('/orders', { params })
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },
  getByBonnummerPublic: async (bonnummer: string) => {
    // Public endpoint without authentication
    const response = await axios.get(`${API_BASE_URL}/orders/public/${bonnummer}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
  trackOrder: async (bonnummer: string, phone: string) => {
    // Track order by bonnummer with REQUIRED phone verification for security
    if (!phone || !phone.trim()) {
      throw new Error('Telefoonnummer is verplicht om je bestelling te volgen')
    }
    const response = await axios.get(`${API_BASE_URL}/orders/track/${bonnummer}`, {
      params: { phone: phone.trim() },
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
  trackOrdersByPhone: async (phone: string) => {
    // Get all orders for a phone number
    const response = await axios.get(`${API_BASE_URL}/orders/track/by-phone`, {
      params: { phone },
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
  create: async (data: any) => {
    const response = await api.post('/orders', data)
    return response.data
  },
  createPublic: async (data: any) => {
    // Public endpoint without authentication
    const response = await axios.post(`${API_BASE_URL}/orders/public`, data, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
  update: async (id: number, data: any) => {
    const response = await api.put(`/orders/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    await api.delete(`/orders/${id}`)
  },
  deleteMultiple: async (orderIds?: number[]) => {
    const response = await api.post('/orders/delete-multiple', orderIds || [])
    return response.data
  },
  renumberReceipts: async () => {
    const response = await api.post('/orders/renumber')
    return response.data
  },
}

// Menu API
export const menuAPI = {
  getMenu: async (includeUnavailable: boolean = false) => {
    const response = await api.get('/menu', { params: { include_unavailable: includeUnavailable } })
    return response.data
  },
  getPublicMenu: async () => {
    // Public endpoint without authentication
    // Create a request without auth token by temporarily removing the interceptor
    try {
      // Use api instance but create a config without auth
      const config = {
        headers: {
          'Content-Type': 'application/json',
        },
      }
      // Remove Authorization header if present
      const response = await api.get('/menu/public', config)
      return response.data
    } catch (error: any) {
      console.error('Error fetching public menu:', error)
      if (error.response) {
        console.error('Response status:', error.response.status)
        console.error('Response data:', error.response.data)
      }
      throw error
    }
  },
  getItems: async (categorie?: string) => {
    const response = await api.get('/menu/items', { params: { categorie } })
    return response.data
  },
  getItemById: async (id: number) => {
    const response = await api.get(`/menu/items/${id}`)
    return response.data
  },
  getCategories: async () => {
    const response = await api.get('/menu/categories')
    return response.data
  },
  createItem: async (data: any) => {
    const response = await api.post('/menu/items', data)
    return response.data
  },
  updateItem: async (id: number, data: any) => {
    const response = await api.put(`/menu/items/${id}`, data)
    return response.data
  },
  deleteItem: async (id: number) => {
    await api.delete(`/menu/items/${id}`)
  },
  createCategory: async (data: any) => {
    const response = await api.post('/menu/categories', data)
    return response.data
  },
}

// Extras API
export const extrasAPI = {
  getExtras: async () => {
    const response = await api.get('/extras')
    return response.data
  },
  getPublicExtras: async () => {
    // Public endpoint without authentication
    const response = await axios.get(`${API_BASE_URL}/extras/public`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
}

// Reports API
export const reportsAPI = {
  getDailyReport: async (date: string) => {
    const response = await api.get('/reports/daily', { params: { report_date: date } })
    return response.data
  },
  getMonthlyReport: async (year: number, month: number) => {
    const response = await api.get('/reports/monthly', { params: { year, month } })
    return response.data
  },
  getZReport: async (date: string) => {
    const response = await api.get('/reports/z-report', { params: { report_date: date } })
    return response.data
  },
}

// Printer API
export const printerAPI = {
  getInfo: async () => {
    const response = await api.get('/printer/info')
    return response.data
  },
  printOrder: async (orderId: number, customFooter?: string) => {
    const response = await api.post('/printer/print', { order_id: orderId, custom_footer: customFooter })
    return response.data
  },
  getPendingJobs: async () => {
    const response = await api.get('/printer/jobs/pending')
    return response.data
  },
  completeJob: async (jobId: string) => {
    const response = await api.post(`/printer/jobs/${jobId}/complete`)
    return response.data
  },
  configure: async (printerName: string) => {
    const response = await api.post('/printer/configure', { printer_name: printerName })
    return response.data
  },
}

// Payments API (Stripe)
export const paymentsAPI = {
  create: async (orderId: number, amount: number) => {
    const response = await axios.post(`${API_BASE_URL}/payments/create`, {
      order_id: orderId,
      amount,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data as { client_secret: string; payment_intent_id: string }
  },
}

// Contact API
export const contactAPI = {
  submit: async (data: {
    naam: string
    email: string
    telefoon?: string
    bericht: string
  }) => {
    const response = await api.post('/contact', data)
    return response.data
  },
}

// Settings API
export const settingsAPI = {
  getCustomerInfo: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/settings/customer-info`, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      return response.data
    } catch (error: any) {
      console.error('Error fetching customer info:', error)
      // Return default message on error
      return {
        message: "Beste klanten,\n\nLevertijd in het weekend kan oplopen tot 75 minuten.\n\nMet vriendelijke groeten,\nPita Pizza Napoli"
      }
    }
  },
  getDeliveryZones: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/settings/delivery-zones`, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      return response.data
    } catch (error: any) {
      console.error('Error fetching delivery zones:', error)
      return {}
    }
  },
}

// Address API
export const addressAPI = {
  getStreets: async () => {
    const response = await api.get('/addresses/streets')
    return response.data.streets || []
  },
  lookupAddress: async (straat: string) => {
    const response = await api.get('/addresses/lookup', { params: { straat } })
    return response.data
  },
  getSuggestions: async (straat?: string) => {
    const params = straat ? { straat } : {}
    const response = await api.get('/addresses/suggestions', { params })
    return response.data.suggestions || []
  },
  getPostcodes: async () => {
    const response = await api.get('/addresses/postcodes')
    // Backend returns { "postcodes": [...] }
    return response.data.postcodes || []
  },
  addStreet: async (straat: string) => {
    // Public endpoint without authentication
    const response = await axios.post(`${API_BASE_URL}/addresses/streets`, null, {
      params: { straat },
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },
}

