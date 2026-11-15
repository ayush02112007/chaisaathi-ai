import { useEffect, useState } from 'react'
import {
  getSales, createSale, getExpenses, createExpense, deleteExpense, getInventory
} from '../api'
import { Plus, Trash2, ShoppingCart, Receipt } from 'lucide-react'

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  )
}

export default function Sales() {
  const [tab, setTab] = useState('sales')
  const [sales, setSales] = useState([])
  const [expenses, setExpenses] = useState([])
  const [inventory, setInventory] = useState([])
  const [showSaleForm, setShowSaleForm] = useState(false)
  const [showExpForm, setShowExpForm] = useState(false)
  const [sForm, setSForm] = useState({ item_id: '', item_name: '', quantity: '1', amount: '', payment_mode: 'cash', notes: '' })
  const [eForm, setEForm] = useState({ category: 'General', amount: '', description: '' })

  const load = () => {
    getSales().then(r => setSales(r.data))
    getExpenses().then(r => setExpenses(r.data))
    getInventory().then(r => setInventory(r.data))
  }
  useEffect(() => { load() }, [])

  const handleSale = async (e) => {
    e.preventDefault()
    const payload = {
      ...sForm,
      item_id: sForm.item_id ? parseInt(sForm.item_id) : null,
      quantity: parseFloat(sForm.quantity),
      amount: parseFloat(sForm.amount),
    }
    await createSale(payload)
    setShowSaleForm(false)
    setSForm({ item_id: '', item_name: '', quantity: '1', amount: '', payment_mode: 'cash', notes: '' })
    load()
  }

  const handleExp = async (e) => {
    e.preventDefault()
    await createExpense({ ...eForm, amount: parseFloat(eForm.amount) })
    setShowExpForm(false)
    setEForm({ category: 'General', amount: '', description: '' })
    load()
  }

  const handleSelectItem = (e) => {
    const id = e.target.value
    const item = inventory.find(i => String(i.id) === id)
    setSForm(f => ({
      ...f,
      item_id: id,
      item_name: item ? item.name : '',
      amount: item ? String(item.selling_price) : f.amount
    }))
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sales & Expenses</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowSaleForm(true)} className="flex items-center gap-2 bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600">
            <Plus size={16} /> Sale
          </button>
          <button onClick={() => setShowExpForm(true)} className="flex items-center gap-2 bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800">
            <Plus size={16} /> Expense
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
        {[['sales', 'Sales', ShoppingCart], ['expenses', 'Expenses', Receipt]].map(([key, label, Icon]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === key ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'}`}
          >
            <Icon size={14} />{label}
          </button>
        ))}
      </div>

      {/* Sales Table */}
      {tab === 'sales' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          {sales.length === 0 ? (
            <p className="text-center text-gray-400 py-12">No sales yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  {['Item', 'Qty', 'Amount', 'Mode', 'Date'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {sales.map(s => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{s.item_name || 'Manual Entry'}</td>
                    <td className="px-4 py-3 text-gray-500">{s.quantity}</td>
                    <td className="px-4 py-3 font-semibold text-green-700">₹{s.amount.toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        s.payment_mode === 'cash' ? 'bg-green-100 text-green-700' :
                        s.payment_mode === 'upi' ? 'bg-blue-100 text-blue-700' :
                        'bg-red-100 text-red-700'
                      }`}>{s.payment_mode}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{new Date(s.created_at).toLocaleDateString('en-IN')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Expenses Table */}
      {tab === 'expenses' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          {expenses.length === 0 ? (
            <p className="text-center text-gray-400 py-12">No expenses yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  {['Category', 'Description', 'Amount', 'Date', ''].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {expenses.map(e => (
                  <tr key={e.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{e.category}</td>
                    <td className="px-4 py-3 text-gray-500">{e.description}</td>
                    <td className="px-4 py-3 font-semibold text-red-600">₹{e.amount.toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{new Date(e.created_at).toLocaleDateString('en-IN')}</td>
                    <td className="px-4 py-3">
                      <button onClick={() => deleteExpense(e.id).then(load)} className="p-1.5 text-gray-400 hover:text-red-500">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Sale Form */}
      {showSaleForm && (
        <Modal title="Record Sale" onClose={() => setShowSaleForm(false)}>
          <form onSubmit={handleSale} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Item from Inventory (optional)</label>
              <select value={sForm.item_id} onChange={handleSelectItem}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none">
                <option value="">-- Manual Entry --</option>
                {inventory.map(i => <option key={i.id} value={i.id}>{i.name} (Stock: {i.quantity})</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Item Name</label>
              <input value={sForm.item_name} onChange={e => setSForm(f => ({ ...f, item_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Quantity</label>
                <input required type="number" min="0.1" step="any" value={sForm.quantity} onChange={e => setSForm(f => ({ ...f, quantity: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Amount ₹ *</label>
                <input required type="number" min="0" step="any" value={sForm.amount} onChange={e => setSForm(f => ({ ...f, amount: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Payment Mode</label>
              <select value={sForm.payment_mode} onChange={e => setSForm(f => ({ ...f, payment_mode: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none">
                <option value="cash">Cash</option>
                <option value="upi">UPI</option>
                <option value="udhaar">Udhaar</option>
              </select>
            </div>
            <button type="submit" className="w-full bg-orange-500 text-white py-2 rounded-lg font-medium hover:bg-orange-600">Record Sale</button>
          </form>
        </Modal>
      )}

      {/* Expense Form */}
      {showExpForm && (
        <Modal title="Add Expense" onClose={() => setShowExpForm(false)}>
          <form onSubmit={handleExp} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Category</label>
              <input value={eForm.category} onChange={e => setEForm(f => ({ ...f, category: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Amount ₹ *</label>
              <input required type="number" min="0" step="any" value={eForm.amount} onChange={e => setEForm(f => ({ ...f, amount: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <input value={eForm.description} onChange={e => setEForm(f => ({ ...f, description: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none" />
            </div>
            <button type="submit" className="w-full bg-gray-700 text-white py-2 rounded-lg font-medium hover:bg-gray-800">Add Expense</button>
          </form>
        </Modal>
      )}
    </div>
  )
}
