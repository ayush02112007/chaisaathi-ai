import { useState, useRef, useEffect } from 'react'
import { chatAssistant } from '../api'
import { Mic, MicOff, Send, Volume2, VolumeX, Bot } from 'lucide-react'

function detectLanguage(text) {
  // Check for Devanagari script (Hindi)
  return /[\u0900-\u097F]/.test(text) ? 'hi' : 'en'
}

export default function Assistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Namaste! Main ChaiSaathi AI hoon. Aapka dukan assistant. Aap Hindi ya English mein baat kar sakte hain. Kya jaanna chahte hain? 🙏' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(true)
  const bottomRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const speak = (text, lang) => {
    if (!ttsEnabled) return
    window.speechSynthesis.cancel()
    const utter = new SpeechSynthesisUtterance(text)
    utter.lang = lang === 'hi' ? 'hi-IN' : 'en-IN'
    utter.rate = 0.9
    window.speechSynthesis.speak(utter)
  }

  const send = async (text) => {
    if (!text.trim()) return
    const lang = detectLanguage(text)
    setMessages(m => [...m, { role: 'user', text }])
    setInput('')
    setLoading(true)
    try {
      const r = await chatAssistant(text, lang)
      const reply = r.data.response
      setMessages(m => [...m, { role: 'assistant', text: reply }])
      speak(reply, lang)
    } catch {
      setMessages(m => [...m, { role: 'assistant', text: 'Sorry, kuch galat ho gaya. Backend se connect nahi ho paa raha.' }])
    } finally {
      setLoading(false)
    }
  }

  const startVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Voice recognition not supported in this browser. Use Chrome.')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang = 'hi-IN'
    recognition.interimResults = false
    recognition.continuous = false

    recognition.onstart = () => setListening(true)
    recognition.onend = () => setListening(false)
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      setInput(transcript)
      send(transcript)
    }
    recognition.onerror = () => setListening(false)

    recognitionRef.current = recognition
    recognition.start()
  }

  const stopVoice = () => {
    recognitionRef.current?.stop()
    setListening(false)
  }

  const quickPrompts = [
    'Aaj kitni kamai hui?',
    'Kitna udhaar pending hai?',
    'Low stock items kaunse hain?',
    'Is month ka profit kitna hai?',
  ]

  return (
    <div className="p-6 h-[calc(100vh-2rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl chai-gradient flex items-center justify-center text-white">
            <Bot size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">ChaiSaathi AI</h1>
            <p className="text-xs text-gray-400">Hindi & English voice assistant</p>
          </div>
        </div>
        <button
          onClick={() => setTtsEnabled(t => !t)}
          className={`p-2 rounded-lg border ${ttsEnabled ? 'bg-orange-50 border-orange-200 text-orange-600' : 'bg-gray-100 border-gray-200 text-gray-400'}`}
          title={ttsEnabled ? 'Mute voice' : 'Enable voice'}
        >
          {ttsEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
      </div>

      {/* Chat */}
      <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm overflow-y-auto p-4 space-y-3 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-orange-500 text-white rounded-br-sm'
                : 'bg-gray-100 text-gray-800 rounded-bl-sm'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <span key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick prompts */}
      <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
        {quickPrompts.map(q => (
          <button key={q} onClick={() => send(q)}
            className="whitespace-nowrap text-xs bg-orange-50 text-orange-600 px-3 py-1.5 rounded-full hover:bg-orange-100 border border-orange-200 shrink-0">
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
          placeholder="Hindi ya English mein likhe..."
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-orange-300 focus:outline-none"
        />
        <button
          onClick={listening ? stopVoice : startVoice}
          className={`relative p-3 rounded-xl transition-colors ${listening ? 'bg-red-500 text-white' : 'bg-orange-100 text-orange-600 hover:bg-orange-200'}`}
          title={listening ? 'Stop' : 'Speak'}
        >
          {listening ? <MicOff size={20} /> : <Mic size={20} />}
          {listening && <span className="voice-pulse absolute inset-0 rounded-xl" />}
        </button>
        <button
          onClick={() => send(input)}
          disabled={!input.trim() || loading}
          className="p-3 rounded-xl bg-orange-500 text-white hover:bg-orange-600 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  )
}
