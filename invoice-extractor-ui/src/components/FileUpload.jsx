import { useRef } from 'react'

export default function FileUpload({ onFileSelect, selectedFile, disabled }) {
  const inputRef = useRef(null)

  const handleChange = (event) => {
    const file = event.target.files?.[0] || null
    onFileSelect(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    if (disabled) return

    const file = event.dataTransfer.files?.[0] || null
    if (file) {
      onFileSelect(file)
    }
  }

  return (
    <div
      className={`rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
        disabled
          ? 'cursor-not-allowed border-slate-200 bg-slate-50'
          : 'cursor-pointer border-slate-300 bg-white hover:border-blue-400 hover:bg-blue-50/30'
      }`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />

      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
        <svg
          className="h-7 w-7 text-blue-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>

      <p className="text-base font-medium text-slate-800">
        {selectedFile ? selectedFile.name : 'Drop your PDF here or click to browse'}
      </p>
      <p className="mt-1 text-sm text-slate-500">Supports utility invoice PDFs</p>
    </div>
  )
}
