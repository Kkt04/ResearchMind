import { useEffect, useState } from 'react'
import { Plus, Network, Library } from 'lucide-react'
import Button from '../components/ui/Button.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import PaperCard from '../components/features/PaperCard.jsx'
import AddPaperModal from '../components/features/AddPaperModal.jsx'
import RateModal from '../components/features/RateModal.jsx'
import { getPapers, deletePaper } from '../lib/api.js'

export default function Dashboard() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [ratingPaper, setRatingPaper] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await getPapers()
      setPapers(res.data.papers || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id) => {
    if (!confirm('Remove this paper from the knowledge graph? This calls Cognee forget().')) return
    setPapers((prev) => prev.filter((p) => p.id !== id))
    try {
      await deletePaper(id)
    } catch (err) {
      console.error(err)
      load()
    }
  }

  const handleRated = (id, rating, feedback) => {
    setPapers((prev) => prev.map((p) => (p.id === id ? { ...p, rating, feedback } : p)))
  }

  return (
    <div className="max-w-6xl mx-auto px-8 py-10">
      <header className="flex items-start justify-between mb-10">
        <div>
          <div className="flex items-center gap-2 text-graph-500 mb-2">
            <Network size={16} />
            <span className="text-xs font-mono font-medium uppercase tracking-wide">Knowledge Graph</span>
          </div>
          <h1 className="font-display text-3xl text-ink">Your research memory</h1>
          <p className="text-ink/50 mt-1.5 text-sm">
            {papers.length} paper{papers.length !== 1 ? 's' : ''} ingested · persistent across every session
          </p>
        </div>
        <Button onClick={() => setShowAdd(true)}>
          <Plus size={16} /> Add paper
        </Button>
      </header>

      {loading ? (
        <div className="flex justify-center py-24"><Spinner size={28} className="text-graph-400" /></div>
      ) : papers.length === 0 ? (
        <EmptyState
          icon={Library}
          title="No papers yet"
          description="Add your first paper — via arXiv ID, PDF upload, or pasted text — and watch ResearchMind build a living knowledge graph from it."
          action={<Button onClick={() => setShowAdd(true)}><Plus size={16} /> Add your first paper</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {papers.map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              onDelete={handleDelete}
              onRate={(p) => setRatingPaper(p)}
              onClick={() => {}}
            />
          ))}
        </div>
      )}

      {showAdd && (
        <AddPaperModal onClose={() => setShowAdd(false)} onAdded={(paper) => setPapers((prev) => [paper, ...prev])} />
      )}

      {ratingPaper && (
        <RateModal paper={ratingPaper} initialRating={ratingPaper.rating} onClose={() => setRatingPaper(null)} onRated={handleRated} />
      )}
    </div>
  )
}