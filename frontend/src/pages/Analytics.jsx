import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'

const COLORS = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899']

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard().then(r => setData(r.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full" />
    </div>
  )

  if (!data) return <p className="p-6 text-gray-500">Could not load analytics.</p>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>

      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
        {[
          { label: 'Monthly Sales', val: data.month_sales, color: 'text-green-700', bg: 'bg-green-50' },
          { label: 'Monthly Expenses', val: data.month_expenses, color: 'text-red-600', bg: 'bg-red-50' },
          { label: 'Net Profit', val: data.net_profit, color: data.net_profit >= 0 ? 'text-green-700' : 'text-red-600', bg: data.net_profit >= 0 ? 'bg-green-50' : 'bg-red-50' },
          { label: 'Outstanding Udhaar', val: data.total_udhaar, color: 'text-orange-600', bg: 'bg-orange-50' },
          { label: "Today's Sales", val: data.today_sales, color: 'text-blue-700', bg: 'bg-blue-50' },
          { label: "Week's Sales", val: data.week_sales, color: 'text-purple-700', bg: 'bg-purple-50' },
        ].map(({ label, val, color, bg }) => (
          <div key={label} className={`${bg} rounded-xl p-4`}>
            <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
            <p className={`text-2xl font-bold ${color}`}>₹{val.toLocaleString('en-IN')}</p>
          </div>
        ))}
      </div>

      {/* Sales Trend */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-base font-semibold text-gray-800 mb-4">Sales Trend (Last 7 Days)</h2>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data.sales_trend}>
            <defs>
              <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={v => [`₹${v}`, 'Sales']} />
            <Area type="monotone" dataKey="sales" stroke="#f97316" fill="url(#salesGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Payment Modes */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Payment Mode Breakdown</h2>
          {data.payment_breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={data.payment_breakdown} dataKey="amount" nameKey="mode" cx="50%" cy="50%" outerRadius={75} label={({ mode, percent }) => `${mode} ${(percent * 100).toFixed(0)}%`}>
                  {data.payment_breakdown.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={v => `₹${v}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center mt-10">No data</p>}
        </div>

        {/* Expense Categories */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Expense Categories</h2>
          {data.expense_breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={data.expense_breakdown} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip formatter={v => `₹${v}`} />
                <Bar dataKey="amount" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center mt-10">No expenses</p>}
        </div>
      </div>
    </div>
  )
}
