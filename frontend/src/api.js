import axios from 'axios'

// In dev, Vite proxy handles /api -> localhost:8000
// In prod, use VITE_API_URL directly
const baseURL = import.meta.env.PROD
  ? import.meta.env.VITE_API_URL
  : '/api'

const api = axios.create({ baseURL })

export const getCustomers = () => api.get('/customers/')
export const createCustomer = (data) => api.post('/customers/', data)
export const deleteCustomer = (id) => api.delete(`/customers/${id}`)
export const getUdhaar = (customerId) => api.get(`/customers/${customerId}/udhaar`)
export const addUdhaar = (data) => api.post('/customers/udhaar', data)
export const markPaid = (udhaarId) => api.put(`/customers/udhaar/${udhaarId}/pay`)

export const getInventory = () => api.get('/inventory/')
export const getLowStock = () => api.get('/inventory/low-stock')
export const createItem = (data) => api.post('/inventory/', data)
export const updateItem = (id, data) => api.put(`/inventory/${id}`, data)
export const deleteItem = (id) => api.delete(`/inventory/${id}`)

export const getSales = () => api.get('/sales/')
export const createSale = (data) => api.post('/sales/', data)
export const getExpenses = () => api.get('/sales/expenses')
export const createExpense = (data) => api.post('/sales/expenses', data)
export const deleteExpense = (id) => api.delete(`/sales/expenses/${id}`)

export const getDashboard = () => api.get('/analytics/dashboard')
export const chatAssistant = (message, language) =>
  api.post('/assistant/chat', { message, language })
