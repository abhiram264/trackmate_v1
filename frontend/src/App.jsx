import React, { useEffect, useState } from 'react'
import { Routes, Route, NavLink, useLocation, useNavigate } from 'react-router-dom'
import HomePage from './pages/HomePage.jsx'
import ItemsPage from './pages/ItemsPage.jsx'
import ClaimsPage from './pages/ClaimsPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import AdminPage from './pages/AdminPage.jsx'

function RequireAuth({ children }) {
  const token = localStorage.getItem('token')
  const location = useLocation()
  if (!token) {
    window.location.replace('/login')
    return null
  }
  return children
}

export default function App() {
  const navigate = useNavigate()
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
  }, [token])

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    navigate('/login')
  }

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container-fluid">
          <NavLink to="/" className="navbar-brand">TrackMate</NavLink>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item"><NavLink to="/" className="nav-link">Home</NavLink></li>
              <li className="nav-item"><NavLink to="/items" className="nav-link">Items</NavLink></li>
              <li className="nav-item"><NavLink to="/claims" className="nav-link">Claims</NavLink></li>
              <li className="nav-item"><NavLink to="/admin" className="nav-link">Admin</NavLink></li>
            </ul>
            <div className="d-flex">
              {token ? (
                <button className="btn btn-outline-light" onClick={logout}>Logout</button>
              ) : (
                <>
                  <NavLink to="/login" className="btn btn-outline-light me-2">Login</NavLink>
                  <NavLink to="/register" className="btn btn-primary">Register</NavLink>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="container py-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/items" element={<RequireAuth><ItemsPage /></RequireAuth>} />
          <Route path="/claims" element={<RequireAuth><ClaimsPage /></RequireAuth>} />
          <Route path="/admin" element={<RequireAuth><AdminPage /></RequireAuth>} />
          <Route path="/login" element={<LoginPage setToken={setToken} />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </div>
    </>
  )
} 