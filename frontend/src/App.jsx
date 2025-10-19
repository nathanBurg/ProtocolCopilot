import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ProtocolsPage from './pages/ProtocolsPage'
import AddProtocolPage from './pages/AddProtocolPage'
import ProtocolDetailPage from './pages/ProtocolDetailPage'
import ProtocolPreviewPage from './pages/ProtocolPreviewPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<ProtocolsPage />} />
          <Route path="/add-protocol" element={<AddProtocolPage />} />
          <Route path="/protocols/:protocolId" element={<ProtocolDetailPage />} />
          <Route path="/protocol-preview" element={<ProtocolPreviewPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
