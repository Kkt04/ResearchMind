import { useState } from 'react'
import { FileText, Sparkles, Loader2, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import Button from '../components/ui/Button.jsx'
import Card from '../components/ui/Card.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import { generateReview } from '../lib/api.js'

export default function Review() {
  const [title, setTitle] = useState('Literature Review')
  const [focusArea, setFocusArea] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await generateReview(title, focusArea)
      setResult(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const downloadMarkdown = () => {
    if (!result) return
    const md = `# ${result.title}\n\n` + result.sections.map(s => `## ${s.heading}\n\n${s.content}`).join('\n\n')
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.title.replace(/\s+/g, '_')}.md`
    a.click()
  }

  return (
    <div className="max-w-3xl mx-auto px-8 py-10">
      <header className="mb-8">
        <div className="flex items-center gap-2 text-graph-500 mb-2">
          <FileText size={16} />
          <span className="text-xs font-mono font-medium uppercase tracking-wide">Synthesis across the graph</span>
        </div>
        <h1 className="font-display text-3xl text-ink">Generate a literature review</h1>
        <p className="text-ink/50 mt-1.5 text-sm">
          ResearchMind traverses every paper in your knowledge graph and drafts a structured academic review.
        </p>
      </header>

      <Card className="p-6 mb-8">
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-ink/60 mb-1.5 block">Review title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-ink/60 mb-1.5 block">Focus area (optional)</label>
            <input
              value={focusArea}
              onChange={(e) => setFocusArea(e.target.value)}
              placeholder="e.g. passive speech-based depression detection"
              className="w-full px-3.5 py-2.5 text-sm border border-ink/12 rounded-lg focus:outline-none focus:ring-2 focus:ring-graph-400/40"
            />
          </div>
          <Button onClick={handleGenerate} disabled={loading} className="w-full">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            {loading ? 'Synthesizing from knowledge graph...' : 'Generate review'}
          </Button>
        </div>
      </Card>

      {!result && !loading && (
        <EmptyState
          icon={FileText}
          title="No review generated yet"
          description="Generate a structured draft synthesizing methodology, findings, and gaps across every paper you've added."
        />
      )}

      {result && (
        <div className="float-up">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="font-display text-2xl text-ink">{result.title}</h2>
              <p className="text-xs text-ink/40 font-mono mt-1">Synthesized from {result.total_papers} papers</p>
            </div>
            <Button variant="secondary" size="sm" onClick={downloadMarkdown}>
              <Download size={14} /> Export .md
            </Button>
          </div>

          <div className="space-y-6">
            {result.sections.map((section, i) => (
              <Card key={i} className="p-6">
                <h3 className="font-display text-lg text-graph-600 mb-3">{section.heading}</h3>
                <div className="prose prose-sm max-w-none text-ink/75 leading-relaxed prose-strong:text-ink">
                  <ReactMarkdown>{section.content}</ReactMarkdown>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}