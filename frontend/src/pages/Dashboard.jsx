import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, getProjects } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'

const STAT_CARDS = [
  { key: 'total_projects', label: 'Projects', icon: '📁', color: '#6e40c9' },
  { key: 'todo', label: 'To Do', icon: '📋', color: '#8b949e' },
  { key: 'in_progress', label: 'In Progress', icon: '🔄', color: '#58a6ff' },
  { key: 'done', label: 'Completed', icon: '✅', color: '#39d353' },
  { key: 'overdue', label: 'Overdue', icon: '⚠️', color: '#f78166' },
]

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getDashboard(), getProjects({ page_size: 5 })])
      .then(([s, p]) => {
        setStats(s.data)
        setProjects(p.data.items)
      })
      .finally(() => setLoading(false))
  }, [])

  const firstName = user?.full_name?.split(' ')[0] || 'there'

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Good day, {firstName} 👋</h1>
          <p className="page-subtitle">Here's what's happening across your projects</p>
        </div>
        <Link to="/projects" className="btn btn-primary" id="go-to-projects">
          <span>+</span> New Project
        </Link>
      </div>

      {loading ? (
        <div className="loading-spinner"><div className="spinner" /></div>
      ) : (
        <>
          <div className="stats-grid">
            {STAT_CARDS.map(({ key, label, icon, color }) => (
              <div className="stat-card" key={key} style={{ '--accent-color': color }}>
                <div className="stat-icon">{icon}</div>
                <div className="stat-value">{stats?.[key] ?? 0}</div>
                <div className="stat-label">{label}</div>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="flex justify-between items-center" style={{ marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>Recent Projects</h2>
              <Link to="/projects" className="btn btn-secondary btn-sm">View all</Link>
            </div>
            {projects.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🚀</div>
                <div className="empty-title">No projects yet</div>
                <div className="empty-desc">Create your first project to get started</div>
                <Link to="/projects" className="btn btn-primary" style={{ marginTop: 8 }}>
                  Create Project
                </Link>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {projects.map(p => (
                  <Link
                    key={p.id}
                    to={`/projects/${p.id}`}
                    className="member-row"
                    style={{ textDecoration: 'none', transition: 'all 200ms' }}
                    id={`project-row-${p.id}`}
                  >
                    <div className="user-avatar" style={{ borderRadius: '8px' }}>
                      {p.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div className="member-info">
                      <div className="member-name">{p.name}</div>
                      <div className="member-email">{p.member_count} member{p.member_count !== 1 ? 's' : ''}</div>
                    </div>
                    <span style={{ color: 'var(--text-muted)', fontSize: 18 }}>›</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
