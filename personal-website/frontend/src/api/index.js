import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export function getHomeData() {
  return api.get('/home')
}

export function submitContact(data) {
  return api.post('/contact', data)
}