import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Udhaar from './pages/Udhaar'
import Inventory from './pages/Inventory'
import Sales from './pages/Sales'
import Analytics from './pages/Analytics'
import Assistant from './pages/Assistant'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/udhaar" element={<Udhaar />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/assistant" element={<Assistant />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
