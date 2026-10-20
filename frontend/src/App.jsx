import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [lastUpload, setLastUpload] = useState(null)

  return (
    <div className="min-h-screen bg-slate-50 flex items-start justify-center py-10 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <header>
          <h1 className="text-2xl font-semibold text-slate-900">RAG Q&A Agent</h1>
          <p className="text-sm text-slate-500">
            Retrieval-Augmented Generation over your own documents — fully local, no API keys.
          </p>
        </header>

        <FileUpload onUploaded={setLastUpload} />
        <ChatWindow key={lastUpload?.filename} />
      </div>
    </div>
  )
}
