export default function Card({ children, className = '', ...props }) {
    return (
      <div className={`bg-white border border-ink/8 rounded-2xl shadow-sm ${className}`} {...props}>
        {children}
      </div>
    )
  }