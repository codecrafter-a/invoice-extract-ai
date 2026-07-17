import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import DownloadCsvButton from '../components/DownloadCsvButton'
import Header from '../components/Header'
import InvoiceTable from '../components/InvoiceTable'

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = location.state?.result
  const [showDetails, setShowDetails] = useState(false)

  if (!result) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <main className="mx-auto max-w-2xl px-6 py-12 text-center">
          <p className="text-slate-600">No extraction results found.</p>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Go to Upload
          </button>
        </main>
      </div>
    )
  }

  const {
    invoice,
    fields = [],
    warnings = [],
    csv_id: csvId,
    extraction_method: extractionMethod,
    detected_language: detectedLanguage,
    confidence = {},
  } = result

  const LANGUAGE_NAMES = {
    en: 'English',
    es: 'Spanish',
    fr: 'French',
    de: 'German',
    it: 'Italian',
    pt: 'Portuguese',
  }
  const languageLabel = detectedLanguage
    ? LANGUAGE_NAMES[detectedLanguage] || detectedLanguage.toUpperCase()
    : null

  const primaryFields = fields.filter((field) => field.primary)
  const detailFields = fields.filter((field) => !field.primary)

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Extraction Results</h2>
            <p className="mt-1 text-slate-600">
              Review the extracted invoice data below.
            </p>
          </div>
          <DownloadCsvButton csvId={csvId} />
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          {extractionMethod && (
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              Extracted via: {extractionMethod === 'openai' ? 'GPT-4o' : 'Regex fallback'}
            </span>
          )}
          {languageLabel && (
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
              Detected language: {languageLabel}
            </span>
          )}
        </div>

        {warnings.length > 0 && (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
            <p className="text-sm font-medium text-amber-800">Validation Warnings</p>
            <ul className="mt-2 space-y-1">
              {warnings.map((warning) => (
                <li key={warning.field} className="text-sm text-amber-700">
                  • {warning.message}
                </li>
              ))}
            </ul>
          </div>
        )}

        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Key Details
        </h3>
        <InvoiceTable
          invoice={invoice}
          fields={primaryFields}
          warnings={warnings}
          confidence={confidence}
        />

        {detailFields.length > 0 && (
          <div className="mt-6">
            <button
              type="button"
              onClick={() => setShowDetails((prev) => !prev)}
              className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              <span>{showDetails ? '▾' : '▸'}</span>
              {showDetails
                ? 'Hide additional details'
                : `View additional details (${detailFields.length} more fields)`}
            </button>

            {showDetails && (
              <div className="mt-3">
                <InvoiceTable
                  invoice={invoice}
                  fields={detailFields}
                  warnings={warnings}
                  confidence={confidence}
                />
              </div>
            )}
          </div>
        )}

        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← Upload another invoice
          </button>
        </div>
      </main>
    </div>
  )
}
