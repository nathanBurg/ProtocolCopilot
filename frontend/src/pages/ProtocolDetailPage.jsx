import { useState, useEffect } from 'react'
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
          <h3 className="section-title">Experiments</h3>
          <div className="experiments-placeholder">
            <p>No experiments yet. This section will be implemented soon.</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default ProtocolDetailPage
