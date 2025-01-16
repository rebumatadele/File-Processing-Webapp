import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'https://file-processing-webapp.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor: Attach token to every request if present
axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response Interceptor: Catch 401 errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token invalid/expired. Clear token and redirect.
      if (typeof window !== 'undefined') {
        // Remove token from localStorage
        localStorage.removeItem('access_token')
        
        // Clear the access_token cookie by setting an expired cookie
        document.cookie = 'access_token=; Max-Age=0; path=/;'

        // Redirect to the login page
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
