import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register as registerApi } from '../api/endpoints'

export default function Register() {
  const [form, setForm] = useState({ email: '', full_name: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handle = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await registerApi(form)
      navigate('/login?registered=1')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join(', '))
      } else {
        setError(detail || 'Registration failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">⚡</div>
          <span className="auth-logo-text">TaskFlow</span>
        </div>
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start managing projects with your team</p>

        {error && <div className="error-banner" role="alert">{error}</div>}

        <form className="auth-form" onSubmit={handle} id="register-form">
          <div className="form-group">
            <label className="form-label" htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              className="form-input"
              type="text"
              placeholder="Jane Doe"
              value={form.full_name}
              onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="reg_email">Email</label>
            <input
              id="reg_email"
              className="form-input"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="reg_password">Password</label>
            <input
              id="reg_password"
              className="form-input"
              type="password"
              placeholder="Min. 6 characters"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              required
              minLength={6}
            />
          </div>
          <button
            id="register-submit"
            className="btn btn-primary btn-lg"
            type="submit"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Sign in →</Link>
        </p>
      </div>
    </div>
  )
}
