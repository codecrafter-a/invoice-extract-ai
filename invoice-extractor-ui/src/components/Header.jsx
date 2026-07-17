export default function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">
            Utility Invoice Extractor
          </h1>
          <p className="text-sm text-slate-500">
            AI-powered extraction from PDF invoices
          </p>
        </div>
        <div className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
          GPT-4o
        </div>
      </div>
    </header>
  )
}
