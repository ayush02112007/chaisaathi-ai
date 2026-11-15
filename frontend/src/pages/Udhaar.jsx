import { useEffect, useState } from 'react'
import {
  getCustomers, createCustomer, deleteCustomer,
  getUdhaar, addUdhaar, markPaid
} from '../api'
import { Plus, ChevronDown, ChevronUp, Check, Trash2, User } from 'lucide-react'

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  )
}

export default function Udhaar() {
  const [customers, setCustomers] = useState([])
  const [expanded, setExpanded] = useState(null)
  const [udhaarMap, setUdhaarMap] = useState({})
  const [showAdd, setShowAdd] = useState(false)
  const [showUdhaarFor, setShowUdhaarFor] = useState(null)
  const [form, setForm] = useState({ name: '', phone: '', address: '' })
  const [uForm, setUForm] = useState({ amount: '', description: '' })

  const load = () => getCustomers().then(r => setCustomers(r.data))
  useEffect(() => { load() }, [])

  const toggle = async (id) => {
    if (expanded === id) { setExpanded(null); return }
    setExpanded(id)
    if (!udhaarMap[id]) {
      const r = await getUdhaar(id)
      setUdhaarMap(m => ({ ...m, [id]: r.data }))
    }
  }

  const handleAddCustomer = async (e) => {
    e.preventDefault()
    await createCustomer(form)
    setShowAdd(false)
    setForm({ name: '', phone: '', address: '' })
    load()
  }

  const handleAddUdhaar = async (e) => {
    e.preventDefault()
    await addUdhaar({ customer_id: showUdhaarFor, ...uForm, amount: parseFloat(uForm.amount) })
    setShowUdhaarFor(null)
    setUForm({ amount: '', description: '' })
    // refresh udhaar for this customer
    const r = await getUdhaar(showUdhaarFor)
    setUdhaarMap(m => ({ ...m, [showUdhaarFor]: r.data }))
    load() // refresh totals
  }

  const handlePaid = async (customerId, udhaarId) => {
    await markPaid(udhaarId)
    const r = await getUdhaar(customerId)
    setUdhaarMap(m => ({ ...m, [customerId]: r.data }))
    load()
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this customer?')) return
    await deleteCustomer(id)
    load()
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Udhaar Khata</h1>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600"
        >
          <Plus size={16} /> Add Customer
        </button>
      </div>

      {customers.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <User size={40} className="mx-auto mb-3 opacity-30" />
          <p>No customers yet. Add one to start tracking udhaar.</p>
        </div>
      )}

      <div className="space-y-2">
        {customers.map(c => (
          <div key={c.id} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
              onClick={() => toggle(c.id)}
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-semibold text-sm">
                  {c.name[0].toUpperCase()}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{c.name}</p>
                  <p className="text-xs text-gray-400">{c.phone}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {c.total_udhaar > 0 && (
                  <span className="text-sm font-semibold text-red-600">₹{c.total_udhaar.toLocaleString('en-IN')}</span>
                )}
                {expanded === c.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
              </div>
            </div>

            {expanded === c.id && (
              <div className="border-t border-gray-100 p-4 space-y-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowUdhaarFor(c.id)}
                    className="text-xs bg-orange-50 text-orange-600 px-3 py-1.5 rounded-lg font-medium hover:bg-orange-100"
                  >
                    + Add Udhaar
                  </button>
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="text-xs bg-red-50 text-red-500 px-3 py-1.5 rounded-lg font-medium hover:bg-red-100 flex items-center gap-1"
                  >
                    <Trash2 size={12} /> Delete
                  </button>
                </div>

                {(udhaarMap[c.id] || []).length === 0 ? (
                  <p className="text-xs text-gray-400">No udhaar entries</p>
                ) : (
                  <div className="space-y-2">
                    {(udhaarMap[c.id] || []).map(u => (
                      <div key={u.id} className={`flex items-center justify-between p-3 rounded-lg text-sm ${u.is_paid ? 'bg-green-50' : 'bg-red-50'}`}>
                        <div>
                          <span className={`font-medium ${u.is_paid ? 'text-green-700 line-through' : 'text-red-700'}`}>
                            ₹{u.amount.toLocaleString('en-IN')}
                          </span>
                          {u.description && <span className="text-gray-500 ml-2 text-xs">{u.description}</span>}
                          <div className="text-xs text-gray-400">{new Date(u.created_at).toLocaleDateString('en-IN')}</div>
                        </div>
                        {!u.is_paid && (
                          <button
                            onClick={() => handlePaid(c.id, u.id)}
                            className="flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                          >
                            <Check size={12} /> Paid
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add Customer Modal */}
      {showAdd && (
        <Modal title="Add Customer" onClose={() => setShowAdd(false)}>
          <form onSubmit={handleAddCustomer} className="space-y-4">
            {[['name', 'Name *'], ['phone', 'Phone *'], ['address', 'Address']].map(([k, l]) => (
              <div key={k}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{l}</label>
                <input
                  required={k !== 'address'}
                  value={form[k]}
                  onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none"
                />
              </div>
            ))}
            <button type="submit" className="w-full bg-orange-500 text-white py-2 rounded-lg font-medium hover:bg-orange-600">
              Add Customer
            </button>
          </form>
        </Modal>
      )}

      {/* Add Udhaar Modal */}
      {showUdhaarFor && (
        <Modal title="Add Udhaar Entry" onClose={() => setShowUdhaarFor(null)}>
          <form onSubmit={handleAddUdhaar} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹) *</label>
              <input
                required
                type="number"
                min="1"
                value={uForm.amount}
                onChange={e => setUForm(f => ({ ...f, amount: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <input
                value={uForm.description}
                onChange={e => setUForm(f => ({ ...f, description: e.target.value }))}
                placeholder="e.g. Chai & Biscuit"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none"
              />
            </div>
            <button type="submit" className="w-full bg-orange-500 text-white py-2 rounded-lg font-medium hover:bg-orange-600">
              Add Udhaar
            </button>
          </form>
        </Modal>
      )}
    </div>
  )
}
