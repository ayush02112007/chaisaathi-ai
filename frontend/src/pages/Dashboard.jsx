import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { TrendingUp, Users, AlertTriangle, IndianRupee } from 'lucide-react'

const COLORS = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6']

function StatCard({ title, value, sub, icon: Icon, color = 'orange' }) {
  const colors = {
    orange: 'bg-orange-50 text-orange-600',
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
  }
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">₹{value?.toLocaleString('en-IN') ?? '—'}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-2 rounded-lg ${colors[color]}`}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard()
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full" />
    </div>
  )

  if (!data) return <p className="text-gray-500 p-6">Failed to load dashboard. Is backend running?</p>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Aaj ki Kamai" value={data.today_sales} sub="Today's Sales" icon={IndianRupee} color="orange" />
        <StatCard title="Mahine ki Kamai" value={data.month_sales} sub="Month Sales" icon={TrendingUp} color="green" />
        <StatCard title="Total Udhaar" value={data.total_udhaar} sub={`${data.customer_count} customers`} icon={Users} color="blue" />
        <StatCard title="Net Profit" value={data.net_profit} sub="Last 30 days" icon={IndianRupee} color={data.net_profit >= 0 ? 'green' : 'red'} />
      </div>

      {/* Alerts */}
      {data.low_stock_count > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle size={18} className="text-amber-500 shrink-0" />
          <span className="text-sm text-amber-800 font-medium">
            {data.low_stock_count} item(s) low on stock. Check Inventory.
          </span>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Sales Trend */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">7-Day Sales Trend</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.sales_trend}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => [`₹${v}`, 'Sales']} />
              <Bar dataKey="sales" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Payment Breakdown */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Payment Modes (30 days)</h2>
          {data.payment_breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={data.payment_breakdown} dataKey="amount" nameKey="mode" cx="50%" cy="50%" outerRadius={70} label={({ mode }) => mode}>
                  {data.payment_breakdown.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={v => `₹${v}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center mt-10">No sales data yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
