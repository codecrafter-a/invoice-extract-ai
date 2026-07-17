export default function Loader({ message = 'Processing invoice...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
      <p className="text-sm text-slate-600">{message}</p>
    </div>
  )
}
