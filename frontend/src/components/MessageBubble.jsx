export default function MessageBubble({ role, content, sources }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
          isUser ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-800'
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>

        {sources?.length > 0 && (
          <details className="mt-2 text-xs text-slate-500">
            <summary className="cursor-pointer select-none">
              {sources.length} source{sources.length > 1 ? 's' : ''}
            </summary>
            <ul className="mt-1 space-y-1">
              {sources.map((s, i) => (
                <li key={i} className="border-l-2 border-slate-300 pl-2">
                  <span className="font-medium">
                    {s.source} (chunk {s.chunk_index})
                  </span>
                  {s.similarity_score != null && (
                    <span className="ml-1 text-slate-400">
                      score {s.similarity_score}
                    </span>
                  )}
                  <div className="italic">"{s.excerpt}"</div>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  )
}
