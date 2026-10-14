import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  getProject, getTasks, createTask, updateTask, deleteTask, addMember
} from '../api/endpoints'
import { useAuth } from '../context/AuthContext'

const COLUMNS = [
  { key: 'todo', label: 'To Do', dot: 'var(--status-todo)' },
  { key: 'in_progress', label: 'In Progress', dot: 'var(--status-progress)' },
  { key: 'done', label: 'Done', dot: 'var(--status-done)' },
]

const PRIORITY_COLORS = { low: '#8b949e', medium: '#e3b341', high: '#f78166' }
const PRIORITY_LABELS = { low: '↓ Low', medium: '→ Medium', high: '↑ High' }

function TaskModal({ open, onClose, onSave, members, initial }) {
  const [form, setForm] = useState(initial || {
    title: '', description: '', status: 'todo', priority: 'medium', assignee_id: '', due_date: ''
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (open) setForm(initial || { title: '', description: '', status: 'todo', priority: 'medium', assignee_id: '', due_date: '' })
    setError('')
  }, [open, initial])

  if (!open) return null

  const handle = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = {
        ...form,
        assignee_id: form.assignee_id ? parseInt(form.assignee_id) : null,
        due_date: form.due_date || null,
      }
      await onSave(payload)
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save task.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" id="task-modal" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">{initial ? 'Edit Task' : 'New Task'}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        {error && <div className="error-banner" style={{ marginBottom: 16 }}>{error}</div>}
        <form className="modal-form" onSubmit={handle}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input id="task-title" className="form-input" placeholder="Task title" value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))} required autoFocus />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea id="task-desc" className="form-textarea" placeholder="Optional details…" value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select id="task-status" className="form-select" value={form.status}
                onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Priority</label>
              <select id="task-priority" className="form-select" value={form.priority}
                onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">Assignee</label>
              <select id="task-assignee" className="form-select" value={form.assignee_id || ''}
                onChange={e => setForm(f => ({ ...f, assignee_id: e.target.value }))}>
                <option value="">Unassigned</option>
                {members.map(m => (
                  <option key={m.user_id} value={m.user_id}>{m.full_name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Due Date</label>
              <input id="task-due" className="form-input" type="date" value={form.due_date || ''}
                onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))} />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button id="task-save-btn" type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : initial ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function AddMemberModal({ open, onClose, onAdd }) {
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('member')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try { await onAdd({ user_email: email, role }); onClose(); setEmail('') }
    catch (err) { setError(err.response?.data?.detail || 'Failed to add member.') }
    finally { setLoading(false) }
  }

  if (!open) return null
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 380 }}>
        <div className="modal-header">
          <h2 className="modal-title">Add Member</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        {error && <div className="error-banner" style={{ marginBottom: 16 }}>{error}</div>}
        <form className="modal-form" onSubmit={handle}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input id="member-email" className="form-input" type="email" placeholder="teammate@example.com"
              value={email} onChange={e => setEmail(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label className="form-label">Role</label>
            <select id="member-role" className="form-select" value={role} onChange={e => setRole(e.target.value)}>
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button id="add-member-submit" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding…' : 'Add Member'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function ProjectDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('board')
  const [taskModal, setTaskModal] = useState({ open: false, initial: null })
  const [memberModal, setMemberModal] = useState(false)

  const fetchAll = async () => {
    const [p, t] = await Promise.all([
      getProject(id),
      getTasks(id, { page_size: 100 }),
    ])
    setProject(p.data)
    setTasks(t.data.items)
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [id])

  const handleSaveTask = async (payload) => {
    if (taskModal.initial) {
      const res = await updateTask(taskModal.initial.id, payload)
      setTasks(ts => ts.map(t => t.id === res.data.id ? res.data : t))
    } else {
      const res = await createTask(id, payload)
      setTasks(ts => [...ts, res.data])
    }
  }

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Delete this task?')) return
    await deleteTask(taskId)
    setTasks(ts => ts.filter(t => t.id !== taskId))
  }

  const handleQuickStatus = async (task, newStatus) => {
    const res = await updateTask(task.id, { status: newStatus })
    setTasks(ts => ts.map(t => t.id === res.data.id ? res.data : t))
  }

  const handleAddMember = async (payload) => {
    await addMember(id, payload)
    const res = await getProject(id)
    setProject(res.data)
  }

  const isOverdue = (task) =>
    task.due_date && task.status !== 'done' && new Date(task.due_date) < new Date()

  if (loading) return <div className="loading-spinner"><div className="spinner" /></div>
  if (!project) return <p style={{ color: 'var(--accent-orange)' }}>Project not found</p>

  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    done: tasks.filter(t => t.status === 'done'),
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>
            <Link to="/projects" style={{ color: 'var(--text-muted)' }}>Projects</Link> › {project.name}
          </div>
          <h1 className="page-title">{project.name}</h1>
          {project.description && <p className="page-subtitle">{project.description}</p>}
        </div>
        <div className="flex gap-8">
          <button id="add-member-btn" className="btn btn-secondary" onClick={() => setMemberModal(true)}>
            👤 Add Member
          </button>
          <button id="add-task-btn" className="btn btn-primary" onClick={() => setTaskModal({ open: true, initial: null })}>
            <span>+</span> Add Task
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <div className={`tab ${tab === 'board' ? 'active' : ''}`} onClick={() => setTab('board')} id="tab-board">
          📋 Board
        </div>
        <div className={`tab ${tab === 'members' ? 'active' : ''}`} onClick={() => setTab('members')} id="tab-members">
          👥 Members ({project.members?.length || 0})
        </div>
      </div>

      {/* Board Tab */}
      {tab === 'board' && (
        <div className="kanban-board">
          {COLUMNS.map(col => (
            <div className="kanban-column" key={col.key} id={`col-${col.key}`}>
              <div className="kanban-column-header">
                <div className="kanban-column-title">
                  <div className="column-dot" style={{ background: col.dot }} />
                  {col.label}
                </div>
                <span className="kanban-column-count">{tasksByStatus[col.key].length}</span>
              </div>
              <div className="kanban-tasks">
                {tasksByStatus[col.key].length === 0 && (
                  <div style={{ textAlign: 'center', padding: '24px 12px', color: 'var(--text-muted)', fontSize: 13 }}>
                    No tasks here
                  </div>
                )}
                {tasksByStatus[col.key].map(task => (
                  <div
                    key={task.id}
                    className="task-card"
                    id={`task-${task.id}`}
                    onClick={() => setTaskModal({ open: true, initial: { ...task, due_date: task.due_date || '' } })}
                  >
                    <div className="task-card-title">{task.title}</div>
                    <div className="task-card-meta">
                      <span
                        className="badge"
                        style={{
                          background: `${PRIORITY_COLORS[task.priority]}20`,
                          color: PRIORITY_COLORS[task.priority],
                          border: `1px solid ${PRIORITY_COLORS[task.priority]}40`,
                        }}
                      >
                        {PRIORITY_LABELS[task.priority]}
                      </span>
                      {task.assignee && (
                        <span className="badge" style={{ background: 'var(--bg-glass)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
                          👤 {task.assignee.full_name.split(' ')[0]}
                        </span>
                      )}
                      {task.due_date && (
                        <span className={`badge ${isOverdue(task) ? 'badge-overdue' : ''}`}
                          style={!isOverdue(task) ? { background: 'var(--bg-glass)', color: 'var(--text-muted)', border: '1px solid var(--border)' } : {}}>
                          📅 {task.due_date}
                        </span>
                      )}
                    </div>
                    {/* Quick status buttons */}
                    <div className="flex gap-8 mt-8" onClick={e => e.stopPropagation()}>
                      {COLUMNS.filter(c => c.key !== col.key).map(c => (
                        <button
                          key={c.key}
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '3px 8px', fontSize: 11 }}
                          onClick={() => handleQuickStatus(task, c.key)}
                          id={`move-${task.id}-to-${c.key}`}
                        >
                          → {c.label}
                        </button>
                      ))}
                      <button
                        className="btn btn-danger btn-sm"
                        style={{ padding: '3px 8px', fontSize: 11, marginLeft: 'auto' }}
                        onClick={() => handleDeleteTask(task.id)}
                        id={`delete-task-${task.id}`}
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Members Tab */}
      {tab === 'members' && (
        <div className="card" style={{ maxWidth: 560 }}>
          <div className="flex justify-between items-center" style={{ marginBottom: 16 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700 }}>Team Members</h2>
            <button className="btn btn-primary btn-sm" onClick={() => setMemberModal(true)} id="members-add-btn">
              + Add
            </button>
          </div>
          <div className="members-list">
            {project.members?.map(m => (
              <div key={m.user_id} className="member-row" id={`member-${m.user_id}`}>
                <div className="member-avatar">{m.full_name.slice(0, 2).toUpperCase()}</div>
                <div className="member-info">
                  <div className="member-name">{m.full_name}</div>
                  <div className="member-email">{m.email}</div>
                </div>
                <span className={`badge ${m.role === 'admin' ? 'badge-in_progress' : 'badge-todo'}`}>
                  {m.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <TaskModal
        open={taskModal.open}
        initial={taskModal.initial}
        members={project.members || []}
        onClose={() => setTaskModal({ open: false, initial: null })}
        onSave={handleSaveTask}
      />
      <AddMemberModal
        open={memberModal}
        onClose={() => setMemberModal(false)}
        onAdd={handleAddMember}
      />
    </div>
  )
}
