import React, { useState, useEffect, useRef, useCallback } from 'react';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [isWaitingForWakeWord, setIsWaitingForWakeWord] = useState(false);
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  const processCommand = useCallback(async (command) => {
    const lowerCommand = command.toLowerCase();
    let responseText = '';

    try {
      // Check for wake word
      if (lowerCommand.includes('hello specter') || lowerCommand.includes('hey specter') || lowerCommand.includes('hi specter')) {
        setIsWaitingForWakeWord(false);
        responseText = 'Hello! I am Specter, your legal assistant. How can I help you today?';
        speak(responseText);
        return;
      }

      // Check for stop command
      if (lowerCommand.includes('satisfied') || lowerCommand.includes('stop') || lowerCommand.includes('exit') || lowerCommand.includes('quit') || lowerCommand.includes('goodbye')) {
        responseText = 'Thank you! I am deactivating. Say "Hello Specter" to activate me again.';
        setIsActive(false);
        setIsWaitingForWakeWord(false);
        speak(responseText);
        return;
      }

      // Only process commands if not waiting for wake word
      if (isWaitingForWakeWord) {
        return;
      }

      // Navigation commands
      if (lowerCommand.includes('go to') || lowerCommand.includes('navigate to') || lowerCommand.includes('open')) {
        if (lowerCommand.includes('home') || lowerCommand.includes('main page')) {
          responseText = 'Navigating to home page';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'home' }));
        } else if (lowerCommand.includes('ask') || lowerCommand.includes('question') || lowerCommand.includes('legal question')) {
          responseText = 'Opening legal question interface';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'chat' }));
        } else if (lowerCommand.includes('solutions') || lowerCommand.includes('legal solutions')) {
          responseText = 'Opening legal solutions';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'solutions' }));
        } else if (lowerCommand.includes('upload') || lowerCommand.includes('documents')) {
          responseText = 'Opening document upload';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'upload' }));
        } else if (lowerCommand.includes('services') || lowerCommand.includes('legal services')) {
          responseText = 'Opening legal services portal';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'services' }));
        } else if (lowerCommand.includes('contact') || lowerCommand.includes('contact us')) {
          responseText = 'Opening contact form';
          window.dispatchEvent(new CustomEvent('navigateTo', { detail: 'contact' }));
        } else {
          responseText = 'I can help you navigate to: home, ask legal questions, solutions, upload documents, legal services, or contact. Please specify which section you want to go to.';
        }
      }
      // Help commands - only narrate when user says help
      else if (lowerCommand.includes('help') || lowerCommand.includes('what can you do')) {
        responseText = 'Here are the available commands: Say "go to ask legal questions" to open the question interface, "go to solutions" for legal solutions, "go to upload" for document upload, "go to services" for legal services, "go to contact" for contact form, "what time is it" for current time, and "satisfied" to stop.';
      }
      // Time and date
      else if (lowerCommand.includes('time') || lowerCommand.includes('what time')) {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        responseText = `The current time is ${timeString}`;
      }
      else if (lowerCommand.includes('date') || lowerCommand.includes('what date') || lowerCommand.includes('today')) {
        const now = new Date();
        const dateString = now.toLocaleDateString();
        responseText = `Today's date is ${dateString}`;
      }
      // Default response
      else {
        responseText = 'I heard you say: ' + command + '. Say "help" to learn what I can do.';
      }

      speak(responseText);

    } catch (error) {
      console.error('Error processing command:', error);
      responseText = 'Sorry, I encountered an error processing your command. Please try again.';
      speak(responseText);
    }
  }, [isWaitingForWakeWord]);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        processCommand(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'not-allowed') {
          speak('Microphone permission denied. Please allow microphone access to use voice assistant.');
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        // Restart listening if still active
        if (isActive && !isWaitingForWakeWord) {
          setTimeout(() => {
            if (isActive && !isWaitingForWakeWord) {
              recognitionRef.current.start();
            }
          }, 100);
        }
      };
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isActive, isWaitingForWakeWord, processCommand]);

  const speak = (text) => {
    if (synthesisRef.current) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      synthesisRef.current.speak(utterance);
    }
  };

  const toggleVoiceAssistant = () => {
    if (!isActive) {
      // Request microphone permission only when activating
      if (recognitionRef.current) {
        setIsActive(true);
        setIsWaitingForWakeWord(true);
        speak('Voice assistant activated. Say "Hello Specter" to start.');
        recognitionRef.current.start();
      } else {
        console.error('Speech recognition is not supported in your browser.');
      }
    } else {
      setIsActive(false);
      setIsWaitingForWakeWord(false);
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }
      speak('Voice assistant deactivated.');
    }
  };

  return (
    <div className="voice-assistant">
      {/* Voice Assistant Button */}
      <button
        className={`voice-assistant-btn ${isActive ? 'active' : ''} ${isListening ? 'listening' : ''}`}
        onClick={toggleVoiceAssistant}
        title={isActive ? 'Deactivate Voice Assistant' : 'Activate Voice Assistant'}
      >
        <i className={`fas fa-microphone${isListening ? '-slash' : ''}`}></i>
        {isListening && <div className="pulse-ring"></div>}
      </button>
    </div>
  );
};

export default VoiceAssistant;
