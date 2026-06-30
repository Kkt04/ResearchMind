import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

export const getPapers = () => api.get('/papers/')
export const getPaper = (id) => api.get(`/papers/${id}`)
export const uploadPdf = (formData) =>
  api.post('/papers/upload-pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const addArxivPaper = (arxiv_id) => api.post('/papers/arxiv', { arxiv_id })
export const addTextPaper = (content, title) => api.post('/papers/text', { content, title })
export const deletePaper = (id) => api.delete(`/papers/${id}`)

export const queryPapers = (query, paper_ids, mode) =>
  api.post('/query/', { query, paper_ids, mode })
export const chatMessage = (message, history) =>
  api.post('/query/chat', { message, history })

export const submitFeedback = (paper_id, rating, feedback) =>
  api.post('/feedback/', { paper_id, rating, feedback })

export const generateReview = (title, focus_area, paper_ids) =>
  api.post('/generate/review', { title, focus_area, paper_ids })

export default api