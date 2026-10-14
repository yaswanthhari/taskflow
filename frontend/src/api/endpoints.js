import api from './client'

// Auth
export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)

// Projects
export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)
export const getProject = (id) => api.get(`/projects/${id}`)
export const updateProject = (id, data) => api.put(`/projects/${id}`, data)
export const deleteProject = (id) => api.delete(`/projects/${id}`)
export const addMember = (projectId, data) => api.post(`/projects/${projectId}/members`, data)
export const removeMember = (projectId, userId) => api.delete(`/projects/${projectId}/members/${userId}`)

// Tasks
export const getTasks = (projectId, params) => api.get(`/projects/${projectId}/tasks`, { params })
export const createTask = (projectId, data) => api.post(`/projects/${projectId}/tasks`, data)
export const getTask = (id) => api.get(`/tasks/${id}`)
export const updateTask = (id, data) => api.put(`/tasks/${id}`, data)
export const deleteTask = (id) => api.delete(`/tasks/${id}`)

// Dashboard
export const getDashboard = () => api.get('/dashboard')
