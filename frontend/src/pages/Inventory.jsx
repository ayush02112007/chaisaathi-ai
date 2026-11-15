import { useEffect, useState } from 'react'
import { getInventory, createItem, updateItem, deleteItem } from '../api'
import { Plus, Pencil, Trash2, AlertTriangle, Package } from 'lucide-react'

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

const empty = { name: '', category: 'General', quantity: '', unit: 'pcs', purchase_price: '', selling_price: '', low_stock_alert: '10' }

export default function Inventory() {
  const [items, setItems] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editItem, setEditItem] = useState(null)
  const [form, setForm] = useState(empty)

  const load = () => getInventory().then(r => setItems(r.data))
  useEffect(() => { load() }, [])

  const openEdit = (item) => {
    setEditItem(item)
    setForm({ ...item, quantity: String(item.quantity), purchase_price: String(item.purchase_price), selling_price: String(item.selling_price), low_stock_alert: String(item.low_stock_alert) })
    setShowForm(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      quantity: parseFloat(form.quantity),
      purchase_price: parseFloat(form.purchase_price),
      selling_price: parseFloat(form.selling_price),
      low_stock_alert: parseFloat(form.low_stock_alert),
    }
    if (editItem) {
      await updateItem(editItem.id, payload)
    } else {
      await createItem(payload)
    }
    setShowForm(false)
    setEditItem(null)
    setForm(empty)
    load()
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete item?')) return
    await deleteItem(id)
    load()
  }

  const f = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
        <button
          onClick={() => { setEditItem(null); setForm(empty); setShowForm(true) }}
          className="flex items-center gap-2 bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600"
        >
          <Plus size={16} /> Add Item
        </button>
      </div>

      {items.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <Package size={40} className="mx-auto mb-3 opacity-30" />
          <p>No items yet. Add your stock items.</p>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        {items.length > 0 && (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['Item', 'Category', 'Stock', 'Buy Price', 'Sell Price', 'Margin', ''].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {items.map(item => {
                const low = item.quantity <= item.low_stock_alert
                const margin = item.purchase_price > 0
                  ? (((item.selling_price - item.purchase_price) / item.purchase_price) * 100).toFixed(0)
                  : '—'
                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900 flex items-center gap-2">
                      {low && <AlertTriangle size={14} className="text-amber-500 shrink-0" />}
                      {item.name}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{item.category}</td>
                    <td className={`px-4 py-3 font-medium ${low ? 'text-red-600' : 'text-gray-900'}`}>
                      {item.quantity} {item.unit}
                    </td>
                    <td className="px-4 py-3 text-gray-600">₹{item.purchase_price}</td>
                    <td className="px-4 py-3 text-gray-600">₹{item.selling_price}</td>
                    <td className="px-4 py-3">
                      {margin !== '—' && (
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${Number(margin) >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {margin}%
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => openEdit(item)} className="p-1.5 text-gray-400 hover:text-blue-500">
                          <Pencil size={14} />
                        </button>
                        <button onClick={() => handleDelete(item.id)} className="p-1.5 text-gray-400 hover:text-red-500">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {showForm && (
        <Modal title={editItem ? 'Edit Item' : 'Add Item'} onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              {[
                ['name', 'Item Name', 'text', true, 'col-span-2'],
                ['category', 'Category', 'text', false, ''],
                ['unit', 'Unit', 'text', false, ''],
                ['quantity', 'Quantity', 'number', true, ''],
                ['low_stock_alert', 'Low Stock At', 'number', false, ''],
                ['purchase_price', 'Buy Price ₹', 'number', false, ''],
                ['selling_price', 'Sell Price ₹', 'number', false, ''],
              ].map(([k, l, t, req, cls]) => (
                <div key={k} className={cls}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{l}</label>
                  <input
                    required={req}
                    type={t}
                    min={t === 'number' ? '0' : undefined}
                    step={t === 'number' ? 'any' : undefined}
                    value={form[k]}
                    onChange={f(k)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none"
                  />
                </div>
              ))}
            </div>
            <button type="submit" className="w-full bg-orange-500 text-white py-2 rounded-lg font-medium hover:bg-orange-600 mt-2">
              {editItem ? 'Update Item' : 'Add Item'}
            </button>
          </form>
        </Modal>
      )}
    </div>
  )
}
