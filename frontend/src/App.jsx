import React, { useState } from 'react';
import { Upload, MessageSquare, Send, FileText, Bot, User, CheckCircle } from 'lucide-react';
import './App.css';

function App() {
  const [userId] = useState('user_bohdan_123');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Hello! Upload a document, and I will help you analyze it or extract information.' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatusMessage('');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setStatusMessage('AI is analyzing the document...');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/upload', { method: 'POST', body: formData });
      if (!response.ok) throw new Error('Failed to process document');
      const data = await response.json();
      setExtractedData(data.extracted_data);
      setStatusMessage('Document processed and vectorized successfully!');
      setChatHistory(prev => [...prev, { role: 'assistant', text: `Successfully processed "${data.filename}". You can now ask me any questions!` }]);
    } catch (error) {
      console.error(error);
      setStatusMessage('Error: Failed to process document.');
    } finally { setLoading(false); }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!question.trim() || chatLoading) return;
    const userMessage = question;
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setQuestion('');
    setChatLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, question: userMessage })
      });
      if (!response.ok) throw new Error('Failed to get AI response');
      const data = await response.json();
      setChatHistory(prev => [...prev, { role: 'assistant', text: data.response }]);
    } catch (error) {
      console.error(error);
      setChatHistory(prev => [...prev, { role: 'assistant', text: 'Error: Could not connect to AI service.' }]);
    } finally { setChatLoading(false); }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Smart-Doc <span className="highlight">AI</span></h1>
        <p className="subtitle">Interactive Multi-Tenant RAG Platform & Data Extractor</p>
      </header>
      <div className="main-layout">
        <div className="left-panel">
          <div className="card">
            <h2><Upload size={20} /> Upload Document (.txt, .pdf)</h2>
            <form onSubmit={handleUpload} className="upload-form">
              <input type="file" accept=".txt,.pdf" onChange={handleFileChange} id="file-upload" hidden />
              <label htmlFor="file-upload" className={`file-label ${file ? 'selected' : ''}`}>
                <FileText size={32} />
                <span>{file ? file.name : 'Click to select a file'}</span>
              </label>
              <button type="submit" disabled={!file || loading} className="btn-primary">
                {loading ? 'Processing...' : 'Analyze with AI'}
              </button>
            </form>
            {statusMessage && <p className="status-text">{statusMessage}</p>}
          </div>
          {extractedData && (
            <div className="card data-card animate-fade-in">
              <h2><CheckCircle size={20} color="#10B981" /> AI Extracted Data (JSON Mode)</h2>
              <table className="data-table">
                <tbody>
                  <tr><td><strong>Document Type:</strong></td><td><span className="badge">{extractedData.document_type}</span></td></tr>
                  <tr><td><strong>Client / Actor:</strong></td><td>{extractedData.client_name}</td></tr>
                  <tr><td><strong>Key Date:</strong></td><td>{extractedData.date}</td></tr>
                  <tr><td><strong>Total Amount:</strong></td><td>${extractedData.total_amount.toFixed(2)}</td></tr>
                  <tr><td><strong>Brief Summary:</strong></td><td>{extractedData.summary}</td></tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
        <div className="right-panel">
          <div className="card chat-card">
            <h2><MessageSquare size={20} /> Contextual Document Chat (RAG)</h2>
            <div className="chat-messages">
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message-wrapper ${msg.role}`}>
                  <div className="avatar">{msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}</div>
                  <div className="message-text">{msg.text}</div>
                </div>
              ))}
              {chatLoading && (
                <div className="message-wrapper assistant loading">
                  <div className="avatar"><Bot size={16} /></div>
                  <div className="message-text">AI is thinking...</div>
                </div>
              )}
            </div>
            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input type="text" placeholder="Ask a question about your document..." value={question} onChange={(e) => setQuestion(e.target.value)} disabled={chatLoading} />
              <button type="submit" disabled={!question.trim() || chatLoading}><Send size={18} /></button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;