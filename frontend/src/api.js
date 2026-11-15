import axios from 'axios'

// Dev:  Vite proxy rewrites /api/* → localhost:8000/*
// Prod: FastAPI serves the React build on the same origin,
//       so API routes are relative (no /api prefix needed).
const baseURL = import.meta.env.PROD ? '' : '/api'

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
