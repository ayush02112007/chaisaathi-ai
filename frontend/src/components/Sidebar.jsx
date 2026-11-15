import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Package, ShoppingCart, TrendingUp, Mic
} from 'lucide-react'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/udhaar', icon: Users, label: 'Udhaar Khata' },
  { to: '/inventory', icon: Package, label: 'Inventory' },
  { to: '/sales', icon: ShoppingCart, label: 'Sales & Expenses' },
  { to: '/analytics', icon: TrendingUp, label: 'Analytics' },
  { to: '/assistant', icon: Mic, label: 'ChaiSaathi AI' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col min-h-screen">
      {/* Logo */}
      <div className="p-5 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl chai-gradient flex items-center justify-center text-white text-xl">
            ☕
          </div>
          <div>
            <div className="font-bold text-gray-900 text-lg leading-tight">ChaiSaathi</div>
            <div className="text-xs text-orange-500 font-medium">AI Business Assistant</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-400 text-center">ChaiSaathi AI v1.0</p>
      </div>
    </aside>
  )
}
