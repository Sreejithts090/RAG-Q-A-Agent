import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import { askQuestion } from '../api/client'

export default function ChatWindow() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const question = input.trim()
    if (!question || loading) return

    setMessages((m) => [...m, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const { answer, sources } = await askQuestion(question)
      setMessages((m) => [...m, { role: 'assistant', content: answer, sources }])
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `Error: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[60vh] border border-slate-200 rounded-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-slate-400 text-center mt-10">
            Upload a document above, then ask a question about it.
          </p>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} sources={m.sources} />
        ))}
        {loading && (
          <p className="text-sm text-slate-400">Thinking...</p>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-slate-200 p-3 flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask a question about your documents..."
          className="flex-1 resize-none rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-700 disabled:opacity-50 transition"
        >
          Send
        </button>
      </div>
    </div>
  )
}
