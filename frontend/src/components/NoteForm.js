import React, { useState, useEffect } from 'react';

const NoteForm = ({ note, onSave, onCancel, loading }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (note) {
      setTitle(note.title || '');
      setContent(note.content || '');
    } else {
      setTitle('');
      setContent('');
    }
  }, [note]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      return;
    }

    onSave({
      title: title.trim(),
      content: content.trim()
    });

    // Reset form if creating new note
    if (!note) {
      setTitle('');
      setContent('');
    }
  };

  const handleCancel = () => {
    setTitle('');
    setContent('');
    onCancel();
  };

  return (
    <form className="note-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="title">Title:</label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter note title..."
          required
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="content">Content:</label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Enter note content..."
          required
          disabled={loading}
        />
      </div>

      <div className="button-group">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !title.trim() || !content.trim()}
        >
          {note ? 'Update Note' : 'Save Note'}
        </button>
        
        {note && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleCancel}
            disabled={loading}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default NoteForm;
