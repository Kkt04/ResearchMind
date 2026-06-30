import { useState } from 'react'
import { X, Star, Loader2 } from 'lucide-react'
import Button from '../ui/Button.jsx'
import { submitFeedback } from '../../lib/api.js'

export default function RateModal({ paper, initialRating, onClose, onRated }) {
  const [rating, setRating] = useState(initialRating || 0)
  const [feedback, setFeedback] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!rating) return
    setLoading(true)
    try {
      await submitFeedback(paper.id, rating, feedback || 'No additional comments')
      onRated(paper.id, rating, feedback)
      onClose()
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl float-up">
        <div className="flex items-center justify-between px-6 py-5 border-b border-ink/8">
          <h2 className="font-display text-lg">Rate this paper</h2>
          <button onClick={onClose} className="text-ink/40 hover:text-ink"><X size={20} /></button>
        </div>

        <div className="px-6 py-5 space-y-4">
          <p className="text-sm text-ink/60 line-clamp-2">{paper?.title}</p>

          <div className="flex gap-1.5 justify-center py-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button key={n} onClick={() => setRating(n)}>
                <Star size={28} className={n <= rating ? 'fill-graph-500 text-graph-500' : 'text-ink/15'} />
              </button>
            ))}
          </div>

          <div>
            <label className="text-xs font-medium text-ink/60 mb-1.5 block">
              Why? (this updates the paper's weight in the knowledge graph)
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={3}
              placeholder="e.g. Strong methodology but small sample size..."
              className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40 resize-none"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 px-6 py-4 border-t border-ink/8">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading || !rating}>
            {loading ? <Loader2 size={15} className="animate-spin" /> : null}
            Save rating
          </Button>
        </div>
      </div>
    </div>
  )
}