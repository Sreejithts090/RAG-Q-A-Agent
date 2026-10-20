import { useRef, useState } from 'react'
import { uploadDocument } from '../api/client'

export default function FileUpload({ onUploaded }) {
  const inputRef = useRef(null)
  const [status, setStatus] = useState(null) // { type: 'success'|'error'|'loading', message }

  async function handleFile(file) {
    if (!file) return
    setStatus({ type: 'loading', message: `Indexing ${file.name}...` })
    try {
      const result = await uploadDocument(file)
      setStatus({ type: 'success', message: result.message })
      onUploaded?.(result)
    } catch (err) {
      setStatus({ type: 'error', message: err.message })
    }
  }

  return (
    <div className="border border-dashed border-slate-300 rounded-lg p-4 text-center">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.docx"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <button
        onClick={() => inputRef.current?.click()}
        className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-700 transition"
      >
        Upload document (PDF / TXT / DOCX)
      </button>
      {status && (
        <p
          className={`mt-2 text-sm ${
            status.type === 'error'
              ? 'text-red-600'
              : status.type === 'success'
              ? 'text-green-600'
              : 'text-slate-500'
          }`}
        >
          {status.message}
        </p>
      )}
    </div>
  )
}
