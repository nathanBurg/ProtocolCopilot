import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const uploadApi = axios.create({
  baseURL: API_BASE_URL,
})

export const getProtocols = async () => {
  try {
    const response = await api.get('/protocols')
    return response.data
  } catch (error) {
    throw new Error(`Failed to fetch protocols: ${error.message}`)
  }
}

export const getProtocol = async (protocolId) => {
  try {
    const response = await api.get(`/protocols/${protocolId}`)
    return response.data
  } catch (error) {
    throw new Error(`Failed to fetch protocol: ${error.message}`)
  }
}

export const uploadProtocol = async (formData) => {
  try {
    const response = await uploadApi.post('/protocols/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    throw new Error(`Failed to upload protocol: ${error.message}`)
  }
}

export const createProtocol = async (protocol, protocolSteps) => {
  try {
    const response = await api.post('/protocols/create', {
      protocol: protocol,
      protocol_steps: protocolSteps
    })
    return response.data
  } catch (error) {
    throw new Error(`Failed to create protocol: ${error.message}`)
  }
}

export const getProtocolSteps = async (protocolId) => {
  try {
    const response = await api.get(`/protocol_steps/${protocolId}`)
    return response.data
  } catch (error) {
    throw new Error(`Failed to fetch protocol steps: ${error.message}`)
  }
}

export const startExperiment = async (protocolId, userId = null) => {
  try {
    const response = await api.post('/experiments/start', {
      protocol_id: protocolId,
      user_id: userId
    })
    return response.data
  } catch (error) {
    throw new Error(`Failed to start experiment: ${error.message}`)
  }
}

export const stopExperiment = async (experimentId, endTime = null) => {
  try {
    const response = await api.post('/experiments/stop', {
      experiment_id: experimentId,
      end_time: endTime
    })
    return response.data
  } catch (error) {
    throw new Error(`Failed to stop experiment: ${error.message}`)
  }
}

export const voiceTurn = async (audioFile) => {
  try {
    const formData = new FormData()
    formData.append('file', audioFile, 'turn.webm')
    
    const response = await uploadApi.post('/experiments/voice-turn', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    throw new Error(`Failed to process voice turn: ${error.message}`)
  }
}

export const getExperimentsByProtocol = async (protocolId) => {
  try {
    const response = await api.get(`/experiments/protocol/${protocolId}`)
    return response.data
  } catch (error) {
    throw new Error(`Failed to fetch experiments: ${error.message}`)
  }
}
