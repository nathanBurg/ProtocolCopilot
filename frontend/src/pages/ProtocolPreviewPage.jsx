import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { createProtocol } from '../services/api'
import './ProtocolPreviewPage.css'

function ProtocolPreviewPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [previewData, setPreviewData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Form state
  const [protocolName, setProtocolName] = useState('')
  const [description, setDescription] = useState('')
  const [steps, setSteps] = useState([])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    // Get preview data from navigation state
    if (location.state?.previewData) {
      setPreviewData(location.state.previewData)
      setProtocolName(location.state.previewData.protocol?.protocol_name || '')
      setDescription(location.state.previewData.protocol?.description || '')
      setSteps(location.state.previewData.protocol_steps || [])
      setLoading(false)
    } else {
      setError('No preview data available')
      setLoading(false)
    }
  }, [location.state])

  const handleStepChange = (index, field, value) => {
    const updatedSteps = [...steps]
    updatedSteps[index] = { ...updatedSteps[index], [field]: value }
    setSteps(updatedSteps)
  }

  const addStep = () => {
    const newStep = {
      protocol_step_id: `temp-${Date.now()}`,
      step_number: steps.length + 1,
      step_name: '',
      instruction: '',
      expected_duration_minutes: null
    }
    setSteps([...steps, newStep])
  }

  const removeStep = (index) => {
    const updatedSteps = steps.filter((_, i) => i !== index)
    // Renumber steps
    const renumberedSteps = updatedSteps.map((step, i) => ({
      ...step,
      step_number: i + 1
    }))
    setSteps(renumberedSteps)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      
      // Prepare protocol data
      const protocolData = {
        protocol_id: previewData.protocol?.protocol_id || `temp-${Date.now()}`,
        document_id: previewData.protocol?.document_id,
        protocol_name: protocolName,
        description: description,
        created_by_user_id: previewData.protocol?.created_by_user_id,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      // Prepare steps data
      const stepsData = steps.map((step, index) => ({
        protocol_step_id: step.protocol_step_id || `temp-step-${Date.now()}-${index}`,
        protocol_id: protocolData.protocol_id,
        step_number: step.step_number,
        step_name: step.step_name,
        instruction: step.instruction,
        expected_duration_minutes: step.expected_duration_minutes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }))
      
      // Call the API to create the protocol
      const response = await createProtocol(protocolData, stepsData)
      
      // Navigate to the protocol detail page
      navigate(`/protocols/${response.protocol.protocol_id}`)
    } catch (err) {
      setError(`Failed to save protocol: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    navigate('/')
  }

  if (loading) {
    return (
      <div className="protocol-preview-page">
        <header className="app-header">
          <h1>Protocol Preview</h1>
          <button onClick={handleCancel} className="cancel-btn">
            Cancel
          </button>
        </header>
        <div className="loading">Loading preview...</div>
      </div>
    )
  }

  if (error || !previewData) {
    return (
      <div className="protocol-preview-page">
        <header className="app-header">
          <h1>Protocol Preview</h1>
          <button onClick={handleCancel} className="cancel-btn">
            Cancel
          </button>
        </header>
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="protocol-preview-page">
      <header className="app-header">
        <h1>Protocol Preview</h1>
        <div className="header-actions">
          <button onClick={handleCancel} className="cancel-btn">
            Cancel
          </button>
          <button onClick={handleSave} className="save-btn" disabled={saving}>
            {saving ? 'Saving...' : 'Save Protocol'}
          </button>
        </div>
      </header>

      <main className="preview-content">
        {/* Left side - File preview */}
        <div className="file-preview-section">
          <h3>Document Preview</h3>
          <div className="file-viewer">
            {previewData.protocol?.document_id && (
              <iframe
                src={previewData.object_url}
                title="Document Preview"
                className="document-iframe"
              />
            )}
          </div>
        </div>

        {/* Right side - Editable form */}
        <div className="form-section">
          <h3>Protocol Details</h3>
          
          <div className="form-group">
            <label htmlFor="protocol-name">Protocol Name</label>
            <input
              id="protocol-name"
              type="text"
              value={protocolName}
              onChange={(e) => setProtocolName(e.target.value)}
              className="form-input"
              placeholder="Enter protocol name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="form-textarea"
              placeholder="Enter protocol description"
              rows={4}
            />
          </div>

          <div className="steps-section">
            <div className="steps-header">
              <h4>Protocol Steps</h4>
              <button onClick={addStep} className="add-step-btn">
                + Add Step
              </button>
            </div>

            <div className="steps-list">
              {steps.map((step, index) => (
                <div key={step.protocol_step_id || index} className="step-item">
                  <div className="step-header">
                    <span className="step-number">Step {step.step_number}</span>
                    <button 
                      onClick={() => removeStep(index)}
                      className="remove-step-btn"
                    >
                      ×
                    </button>
                  </div>
                  
                  <div className="step-fields">
                    <input
                      type="text"
                      value={step.step_name}
                      onChange={(e) => handleStepChange(index, 'step_name', e.target.value)}
                      className="form-input"
                      placeholder="Step name"
                    />
                    
                    <textarea
                      value={step.instruction}
                      onChange={(e) => handleStepChange(index, 'instruction', e.target.value)}
                      className="form-textarea"
                      placeholder="Step instructions"
                      rows={3}
                    />
                    
                    <input
                      type="number"
                      value={step.expected_duration_minutes || ''}
                      onChange={(e) => handleStepChange(index, 'expected_duration_minutes', parseInt(e.target.value) || null)}
                      className="form-input"
                      placeholder="Duration (minutes)"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default ProtocolPreviewPage
