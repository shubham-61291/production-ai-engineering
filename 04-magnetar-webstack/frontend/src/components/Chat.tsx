import React, { useState } from 'react';

interface ChatProps {
  messages: { role: 'user' | 'assistant'; content: string }[];
  onSend: (question: string) => void;
  loading?: boolean;
}

const Chat: React.FC<ChatProps> = ({ messages, onSend, loading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-800/60 rounded-lg border border-gray-700">
        {messages.length === 0 && (
          <div className="text-gray-500 text-center mt-8 text-sm">
            Welcome to Magnetar AI Assistant. Ask a question or switch to RAG / Legal Audit.
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-2.5 rounded-lg text-sm leading-relaxed ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-100 border border-gray-600'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-blue-400 text-sm animate-pulse">DeepSeek-R1 is thinking...</div>}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 mt-4">
        <input
          type="text"
          className="flex-1 p-2.5 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:border-blue-500 text-sm"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="px-5 py-2.5 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
