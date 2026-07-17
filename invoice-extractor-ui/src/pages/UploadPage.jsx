import { useState } from 'react'
import FileUpload from '../components/FileUpload'
import Header from '../components/Header'
import Loader from '../components/Loader'
import { useInvoice } from '../hooks/useInvoice'

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const { loading, error, handleProcessInvoice, clearError } = useInvoice()

  const onFileSelect = (file) => {
    clearError()
    setSelectedFile(file)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="mx-auto max-w-2xl px-6 py-12">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-slate-900">Upload Invoice</h2>
          <p className="mt-2 text-slate-600">
            Upload a utility invoice PDF to extract structured data using AI.
          </p>
        </div>

        {loading ? (
          <Loader message="Extracting invoice data with AI..." />
        ) : (
          <div className="space-y-6">
            <FileUpload
              onFileSelect={onFileSelect}
              selectedFile={selectedFile}
              disabled={loading}
            />

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="button"
              onClick={() => handleProcessInvoice(selectedFile)}
              disabled={!selectedFile || loading}
              className="w-full rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              Process Invoice
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
