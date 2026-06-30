export default function EmptyState({ icon: Icon, title, description, action }) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-20 px-6">
        {Icon && (
          <div className="w-14 h-14 rounded-2xl bg-graph-50 flex items-center justify-center mb-5">
            <Icon size={24} className="text-graph-500" />
          </div>
        )}
        <h3 className="font-display text-xl text-ink mb-2">{title}</h3>
        <p className="text-sm text-ink/50 max-w-sm mb-6">{description}</p>
        {action}
      </div>
    )
  }