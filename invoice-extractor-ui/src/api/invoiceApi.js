import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadInvoice = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const extractInvoice = async (fileId) => {
  const response = await apiClient.post('/extract', { file_id: fileId })
  return response.data
}

export const getCsvDownloadUrl = (csvId) => {
  return `${API_BASE_URL}/download-csv?csv_id=${csvId}`
}
