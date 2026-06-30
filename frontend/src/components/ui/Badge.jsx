export default function Badge({ children, tone = 'graph', className = '' }) {
    const tones = {
      graph: 'bg-graph-50 text-graph-600',
      moss: 'bg-moss-400/10 text-moss-500',
      rust: 'bg-rust-400/10 text-rust-500',
      neutral: 'bg-ink/5 text-ink/50',
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-mono font-medium ${tones[tone]} ${className}`}>
        {children}
      </span>
    )
  }