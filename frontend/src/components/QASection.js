import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://notes-app-backend-service:8000';

const QASection = ({ loading, userId = "default" }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) {
      return;
    }

    try {
      setIsAsking(true);
      setError('');
      setAnswer('');
      setSources([]);

      const response = await axios.post(`${API_BASE_URL}/api/ask`, {
        question: question.trim(),
        user_id: userId
      });

      setAnswer(response.data.answer);
      setSources(response.data.sources || []);
    } catch (err) {
      setError('Failed to get answer. Please check if the backend server is running and you have an OpenAI API key configured.');
      console.error('Error asking question:', err);
    } finally {
      setIsAsking(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setAnswer('');
    setSources([]);
    setError('');
  };

  return (
    <div className="qa-section">
      <h2 className="section-title">Ask Questions</h2>
      
      <form className="qa-form" onSubmit={handleAsk}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your notes..."
          disabled={isAsking || loading}
        />
        <div className="button-group">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isAsking || loading || !question.trim()}
          >
            {isAsking ? 'Asking...' : 'Ask Question'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={isAsking || loading}
          >
            Clear
          </button>
        </div>
      </form>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {answer && (
        <div className="answer-section">
          <h4>Answer:</h4>
          <p>{answer}</p>
          
          {sources.length > 0 && (
            <div className="sources">
              <h5>Sources:</h5>
              <ul>
                {sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!answer && !error && (
        <div className="loading">
          Ask a question about your notes to get AI-powered answers!
        </div>
      )}
    </div>
  );
};

export default QASection;
