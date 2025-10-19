import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProtocol, getProtocolSteps } from '../services/api'
import './ProtocolDetailPage.css'

function ProtocolDetailPage() {
  const { protocolId } = useParams()
  const [protocol, setProtocol] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Steps state
  const [steps, setSteps] = useState([])
  const [showSteps, setShowSteps] = useState(false)
  const [loadingSteps, setLoadingSteps] = useState(false)
  const [stepsError, setStepsError] = useState(null)
  
  // Voice interaction state
  const [isExperimentActive, setIsExperimentActive] = useState(false)
  const [voiceStatus, setVoiceStatus] = useState('')
  const [isListening, setIsListening] = useState(false)
  const experimentActiveRef = useRef(false)

  useEffect(() => {
    const fetchProtocol = async () => {
      try {
        setLoading(true)
        const data = await getProtocol(protocolId)
        setProtocol(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (protocolId) {
      fetchProtocol()
    }
  }, [protocolId])

  const handleStepsToggle = async () => {
    if (showSteps) {
      setShowSteps(false)
      return
    }

    if (steps.length > 0) {
      setShowSteps(true)
      return
    }

    try {
      setLoadingSteps(true)
      setStepsError(null)
      const stepsData = await getProtocolSteps(protocolId)
      setSteps(stepsData)
      setShowSteps(true)
    } catch (error) {
      setStepsError(error.message)
    } finally {
      setLoadingSteps(false)
    }
  }

  // Voice interaction functions
  const recordUntilSilence = async () => {
    console.log("Starting recordUntilSilence...");
    // Request high-quality audio for better transcription
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 44100,
        channelCount: 1
      }
    });
    console.log("Got media stream with enhanced audio settings");
    
    const chunks = [];
    const recorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });
    recorder.ondataavailable = e => chunks.push(e.data);
  
    // Simple timeout-based recording instead of silence detection
    const RECORDING_DURATION = 5000; // Record for 5 seconds max
    
    recorder.start();
    console.log("Recorder started - will record for", RECORDING_DURATION, "ms");
    
    return new Promise(resolve => {
      // Stop recording after fixed duration
      setTimeout(() => {
        if (recorder.state === "recording") {
          console.log("Recording timeout reached - stopping recorder");
          recorder.stop();
        }
      }, RECORDING_DURATION);
      
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        console.log("Recording stopped, blob size:", blob.size);
        resolve(blob);
      };
    });
  };
  

  const sendToBackend = async (audioBlob) => {
    console.log("Sending audio to backend, blob size:", audioBlob.size);
    const form = new FormData();
    form.append("file", audioBlob, "turn.webm");
    const res = await fetch("/api/voice-turn", { method: "POST", body: form });
    console.log("Backend response status:", res.status);
    
    if (!res.ok) {
      throw new Error(`Backend error: ${res.status} ${res.statusText}`);
    }
    
    const text = await res.text();
    console.log("Backend response text:", text);
    
    try {
      const data = JSON.parse(text);
      console.log("Backend response data:", data);
      return data.reply;
    } catch (error) {
      console.error("JSON parse error:", error);
      console.error("Response text:", text);
      throw new Error(`Invalid JSON response: ${text}`);
    }
  }

  const speak = (text) => {
    return new Promise(resolve => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onend = resolve;
      speechSynthesis.speak(utterance);
    });
  }

  const conversationLoop = async () => {
    console.log("conversationLoop called, experimentActiveRef.current:", experimentActiveRef.current);
    if (!experimentActiveRef.current) return;
    
    try {
      console.log("Setting voice status to listening...");
      setVoiceStatus("🎤 Listening...");
      setIsListening(true);
      console.log("Calling recordUntilSilence...");
      const audio = await recordUntilSilence();
      console.log("Got audio, setting status to processing...");
      setVoiceStatus("🔄 Processing...");
      setIsListening(false);
      console.log("Sending to backend...");
      const reply = await sendToBackend(audio);
      console.log("Got reply:", reply);
      setVoiceStatus(`🤖 ${reply}`);
      await speak(reply);
      setVoiceStatus("");
      // Wait for user to speak again - don't auto-continue
      console.log("Waiting for user to speak again...");
      if (experimentActiveRef.current) {
        setTimeout(conversationLoop, 2000); // Wait 2 seconds before listening again
      }
    } catch (error) {
      console.error("Error in conversation loop:", error);
      setVoiceStatus(`❌ Error: ${error.message}`);
      setIsListening(false);
    }
  }

  const startExperiment = async () => {
    console.log("startExperiment called");
    try {
      console.log("Requesting microphone permission...");
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("Microphone permission granted");
      setIsExperimentActive(true);
      experimentActiveRef.current = true;
      setVoiceStatus("🎤 Starting experiment...");
      console.log("Starting conversation loop...");
      conversationLoop();
    } catch (error) {
      console.error("Error in startExperiment:", error);
      setVoiceStatus(`❌ Microphone access denied: ${error.message}`);
    }
  }

  const stopExperiment = () => {
    console.log("stopExperiment called");
    setIsExperimentActive(false);
    experimentActiveRef.current = false;
    setVoiceStatus("");
    setIsListening(false);
  }

  if (loading) {
    return (
      <div className="protocol-detail-page">
        <header className="app-header">
          <h1>Protocol Details</h1>
          <Link to="/" className="back-btn">
            ← Back to Protocols
          </Link>
        </header>
        <div className="loading">Loading protocol...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="protocol-detail-page">
        <header className="app-header">
          <h1>Protocol Details</h1>
          <Link to="/" className="back-btn">
            ← Back to Protocols
          </Link>
        </header>
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  if (!protocol) {
    return (
      <div className="protocol-detail-page">
        <header className="app-header">
          <h1>Protocol Details</h1>
          <Link to="/" className="back-btn">
            ← Back to Protocols
          </Link>
        </header>
        <div className="error">Protocol not found</div>
      </div>
    )
  }

  return (
    <div className="protocol-detail-page">
      <header className="app-header">
        <h1>Protocol Details</h1>
        <Link to="/" className="back-btn">
          ← Back to Protocols
        </Link>
      </header>
      
      <main className="protocol-detail-content">
        {/* Protocol Data Rectangle */}
        <div className="protocol-data-card">
          <div className="protocol-header">
            <h2 className="protocol-title">{protocol.protocol_name}</h2>
            <div className="protocol-id-badge">ID: {protocol.protocol_id}</div>
          </div>
          
          <div className="protocol-info-grid">
            <div className="info-item">
              <label>Description</label>
              <p>{protocol.description || 'No description available'}</p>
            </div>
            
            <div className="info-item">
              <label>Document ID</label>
              <p className="document-id">{protocol.document_id}</p>
            </div>
            
            <div className="info-item">
              <label>Created By</label>
              <p>{protocol.created_by_user_id || 'Unknown'}</p>
            </div>
            
            <div className="info-item">
              <label>Created At</label>
              <p>{new Date(protocol.created_at).toLocaleString()}</p>
            </div>
            
            <div className="info-item">
              <label>Last Updated</label>
              <p>{new Date(protocol.updated_at).toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Steps Section */}
        <div className="steps-section">
          <div className="steps-header">
            <h3 className="section-title">Protocol Steps</h3>
            <button 
              onClick={handleStepsToggle}
              className="steps-toggle-btn"
              disabled={loadingSteps}
            >
              {loadingSteps ? 'Loading...' : showSteps ? 'Hide Steps' : 'Show Steps'}
            </button>
          </div>
          
          {showSteps && (
            <div className="steps-content">
              {stepsError ? (
                <div className="steps-error">Error loading steps: {stepsError}</div>
              ) : steps.length === 0 ? (
                <div className="no-steps">No steps available</div>
              ) : (
                <div className="steps-list">
                  {steps.map((step, index) => (
                    <div key={step.protocol_step_id || index} className="step-item">
                      <div className="step-header">
                        <span className="step-number">Step {step.step_number}</span>
                        <span className="step-duration">
                          {step.expected_duration_minutes ? `${step.expected_duration_minutes} min` : ''}
                        </span>
                      </div>
                      <h4 className="step-name">{step.step_name}</h4>
                      <p className="step-instruction">{step.instruction}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Experiments Section */}
        <div className="experiments-section">
          <div className="experiments-header">
            <h3 className="section-title">Experiments</h3>
            <div className="experiment-controls">
              {!isExperimentActive ? (
                <button 
                  onClick={startExperiment}
                  className="start-experiment-btn"
                >
                  🎤 Start Experiment
                </button>
              ) : (
                <button 
                  onClick={stopExperiment}
                  className="stop-experiment-btn"
                >
                  ⏹️ Stop Experiment
                </button>
              )}
            </div>
          </div>
          
          {isExperimentActive && (
            <div className="voice-status">
              <div className={`voice-indicator ${isListening ? 'listening' : 'processing'}`}>
                {isListening ? '🎤' : '🔄'}
              </div>
              <div className="voice-status-text">
                {voiceStatus}
              </div>
            </div>
          )}
          
          <div className="experiments-placeholder">
            <p>No experiments yet. This section will be implemented soon.</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default ProtocolDetailPage
