import { NavLink } from 'react-router-dom'
import { Network, MessageCircleQuestion, FileText, Brain } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Knowledge Graph', icon: Network, end: true },
  { to: '/query', label: 'Ask Research', icon: MessageCircleQuestion },
  { to: '/review', label: 'Generate Review', icon: FileText },
]

export default function Sidebar() {
  return (
    <aside className="w-64 fixed inset-y-0 left-0 bg-ink text-paper flex flex-col border-r border-white/5">
      <div className="px-6 py-7 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-graph-500 flex items-center justify-center">
            <Brain size={18} className="text-white" />
          </div>
          <span className="font-display text-lg tracking-tight">ResearchMind</span>
        </div>
        <p className="text-xs text-white/40 mt-2 font-mono">never forgets a paper</p>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-1">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-graph-500/20 text-graph-100 font-medium'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-5 border-t border-white/5">
        <p className="text-[11px] text-white/30 leading-relaxed">
          Powered by Cognee<br/>
          <span className="font-mono">remember · recall · improve · forget</span>
        </p>
      </div>
    </aside>
  )
}