import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { uploadProtocol } from '../services/api'
import './AddProtocolPage.css'

function AddProtocolPage() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (isValidFileType(droppedFile)) {
        setFile(droppedFile)
        setError(null)
      } else {
        setError('Please upload a PDF or image file')
      }
    }
  }

  const isValidFileType = (file) => {
    const validTypes = [
      'application/pdf',
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp'
    ]
    return validTypes.includes(file.type)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file to upload')
      return
    }

    if (!isValidFileType(file)) {
      setError('Please upload a PDF or image file')
      return
    }

    try {
      setUploading(true)
      setError(null)
      
      const formData = new FormData()
      formData.append('file', file)
      
      await uploadProtocol(formData)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="add-protocol-page">
      <header className="app-header">
        <h1>Add Protocol</h1>
        <Link to="/" className="back-btn">
          ← Back to Protocols
        </Link>
      </header>
      
      <main className="upload-container">
        <div className="upload-card">
          <h2>Upload Protocol Document</h2>
          <p className="upload-description">
            Upload a PDF or image file containing your protocol
          </p>
          
          <form onSubmit={handleSubmit} className="upload-form">
            <div
              className={`file-drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="file-upload"
                accept=".pdf,.jpg,.jpeg,.png,.gif,.webp"
                onChange={handleFileChange}
                className="file-input"
              />
              <label htmlFor="file-upload" className="file-label">
                {file ? (
                  <div className="file-selected">
                    <div className="file-icon">📄</div>
                    <div className="file-info">
                      <div className="file-name">{file.name}</div>
                      <div className="file-size">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="file-placeholder">
                    <div className="upload-icon">📁</div>
                    <div className="upload-text">
                      <strong>Click to browse</strong> or drag and drop
                    </div>
                    <div className="upload-hint">
                      PDF, JPG, PNG, GIF, or WebP files
                    </div>
                  </div>
                )}
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="form-actions">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="cancel-btn"
                disabled={uploading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="upload-btn"
                disabled={!file || uploading}
              >
                {uploading ? 'Uploading...' : 'Upload Protocol'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}

export default AddProtocolPage
