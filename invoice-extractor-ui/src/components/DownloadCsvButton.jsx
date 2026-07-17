import { getCsvDownloadUrl } from '../api/invoiceApi'

export default function DownloadCsvButton({ csvId }) {
  if (!csvId) return null

  const downloadUrl = getCsvDownloadUrl(csvId)

  return (
    <a
      href={downloadUrl}
      download
      className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-green-700"
    >
      <svg
        className="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      Download CSV
    </a>
  )
}
