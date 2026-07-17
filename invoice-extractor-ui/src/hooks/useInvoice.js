import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadInvoice, extractInvoice } from '../api/invoiceApi'

export const useInvoice = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleProcessInvoice = async (file) => {
    if (!file) {
      setError('Please select a PDF file to upload.')
      return
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const uploadResponse = await uploadInvoice(file)

      if (!uploadResponse.success) {
        throw new Error(uploadResponse.error?.message || 'Upload failed')
      }

      const fileId = uploadResponse.data.file_id
      const extractResponse = await extractInvoice(fileId)

      if (!extractResponse.success) {
        throw new Error(extractResponse.error?.message || 'Extraction failed')
      }

      navigate('/results', { state: { result: extractResponse.data } })
    } catch (err) {
      const apiError = err.response?.data?.error
      const message =
        apiError?.message ||
        err.response?.data?.detail ||
        err.message ||
        'Failed to process invoice. Please try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    handleProcessInvoice,
    clearError: () => setError(null),
  }
}
