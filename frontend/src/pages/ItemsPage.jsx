import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../api.js'

export default function ItemsPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [filters, setFilters] = useState({ item_type: '', location: '', search: '' })

  const [form, setForm] = useState({
    name: '', description: '', item_type: 'lost', location: '', date: ''
  })
  const [submitting, setSubmitting] = useState(false)

  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined

  const fetchItems = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (filters.item_type) params.item_type = filters.item_type
      if (filters.location) params.location = filters.location
      if (filters.search) params.search = filters.search
      const { data } = await axios.get(`${API_BASE}/items/`, { params, headers })
      setItems(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchItems() }, [])

  const createItem = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.set('name', form.name)
      fd.set('description', form.description)
      fd.set('item_type', form.item_type)
      fd.set('location', form.location)
      fd.set('date', form.date)
      const { data } = await axios.post(`${API_BASE}/items/`, fd, { headers })
      setForm({ name: '', description: '', item_type: 'lost', location: '', date: '' })
      await fetchItems()
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setSubmitting(false)
    }
  }

  const claimItem = async (itemId) => {
    setError(null)
    try {
      await axios.post(`${API_BASE}/claims/`, { item_id: itemId, message: 'Interested in this item' }, { headers })
      alert('Claim submitted')
    } catch (e) {
      alert(e.response?.data?.detail || e.message)
    }
  }

  return (
    <div>
      <div className="row g-4">
        <div className="col-lg-8 order-2 order-lg-1">
          <div className="d-flex align-items-end gap-2 flex-wrap">
            <div>
              <label className="form-label" htmlFor="filterType">Type</label>
              <select id="filterType" className="form-select" value={filters.item_type} onChange={e => setFilters(f => ({...f, item_type: e.target.value}))}>
                <option value="">All</option>
                <option value="lost">Lost</option>
                <option value="found">Found</option>
              </select>
            </div>
            <div>
              <label className="form-label" htmlFor="filterLocation">Location</label>
              <input id="filterLocation" className="form-control" value={filters.location} onChange={e => setFilters(f => ({...f, location: e.target.value}))} placeholder="e.g. Library" />
            </div>
            <div className="flex-fill">
              <label className="form-label" htmlFor="filterSearch">Search</label>
              <input id="filterSearch" className="form-control" value={filters.search} onChange={e => setFilters(f => ({...f, search: e.target.value}))} placeholder="name or description" />
            </div>
            <div className="ms-auto">
              <button className="btn btn-primary me-2" onClick={fetchItems} disabled={loading}>Search</button>
              <button className="btn btn-outline-secondary" onClick={() => { setFilters({ item_type: '', location: '', search: '' }); fetchItems() }}>Reset</button>
            </div>
          </div>

          <hr />

          {error && <div className="alert alert-danger">{error}</div>}

          <div className="row g-3">
            {items.map(item => (
              <div className="col-md-6" key={item.id}>
                <div className="card h-100 shadow-sm">
                  {item.image_url && (
                    <img src={`${API_BASE}/${item.image_url}`} className="card-img-top" style={{objectFit:'cover', height: 180}} alt={item.name} />
                  )}
                  <div className="card-body d-flex flex-column">
                    <h5 className="card-title">{item.name}</h5>
                    <div className="text-muted small mb-2">{String(item.item_type).toUpperCase()} • {item.location} • {new Date(item.date).toLocaleDateString()}</div>
                    <p className="card-text flex-fill">{item.description}</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="badge text-bg-secondary text-uppercase">{item.status || 'active'}</span>
                      <button className="btn btn-sm btn-outline-primary" onClick={() => claimItem(item.id)}>Claim</button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {items.length === 0 && !loading && <div className="text-center text-muted py-5">No items found.</div>}
        </div>

        <div className="col-lg-4 order-1 order-lg-2">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">Create Item</h5>
              <form onSubmit={createItem}>
                <div className="mb-2">
                  <label className="form-label" htmlFor="itemName">Name</label>
                  <input id="itemName" className="form-control" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
                </div>
                <div className="mb-2">
                  <label className="form-label" htmlFor="itemDesc">Description</label>
                  <textarea id="itemDesc" className="form-control" rows="3" value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))} required />
                </div>
                <div className="mb-2">
                  <label className="form-label" htmlFor="itemType">Type</label>
                  <select id="itemType" className="form-select" value={form.item_type} onChange={e => setForm(f => ({...f, item_type: e.target.value}))}>
                    <option value="lost">Lost</option>
                    <option value="found">Found</option>
                  </select>
                </div>
                <div className="mb-2">
                  <label className="form-label" htmlFor="itemLoc">Location</label>
                  <input id="itemLoc" className="form-control" value={form.location} onChange={e => setForm(f => ({...f, location: e.target.value}))} required />
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="itemDate">Date</label>
                  <input id="itemDate" type="date" className="form-control" value={form.date} onChange={e => setForm(f => ({...f, date: e.target.value}))} required />
                </div>
                <button className="btn btn-primary w-100" type="submit" disabled={submitting}>Create</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 