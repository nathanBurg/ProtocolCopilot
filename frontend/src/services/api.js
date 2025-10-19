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
