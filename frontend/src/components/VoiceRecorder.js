import React, { useState, useEffect } from 'react';

const VoiceRecorder = ({ onTranscription }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [transcript, setTranscript] = useState('');

  useEffect(() => {
    // Check if browser supports Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      // Enhanced configuration based on the documentation
      recognitionInstance.continuous = true; // Allow continuous recording
      recognitionInstance.interimResults = true; // Show interim results
      recognitionInstance.lang = language;
      recognitionInstance.maxAlternatives = 1;

      recognitionInstance.onstart = () => {
        setIsRecording(true);
        setError('');
        setTranscript('');
      };

      recognitionInstance.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update the transcript display
        const currentTranscript = finalTranscript || interimTranscript;
        setTranscript(currentTranscript);

        // If we have final results, call the callback
        if (finalTranscript) {
          onTranscription(finalTranscript);
        }
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
        setIsRecording(false);
      };

      recognitionInstance.onend = () => {
        setIsRecording(false);
      };

      setRecognition(recognitionInstance);
      setIsSupported(true);
    } else {
      setError('Speech recognition is not supported in this browser. Please use Chrome, Firefox, Safari, or Edge.');
      setIsSupported(false);
    }
  }, [onTranscription, language]);

  const startRecording = () => {
    if (recognition && !isRecording) {
      try {
        setTranscript('');
        recognition.start();
      } catch (err) {
        setError('Failed to start recording. Please try again.');
        console.error('Error starting recognition:', err);
      }
    }
  };

  const stopRecording = () => {
    if (recognition && isRecording) {
      recognition.stop();
    }
  };

  const clearTranscript = () => {
    setTranscript('');
  };

  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    if (recognition) {
      recognition.lang = newLanguage;
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-recorder">
        <div className="error">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="voice-recorder">
      <h3>Voice Dictation</h3>
      
      {/* Language Selection */}
      <div className="language-selector">
        <label htmlFor="language">Language:</label>
        <select 
          id="language" 
          value={language} 
          onChange={handleLanguageChange}
          disabled={isRecording}
        >
          <option value="en-US">English (US)</option>
          <option value="en-GB">English (UK)</option>
          <option value="es-ES">Spanish</option>
          <option value="fr-FR">French</option>
          <option value="de-DE">German</option>
          <option value="it-IT">Italian</option>
          <option value="pt-BR">Portuguese (Brazil)</option>
          <option value="ru-RU">Russian</option>
          <option value="ja-JP">Japanese</option>
          <option value="ko-KR">Korean</option>
          <option value="zh-CN">Chinese (Simplified)</option>
        </select>
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="recording-status">
          <div className="recording-indicator">
            <span className="pulse"></span>
            Listening... Speak now
          </div>
        </div>
      )}
      
      {/* Error Display */}
      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="transcript-display">
          <label>Live Transcript:</label>
          <div className="transcript-text" contentEditable="true">
            {transcript}
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div className="button-group">
        <button
          className={`btn ${isRecording ? 'btn-danger' : 'btn-success'}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!isSupported}
        >
          {isRecording ? 'Stop Recording' : 'Start Voice Input'}
        </button>
        
        {transcript && (
          <button
            className="btn btn-secondary"
            onClick={clearTranscript}
            disabled={isRecording}
          >
            Clear
          </button>
        )}
      </div>

      {/* Instructions */}
      <div className="voice-instructions">
        <p>Click "Start Voice Input" and speak clearly. The text will appear in real-time.</p>
        <p>Make sure your microphone is enabled and you're in a quiet environment for best results.</p>
      </div>
    </div>
  );
};

export default VoiceRecorder;
