import { useState } from 'react'
import { X, Upload, Link2, FileType, Loader2 } from 'lucide-react'
import Button from '../ui/Button.jsx'
import { uploadPdf, addArxivPaper, addTextPaper } from '../../lib/api.js'

export default function AddPaperModal({ onClose, onAdded }) {
  const [tab, setTab] = useState('arxiv')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [arxivId, setArxivId] = useState('')
  const [textTitle, setTextTitle] = useState('')
  const [textContent, setTextContent] = useState('')
  const [file, setFile] = useState(null)

  const handleSubmit = async () => {
    setLoading(true)
    setError('')
    try {
      let res
      if (tab === 'arxiv') {
        if (!arxivId.trim()) throw new Error('Enter an arXiv ID')
        res = await addArxivPaper(arxivId.trim())
      } else if (tab === 'text') {
        if (!textContent.trim()) throw new Error('Paste paper content or abstract')
        res = await addTextPaper(textContent, textTitle)
      } else if (tab === 'pdf') {
        if (!file) throw new Error('Choose a PDF file')
        const formData = new FormData()
        formData.append('file', file)
        res = await uploadPdf(formData)
      }
      onAdded(res.data)
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-xl float-up">
        <div className="flex items-center justify-between px-6 py-5 border-b border-ink/8">
          <h2 className="font-display text-lg">Add a paper to memory</h2>
          <button onClick={onClose} className="text-ink/40 hover:text-ink">
            <X size={20} />
          </button>
        </div>

        <div className="flex gap-1 px-6 pt-4">
          {[
            { id: 'arxiv', label: 'arXiv', icon: Link2 },
            { id: 'pdf', label: 'Upload PDF', icon: Upload },
            { id: 'text', label: 'Paste text', icon: FileType },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                tab === id ? 'bg-graph-50 text-graph-600' : 'text-ink/50 hover:bg-ink/5'
              }`}
            >
              <Icon size={13} /> {label}
            </button>
          ))}
        </div>

        <div className="px-6 py-5 space-y-4">
          {tab === 'arxiv' && (
            <div>
              <label className="text-xs font-medium text-ink/60 mb-1.5 block">arXiv ID or URL</label>
              <input
                value={arxivId}
                onChange={(e) => setArxivId(e.target.value)}
                placeholder="e.g. 2301.07041"
                className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40"
              />
              <p className="text-xs text-ink/35 mt-1.5">We'll fetch the title, authors, and abstract automatically.</p>
            </div>
          )}

          {tab === 'pdf' && (
            <div>
              <label className="text-xs font-medium text-ink/60 mb-1.5 block">PDF file</label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full text-sm file:mr-3 file:px-3 file:py-2 file:rounded-lg file:border-0 file:bg-graph-50 file:text-graph-600 file:text-xs file:font-medium"
              />
            </div>
          )}

          {tab === 'text' && (
            <>
              <div>
                <label className="text-xs font-medium text-ink/60 mb-1.5 block">Title (optional)</label>
                <input
                  value={textTitle}
                  onChange={(e) => setTextTitle(e.target.value)}
                  placeholder="Paper title"
                  className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-ink/60 mb-1.5 block">Abstract or content</label>
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  rows={5}
                  placeholder="Paste the abstract or full text..."
                  className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40 resize-none"
                />
              </div>
            </>
          )}

          {error && <p className="text-xs text-rust-500 bg-rust-400/5 px-3 py-2 rounded-lg">{error}</p>}
        </div>

        <div className="flex justify-end gap-2 px-6 py-4 border-t border-ink/8">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? <Loader2 size={15} className="animate-spin" /> : null}
            {loading ? 'Ingesting into graph...' : 'Add to memory'}
          </Button>
        </div>
      </div>
    </div>
  )
}