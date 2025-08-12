import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'

export default function HomePage() {
  const navigate = useNavigate()
  return (
    <>
      {/* Hero */}
      <section className="bg-dark text-white py-5 py-lg-6">
        <div className="container">
          <div className="row align-items-center g-4">
            <div className="col-lg-7">
              <h1 className="display-4 fw-bold mb-3">TrackMate</h1>
              <p className="lead text-opacity-75 mb-4">
                Enterprise-grade lost & found management. Streamline reporting, claiming, and returning items with secure authentication, rich filtering, and actionable insights.
              </p>
              <div className="d-flex gap-3 flex-wrap">
                <button className="btn btn-primary btn-lg" onClick={() => navigate('/register')}>Get Started</button>
                <button className="btn btn-outline-light btn-lg" onClick={() => navigate('/login')}>Sign In</button>
              </div>
              <div className="mt-4 small text-secondary">
                Trusted by campuses and enterprises to reduce loss, improve recovery rates, and enhance operational visibility.
              </div>
            </div>
            <div className="col-lg-5 d-none d-lg-block">
              <div className="bg-body-tertiary rounded-4 shadow p-4 text-dark">
                <div className="row text-center g-3">
                  <div className="col-6">
                    <div className="h1 mb-0">99.9%</div>
                    <div className="text-muted">Uptime</div>
                  </div>
                  <div className="col-6">
                    <div className="h1 mb-0"><i className="bi bi-shield-lock"></i></div>
                    <div className="text-muted">Secure JWT</div>
                  </div>
                  <div className="col-6">
                    <div className="h1 mb-0">5x</div>
                    <div className="text-muted">Faster Recovery</div>
                  </div>
                  <div className="col-6">
                    <div className="h1 mb-0">24/7</div>
                    <div className="text-muted">Self-Service</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="fw-bold">Why TrackMate</h2>
            <p className="text-muted">Built for scale, simplicity, and security</p>
          </div>
          <div className="row g-4">
            <div className="col-md-6 col-lg-3">
              <div className="h-100 p-4 border rounded-4 shadow-sm">
                <div className="display-6 text-primary mb-3"><i className="bi bi-funnel"></i></div>
                <h5 className="fw-semibold mb-2">Powerful Filtering</h5>
                <p className="text-muted mb-0">Find items quickly by type, location, dates, status, and full-text search.</p>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="h-100 p-4 border rounded-4 shadow-sm">
                <div className="display-6 text-primary mb-3"><i className="bi bi-image"></i></div>
                <h5 className="fw-semibold mb-2">Media Support</h5>
                <p className="text-muted mb-0">Attach images securely to improve item identification and claims.</p>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="h-100 p-4 border rounded-4 shadow-sm">
                <div className="display-6 text-primary mb-3"><i className="bi bi-lock"></i></div>
                <h5 className="fw-semibold mb-2">Secure Auth</h5>
                <p className="text-muted mb-0">Role-aware access with industry-standard bcrypt hashing and JWT auth.</p>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="h-100 p-4 border rounded-4 shadow-sm">
                <div className="display-6 text-primary mb-3"><i className="bi bi-graph-up"></i></div>
                <h5 className="fw-semibold mb-2">Actionable Insights</h5>
                <p className="text-muted mb-0">Out-of-the-box analytics for locations, trends, and recent activity.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-5 bg-body-tertiary">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="fw-bold">How It Works</h2>
            <p className="text-muted">Three simple steps to reunite items with owners</p>
          </div>
          <div className="row g-4 text-center">
            <div className="col-md-4">
              <div className="display-5 text-primary mb-2"><i className="bi bi-plus-square"></i></div>
              <h5>Log Items</h5>
              <p className="text-muted">Staff or users create entries for lost or found items with details and images.</p>
            </div>
            <div className="col-md-4">
              <div className="display-5 text-primary mb-2"><i className="bi bi-search"></i></div>
              <h5>Search & Claim</h5>
              <p className="text-muted">Advanced filters help owners discover items and submit verified claims.</p>
            </div>
            <div className="col-md-4">
              <div className="display-5 text-primary mb-2"><i className="bi bi-check2-circle"></i></div>
              <h5>Resolve</h5>
              <p className="text-muted">Admins approve claims and track returns with audit-friendly status updates.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to action */}
      <section className="py-5">
        <div className="container text-center">
          <h2 className="fw-bold mb-3">Ready to modernize lost & found?</h2>
          <p className="text-muted mb-4">Deploy TrackMate to reduce losses, lift recovery rates, and delight users.</p>
          <div className="d-flex justify-content-center gap-3">
            <NavLink to="/register" className="btn btn-primary btn-lg">Get Started</NavLink>
            <NavLink to="/login" className="btn btn-outline-secondary btn-lg">Sign In</NavLink>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-top py-4">
        <div className="container d-flex flex-wrap justify-content-between align-items-center gap-2">
          <span className="text-muted">© {new Date().getFullYear()} TrackMate</span>
          <ul className="nav">
            <li className="nav-item"><a className="nav-link px-2 text-muted" href="#">Privacy</a></li>
            <li className="nav-item"><a className="nav-link px-2 text-muted" href="#">Security</a></li>
            <li className="nav-item"><a className="nav-link px-2 text-muted" href="#">Status</a></li>
            <li className="nav-item"><a className="nav-link px-2 text-muted" href="#">Contact</a></li>
          </ul>
        </div>
      </footer>
    </>
  )
} 