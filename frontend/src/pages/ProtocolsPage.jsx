import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProtocols } from '../services/api'
import ProtocolCard from '../components/ProtocolCard'
import './ProtocolsPage.css'

function ProtocolsPage() {
  const [protocols, setProtocols] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchProtocols = async () => {
      try {
        setLoading(true)
        const data = await getProtocols()
        setProtocols(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchProtocols()
  }, [])

  if (loading) {
    return (
      <div className="protocols-page">
        <header className="app-header">
          <h1>Protocols</h1>
          <Link to="/add-protocol" className="add-protocol-btn">
            Add Protocol
          </Link>
        </header>
        <div className="loading">Loading protocols...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="protocols-page">
        <header className="app-header">
          <h1>Protocols</h1>
          <Link to="/add-protocol" className="add-protocol-btn">
            Add Protocol
          </Link>
        </header>
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="protocols-page">
      <header className="app-header">
        <h1>Protocols</h1>
        <Link to="/add-protocol" className="add-protocol-btn">
          Add Protocol
        </Link>
      </header>
      <main className="protocols-grid">
        {protocols.length === 0 ? (
          <div className="empty-state">No protocols found</div>
        ) : (
          protocols.map((protocol) => (
            <ProtocolCard key={protocol.protocol_id} protocol={protocol} />
          ))
        )}
      </main>
    </div>
  )
}

export default ProtocolsPage
