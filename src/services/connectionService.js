import axios from '@/axios'

export function fetchConnections() {
  return axios.get('/connections')
}

export function fetchSteamConnectUrl() {
  return axios.get('/connections/steam/start')
}

export function disconnectConnection(provider) {
  return axios.delete(`/connections/${provider}`)
}
