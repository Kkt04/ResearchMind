import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, MessageCircleQuestion } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'
import { chatMessage } from '../lib/api.js'

const SUGGESTIONS = [
  'Which papers use transformer-based models?',
  'What are the common research gaps?',
  'Compare datasets used across all papers',
  'Summarize key findings on accuracy',
]

export default function Query() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const q = text || input
    if (!q.trim() || loading) return

    const userMsg = { role: 'user', content: q }
    const newHistory = [...messages, userMsg]
    setMessages(newHistory)
    setInput('')
    setLoading(true)

    try {
      const res = await chatMessage(q, newHistory.map(m => ({ role: m.role, content: m.content })))
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.response, sources: res.data.sources_used }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Something went wrong querying the knowledge graph. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-8 py-10 flex flex-col h-screen">
      <header className="mb-6">
        <div className="flex items-center gap-2 text-graph-500 mb-2">
          <MessageCircleQuestion size={16} />
          <span className="text-xs font-mono font-medium uppercase tracking-wide">Cognee recall()</span>
        </div>
        <h1 className="font-display text-3xl text-ink">Ask your research</h1>
        <p className="text-ink/50 mt-1.5 text-sm">Queries traverse the entire knowledge graph — across every paper, every session.</p>
      </header>

      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-5 pb-4">
        {messages.length === 0 && (
          <div className="pt-6">
            <p className="text-xs font-medium text-ink/40 mb-3">Try asking</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)} className="text-left text-sm px-4 py-3 rounded-xl border border-ink/8 hover:border-graph-300 hover:bg-graph-50/50 transition-colors text-ink/70">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} float-up`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${m.role === 'user' ? 'bg-graph-500 text-white' : 'bg-white border border-ink/8'}`}>
              {m.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none text-ink/80 prose-headings:text-ink prose-strong:text-ink">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm">{m.content}</p>
              )}
              {m.sources?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-ink/8">
                  {m.sources.map((s, idx) => (
                    <Badge key={idx} tone="graph">{s.slice(0, 30)}{s.length > 30 ? '...' : ''}</Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-ink/8 rounded-2xl px-4 py-3 flex items-center gap-2 text-ink/50 text-sm">
              <Loader2 size={14} className="animate-spin" /> Traversing knowledge graph...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-ink/8 pt-4">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask anything across your papers..."
            className="flex-1 px-4 py-3 text-sm border border-ink/12 rounded-xl focus:outline-none focus:ring-2 focus:ring-graph-400/40"
          />
          <Button onClick={() => send()} disabled={loading || !input.trim()}>
            <Send size={16} />
          </Button>
        </div>
      </div>
    </div>
  )
}