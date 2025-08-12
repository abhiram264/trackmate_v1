import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function ClaimsPage() {
  const [claims, setClaims] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined

  const fetchClaims = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (statusFilter) params.status_filter = statusFilter
      const { data } = await axios.get(`${API_BASE}/claims/`, { params, headers })
      setClaims(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchClaims() }, [])

  return (
    <div>
      <div className="d-flex align-items-end gap-2 flex-wrap">
        <div>
          <label className="form-label" htmlFor="statusFilter">Status</label>
          <select id="statusFilter" className="form-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div className="ms-auto">
          <button className="btn btn-primary" onClick={fetchClaims} disabled={loading}>Search</button>
        </div>
      </div>

      <hr />

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Item</th>
              <th>Message</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {claims.map(c => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>#{c.item_id}</td>
                <td>{c.message}</td>
                <td><span className="badge text-bg-secondary text-uppercase">{c.status || 'pending'}</span></td>
                <td>{new Date(c.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {claims.length === 0 && !loading && <div className="text-center text-muted py-5">No claims yet.</div>}
    </div>
  )
}

export default ClaimsPage 