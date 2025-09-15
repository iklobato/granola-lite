import React from 'react';

const NotesList = ({ notes, onEdit, onDelete, loading }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading && notes.length === 0) {
    return (
      <div className="loading">
        Loading notes...
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="notes-list">
        <p>No notes yet. Create your first note above!</p>
      </div>
    );
  }

  return (
    <div className="notes-list">
      {notes.map(note => (
        <div key={note.id} className="note-item">
          <h3>{note.title}</h3>
          <div className="note-meta">
            Created: {formatDate(note.created_at)}
            {note.updated_at !== note.created_at && (
              <span> • Updated: {formatDate(note.updated_at)}</span>
            )}
          </div>
          <p>{note.content}</p>
          <div className="note-actions">
            <button
              className="btn btn-primary"
              onClick={() => onEdit(note)}
              disabled={loading}
            >
              Edit
            </button>
            <button
              className="btn btn-danger"
              onClick={() => onDelete(note.id)}
              disabled={loading}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotesList;
