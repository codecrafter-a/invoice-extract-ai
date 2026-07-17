export default function InvoiceTable({ invoice, fields = [], warnings = [], confidence = {} }) {
  const warningFields = new Set(warnings.map((warning) => warning.field))
  const hasConfidence = Object.keys(confidence).length > 0

  const renderConfidence = (key) => {
    const score = confidence[key]
    if (score === undefined || score === null) {
      return <span className="text-slate-300">—</span>
    }
    const pct = Math.round(score * 100)
    const color =
      score >= 0.8 ? 'text-green-600' : score >= 0.5 ? 'text-amber-600' : 'text-red-500'
    return <span className={`text-sm font-medium ${color}`}>{pct}%</span>
  }

  const formatValue = (value, type) => {
    if (value === null || value === undefined || value === '') {
      return <span className="text-slate-400 italic">Not found</span>
    }

    if (type === 'number') {
      return Number(value).toLocaleString()
    }

    if (type === 'enum') {
      return (
        <span className="capitalize rounded-full bg-slate-100 px-2 py-0.5 text-sm">
          {value}
        </span>
      )
    }

    return value
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Field
            </th>
            <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Extracted Value
            </th>
            {hasConfidence && (
              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Confidence
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {fields.map((field) => (
            <tr key={field.key} className="border-b border-slate-100 last:border-0">
              <td className="px-6 py-4 text-sm font-medium text-slate-700">
                {field.label}
                {field.required && <span className="ml-1 text-red-500">*</span>}
              </td>
              <td className="px-6 py-4 text-sm text-slate-900">
                {formatValue(invoice?.[field.key], field.type)}
                {warningFields.has(field.key) && (
                  <span className="ml-2 text-xs text-amber-600">⚠</span>
                )}
              </td>
              {hasConfidence && (
                <td className="px-6 py-4">{renderConfidence(field.key)}</td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
