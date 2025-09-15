import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://notes-app-backend-service:8000';

const ConversationHistory = ({ userId = "default" }) => {
  const [conversations, setConversations] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/conversations/${userId}`);
      setConversations(response.data.conversations || []);
      setStats(response.data.stats || {});
      setError('');
    } catch (err) {
      setError('Failed to load conversation history');
      console.error('Error loading conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearConversations = async () => {
    if (!window.confirm('Are you sure you want to clear all conversation history?')) {
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/api/conversations/${userId}/clear`);
      setConversations([]);
      setStats({});
      setError('');
    } catch (err) {
      setError('Failed to clear conversations');
      console.error('Error clearing conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [userId]);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading && conversations.length === 0) {
    return (
      <div className="conversation-history">
        <div className="loading">Loading conversation history...</div>
      </div>
    );
  }

  return (
    <div className="conversation-history">
      <div className="conversation-header">
        <h3>Conversation History</h3>
        <div className="conversation-stats">
          <span>Messages: {stats.total_messages || 0}</span>
          <span>Conversations: {stats.conversations || 0}</span>
          {stats.last_activity && (
            <span>Last: {formatTimestamp(stats.last_activity)}</span>
          )}
        </div>
        <button 
          className="btn btn-danger btn-sm"
          onClick={clearConversations}
          disabled={loading || conversations.length === 0}
        >
          Clear History
        </button>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {conversations.length === 0 ? (
        <div className="no-conversations">
          No conversation history yet. Start asking questions!
        </div>
      ) : (
        <div className="conversation-list">
          {conversations.slice(-10).reverse().map((conv, index) => (
            <div key={index} className={`conversation-item ${conv.is_user ? 'user' : 'assistant'}`}>
              <div className="conversation-meta">
                <span className="conversation-role">
                  {conv.is_user ? 'You' : 'Assistant'}
                </span>
                <span className="conversation-time">
                  {formatTimestamp(conv.timestamp)}
                </span>
              </div>
              <div className="conversation-content">
                {conv.message}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;
