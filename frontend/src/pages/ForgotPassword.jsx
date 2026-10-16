import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    background: '#0d1117',
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  card: {
    width: '100%',
    maxWidth: 420,
    padding: 32,
    borderRadius: 20,
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    color: '#e6edf3',
  },
  title: { fontSize: 24, fontWeight: 700, margin: '0 0 6px' },
  sub: { color: '#8b949e', margin: '0 0 20px', fontSize: 14 },
  label: {
    display: 'block',
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: 1,
    color: '#8b949e',
    margin: '14px 0 6px',
    textTransform: 'uppercase',
  },
  input: {
    width: '100%',
    boxSizing: 'border-box',
    padding: '12px 14px',
    borderRadius: 10,
    border: '1px solid rgba(255,255,255,0.12)',
    background: '#0d1117',
    color: '#e6edf3',
    fontSize: 15,
  },
  button: {
    width: '100%',
    marginTop: 20,
    padding: 13,
    borderRadius: 10,
    border: 'none',
    background: '#6e40c9',
    color: '#fff',
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
  },
  link: { color: '#58a6ff', background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, padding: 0 },
  error: { background: 'rgba(248,81,73,0.12)', color: '#ff7b72', padding: '10px 12px', borderRadius: 10, marginBottom: 12, fontSize: 14 },
  ok: { background: 'rgba(63,185,80,0.12)', color: '#56d364', padding: '10px 12px', borderRadius: 10, marginBottom: 12, fontSize: 14 },
  footer: { textAlign: 'center', marginTop: 18, fontSize: 14, color: '#8b949e' },
}

function errorText(err, fallback) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg.replace(/^Value error, /, '')
  if (!err?.response) return 'Cannot reach the server. If it was idle, wait a minute and try again.'
  return fallback
}

export default function ForgotPassword() {
  const [step, setStep] = useState(1) // 1 = ask for code, 2 = enter code + new password, 3 = done
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)

  const requestCode = async (e) => {
    e?.preventDefault()
    setError('')
    setInfo('')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/forgot-password', { email: email.trim() })

      // Local development only: the server tells us when the email has no account here.
      if (data.dev_note) {
        setError(data.dev_note)
        return
      }

      // Local development only: the server returns the code so you can test without email.
      if (data.dev_code) {
        setCode(data.dev_code)
        setInfo(
          `Local dev mode: your code is ${data.dev_code} and it has been filled in for you. ` +
            'On the live site the code arrives by email.'
        )
      } else {
        setInfo(data.message)
      }
      setStep(2)
    } catch (err) {
      setError(errorText(err, 'Could not send the code. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (e) => {
    e.preventDefault()
    setError('')
    setInfo('')
    setLoading(true)
    try {
      await api.post('/auth/reset-password', {
        email: email.trim(),
        code: code.trim(),
        new_password: password,
      })
      setStep(3)
    } catch (err) {
      setError(errorText(err, 'Could not reset the password. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>
          {step === 3 ? 'Password updated' : 'Reset your password'}
        </h1>

        {step === 1 && (
          <form onSubmit={requestCode}>
            <p style={styles.sub}>Enter your account email and we will send you a 6-digit code.</p>
            {error && <div style={styles.error}>{error}</div>}
            <label style={styles.label} htmlFor="fp-email">Email</label>
            <input
              id="fp-email"
              style={styles.input}
              type="email"
              required
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
            <button style={styles.button} type="submit" disabled={loading}>
              {loading ? 'Sending...' : 'Send code'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={resetPassword}>
            <p style={styles.sub}>Enter the 6-digit code from your email and choose a new password.</p>
            {info && <div style={styles.ok}>{info}</div>}
            {error && <div style={styles.error}>{error}</div>}
            <label style={styles.label} htmlFor="fp-code">Code</label>
            <input
              id="fp-code"
              style={styles.input}
              inputMode="numeric"
              maxLength={6}
              required
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              placeholder="123456"
            />
            <label style={styles.label} htmlFor="fp-pass">New password</label>
            <input
              id="fp-pass"
              style={styles.input}
              type="password"
              required
              autoFocus
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters, with a letter and a number"
            />
            <button style={styles.button} type="submit" disabled={loading}>
              {loading ? 'Updating...' : 'Update password'}
            </button>
            <div style={{ ...styles.footer, marginTop: 14 }}>
              Did not get it?{' '}
              <button type="button" style={styles.link} onClick={requestCode} disabled={loading}>
                Send a new code
              </button>{' '}
              (one per minute)
            </div>
          </form>
        )}

        {step === 3 && (
          <div>
            <p style={styles.sub}>Your password has been changed. You can sign in with it now.</p>
            <Link to="/login">
              <button style={styles.button} type="button">Go to sign in</button>
            </Link>
          </div>
        )}

        {step !== 3 && (
          <div style={styles.footer}>
            <Link to="/login" style={{ color: '#58a6ff' }}>Back to sign in</Link>
          </div>
        )}
      </div>
    </div>
  )
}
