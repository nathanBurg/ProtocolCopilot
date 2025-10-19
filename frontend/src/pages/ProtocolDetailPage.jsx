import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProtocol } from '../services/api'
import './ProtocolDetailPage.css'

function ProtocolDetailPage() {
  const { protocolId } = useParams()
  const [protocol, setProtocol] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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
