import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function LoginPage({ setToken }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const form = new FormData()
      form.set('username', email)
      form.set('password', password)
      const { data } = await axios.post(`${API_BASE}/auth/login`, form)
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
      navigate('/items')
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-6 col-lg-5">
        <div className="card shadow-sm">
          <div className="card-body">
            <h3 className="mb-3">Login</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={onSubmit}>
              <div className="mb-3">
                <label className="form-label" htmlFor="loginEmail">Email</label>
                <input id="loginEmail" type="email" className="form-control" value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="loginPassword">Password</label>
                <input id="loginPassword" type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
              </div>
              <button className="btn btn-primary" type="submit" disabled={loading}>Login</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
} 