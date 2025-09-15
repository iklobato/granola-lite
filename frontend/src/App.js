import React, { useState, useEffect } from 'react';
import axios from 'axios';
import VoiceRecorder from './components/VoiceRecorder';
import NoteForm from './components/NoteForm';
import NotesList from './components/NotesList';
import QASection from './components/QASection';
import ConversationHistory from './components/ConversationHistory';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://notes-app-backend-service:8000';

function App() {
  const [notes, setNotes] = useState([]);
  const [editingNote, setEditingNote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load notes on component mount
  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/notes`);
      setNotes(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load notes. Please check if the backend server is running.');
      console.error('Error loading notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNoteSave = async (noteData) => {
    try {
      setLoading(true);
      if (editingNote) {
        // Update existing note
        const response = await axios.put(`${API_BASE_URL}/api/notes/${editingNote.id}`, noteData);
        setNotes(notes.map(note => 
          note.id === editingNote.id ? response.data : note
        ));
        setEditingNote(null);
      } else {
        // Create new note
        const response = await axios.post(`${API_BASE_URL}/api/notes`, noteData);
        setNotes([response.data, ...notes]);
      }
      setError('');
    } catch (err) {
      setError('Failed to save note. Please try again.');
      console.error('Error saving note:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNoteEdit = (note) => {
    setEditingNote(note);
  };

  const handleNoteDelete = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      setLoading(true);
      await axios.delete(`${API_BASE_URL}/api/notes/${noteId}`);
      setNotes(notes.filter(note => note.id !== noteId));
      setError('');
    } catch (err) {
      setError('Failed to delete note. Please try again.');
      console.error('Error deleting note:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceTranscription = (transcript) => {
    if (editingNote) {
      // Add to existing note content
      setEditingNote({
        ...editingNote,
        content: editingNote.content + ' ' + transcript
      });
    } else {
      // Create new note with transcribed text
      setEditingNote({
        title: 'Voice Note',
        content: transcript
      });
    }
  };

  const handleCancelEdit = () => {
    setEditingNote(null);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Notes App</h1>
        <p>Create, edit, and search your notes with voice dictation and AI-powered Q&A</p>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <div className="notes-grid">
        <div className="notes-section">
          <h2 className="section-title">Notes</h2>
          
          <NoteForm
            note={editingNote}
            onSave={handleNoteSave}
            onCancel={handleCancelEdit}
            loading={loading}
          />

          <VoiceRecorder onTranscription={handleVoiceTranscription} />

          <NotesList
            notes={notes}
            onEdit={handleNoteEdit}
            onDelete={handleNoteDelete}
            loading={loading}
          />
        </div>

        <div className="qa-section">
          <QASection loading={loading} userId="default" />
          <ConversationHistory userId="default" />
        </div>
      </div>
    </div>
  );
}

export default App;
