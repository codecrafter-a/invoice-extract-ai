import { Routes, Route, Navigate } from 'react-router-dom'
import UploadPage from '../pages/UploadPage'
import ResultsPage from '../pages/ResultsPage'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/results" element={<ResultsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
