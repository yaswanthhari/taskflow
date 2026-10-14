import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProjects, createProject } from '../api/endpoints'

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  const fetchProjects = async (q = '') => {
    setLoading(true)
    try {
      const res = await getProjects({ search: q || undefined, page_size: 50 })
      setProjects(res.data.items)
      setTotal(res.data.total)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProjects() }, [])

  useEffect(() => {
    const t = setTimeout(() => fetchProjects(search), 350)
    return () => clearTimeout(t)
  }, [search])

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    setError('')
    try {
      const res = await createProject(form)
      setProjects(prev => [res.data, ...prev])
      setTotal(t => t + 1)
      setShowModal(false)
      setForm({ name: '', description: '' })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project.')
    } finally {
      setCreating(false)
    }
  }

  const timeAgo = (iso) => {
    const diff = Date.now() - new Date(iso).getTime()
    const days = Math.floor(diff / 86400000)
    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    return `${days}d ago`
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">{total} project{total !== 1 ? 's' : ''} in your workspace</p>
        </div>
        <div className="flex gap-12 items-center">
          <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input
              id="project-search"
              className="search-input"
              placeholder="Search projects…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <button
            id="create-project-btn"
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
          >
            <span>+</span> New Project
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner"><div className="spinner" /></div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <div className="empty-title">No projects found</div>
          <div className="empty-desc">{search ? 'Try a different search term' : 'Create your first project to get started'}</div>
          {!search && (
            <button className="btn btn-primary" style={{ marginTop: 8 }} onClick={() => setShowModal(true)}>
              Create Project
            </button>
          )}
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(p => (
            <Link key={p.id} to={`/projects/${p.id}`} className="project-card" id={`project-card-${p.id}`}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: 16, marginBottom: 14,
              }}>
                {p.name.slice(0, 2).toUpperCase()}
              </div>
              <div className="project-card-name">{p.name}</div>
              <div className="project-card-desc">{p.description || 'No description'}</div>
              <div className="project-card-meta">
                <span className="meta-chip">👤 {p.member_count} member{p.member_count !== 1 ? 's' : ''}</span>
                <span className="meta-chip">🕐 {timeAgo(p.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" id="create-project-modal" onClick={e => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">New Project</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            {error && <div className="error-banner" style={{ marginBottom: 16 }}>{error}</div>}
            <form className="modal-form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label" htmlFor="project-name">Project Name</label>
                <input
                  id="project-name"
                  className="form-input"
                  placeholder="e.g. Website Redesign"
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="project-desc">Description</label>
                <textarea
                  id="project-desc"
                  className="form-textarea"
                  placeholder="What is this project about?"
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button id="create-project-submit" type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating…' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
