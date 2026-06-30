import { Star, Trash2, ExternalLink, Loader2 } from 'lucide-react'
import Card from '../ui/Card.jsx'
import Badge from '../ui/Badge.jsx'

export default function PaperCard({ paper, onDelete, onRate, onClick }) {
  const statusTone = paper.status === 'ready' ? 'moss' : paper.status === 'failed' ? 'rust' : 'graph'

  return (
    <Card className="p-5 hover:shadow-md transition-shadow cursor-pointer group float-up" onClick={onClick}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <Badge tone={statusTone}>
          {paper.status === 'processing' && <Loader2 size={11} className="animate-spin mr-1" />}
          {paper.status}
        </Badge>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(paper.id) }}
          className="opacity-0 group-hover:opacity-100 text-ink/30 hover:text-rust-500 transition-all"
          title="Remove from graph (forget)"
        >
          <Trash2 size={15} />
        </button>
      </div>

      <h3 className="font-display text-base text-ink leading-snug mb-1.5 line-clamp-2">
        {paper.title}
      </h3>

      {paper.authors && (
        <p className="text-xs text-ink/45 mb-3 font-mono">
          {paper.authors} {paper.year && `· ${paper.year}`}
        </p>
      )}

      {paper.abstract && (
        <p className="text-sm text-ink/60 line-clamp-2 mb-4 leading-relaxed">
          {paper.abstract}
        </p>
      )}

      <div className="flex items-center justify-between pt-3 border-t border-ink/5">
        <div className="flex items-center gap-0.5">
          {[1, 2, 3, 4, 5].map((n) => (
            <button key={n} onClick={(e) => { e.stopPropagation(); onRate(paper, n) }} className="transition-colors">
              <Star size={13} className={n <= (paper.rating || 0) ? 'fill-graph-500 text-graph-500' : 'text-ink/15'} />
            </button>
          ))}
        </div>
        {paper.source_url && (
          <a href={paper.source_url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} className="text-ink/30 hover:text-graph-500 transition-colors">
            <ExternalLink size={13} />
          </a>
        )}
      </div>
    </Card>
  )
}