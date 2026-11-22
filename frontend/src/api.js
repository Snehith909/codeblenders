const BASE = '/api'
const DEFAULT_ERROR = 'Something went wrong. Please try again.'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  if (!res.ok) {
    let body = {}
    try {
      body = await res.json()
    } catch {
      // body is not JSON; use the default message
    }
    throw new Error(body.message || DEFAULT_ERROR)
  }
  return res.status === 204 ? null : res.json()
}

export const getSchemes = () => request('/schemes')

export const getScheme = (id) => request(`/schemes/${encodeURIComponent(id)}`)

export const extract = (text) =>
  request('/extract', { method: 'POST', body: JSON.stringify({ text }) })

export const match = (profile) =>
  request('/match', { method: 'POST', body: JSON.stringify({ profile }) })

export const listApplications = () => request('/applications')

export const createApplication = (schemeId) =>
  request('/applications', {
    method: 'POST',
    body: JSON.stringify({ scheme_id: schemeId }),
  })

export const updateApplication = (id, body) =>
  request(`/applications/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })

export const getReminders = () => request('/reminders')
