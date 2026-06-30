export default function Button({ children, variant = 'primary', size = 'md', className = '', ...props }) {
    const base = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
    const variants = {
      primary: 'bg-graph-500 text-white hover:bg-graph-600',
      secondary: 'bg-graph-50 text-graph-600 hover:bg-graph-100',
      ghost: 'text-ink/60 hover:bg-ink/5 hover:text-ink',
      danger: 'bg-rust-500/10 text-rust-500 hover:bg-rust-500/20',
    }
    const sizes = {
      sm: 'text-xs px-3 py-1.5',
      md: 'text-sm px-4 py-2.5',
      lg: 'text-base px-6 py-3',
    }
    return (
      <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
        {children}
      </button>
    )
  }