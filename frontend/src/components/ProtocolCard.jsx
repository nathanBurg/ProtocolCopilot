import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import './ProtocolCard.css'

function ProtocolCard({ protocol }) {
  return (
    <Link to={`/protocols/${protocol.protocol_id}`} className="protocol-card-link">
      <div className="protocol-card">
        <h3 className="protocol-title">{protocol.protocol_name || 'Untitled Protocol'}</h3>
        <p className="protocol-description">
          {protocol.description || 'No description available'}
        </p>
      </div>
    </Link>
  )
}

ProtocolCard.propTypes = {
  protocol: PropTypes.shape({
    protocol_id: PropTypes.string.isRequired,
    protocol_name: PropTypes.string,
    description: PropTypes.string,
    created_at: PropTypes.string,
  }).isRequired,
}

export default ProtocolCard
