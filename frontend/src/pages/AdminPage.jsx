import React, { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function AdminPage() {
  const [itemStats, setItemStats] = useState(null)
  const [claimStats, setClaimStats] = useState(null)
  const [error, setError] = useState(null)

  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined

  useEffect(() => {
    const load = async () => {
      try {
        const [itemsRes, claimsRes] = await Promise.all([
          axios.get(`${API_BASE}/items/stats`, { headers }),
          axios.get(`${API_BASE}/claims/stats/overview`, { headers }),
        ])
        setItemStats(itemsRes.data)
        setClaimStats(claimsRes.data)
      } catch (e) {
        setError(e.response?.data?.detail || e.message)
      }
    }
    load()
  }, [])

  if (error) return <div className="alert alert-danger">{error}</div>

  return (
    <div className="container">
      <h3 className="mb-4">Admin Dashboard</h3>
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="card text-bg-primary">
            <div className="card-body">
              <div className="text-uppercase small">Total Items</div>
              <div className="display-6">{itemStats?.total_items ?? '-'}</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-success">
            <div className="card-body">
              <div className="text-uppercase small">Found</div>
              <div className="display-6">{itemStats?.found_items ?? '-'}</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-warning">
            <div className="card-body">
              <div className="text-uppercase small">Lost</div>
              <div className="display-6">{itemStats?.lost_items ?? '-'}</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary">
            <div className="card-body">
              <div className="text-uppercase small">Recent (30d)</div>
              <div className="display-6">{itemStats?.recent_items_30_days ?? '-'}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">Item Status</div>
            <div className="card-body">
              <ul className="list-unstyled mb-0">
                <li>Active: <strong>{itemStats?.active_items ?? 'N/A'}</strong></li>
                <li>Claimed: <strong>{itemStats?.claimed_items ?? 'N/A'}</strong></li>
                <li>Returned: <strong>{itemStats?.returned_items ?? 'N/A'}</strong></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">Top Locations</div>
            <div className="card-body">
              <ul className="list-group">
                {(itemStats?.top_locations || []).map((l, i) => (
                  <li key={i} className="list-group-item d-flex justify-content-between align-items-center">
                    {l.location}
                    <span className="badge text-bg-primary rounded-pill">{l.count}</span>
                  </li>
                ))}
                {(!itemStats?.top_locations || itemStats.top_locations.length === 0) && (
                  <div className="text-muted">No data</div>
                )}
              </ul>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">Claims Overview</div>
            <div className="card-body">
              <ul className="list-unstyled mb-0">
                <li>Total: <strong>{claimStats?.total_claims ?? '-'}</strong></li>
                <li>Pending: <strong>{claimStats?.pending_claims ?? 'N/A'}</strong></li>
                <li>Approved: <strong>{claimStats?.approved_claims ?? 'N/A'}</strong></li>
                <li>Rejected: <strong>{claimStats?.rejected_claims ?? 'N/A'}</strong></li>
                <li>Completed: <strong>{claimStats?.completed_claims ?? 'N/A'}</strong></li>
                <li>This Month: <strong>{claimStats?.claims_this_month ?? '-'}</strong></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 