// src/services/userService.js
import axios from '@/axios'

/**
 * Fetch all users
 * GET /api/users
 */
export function fetchUsers() {
  return axios.get('/users')
}

/**
 * Fetch a single user by ID
 * GET /api/users/:id
 */
export function getUserById(id) {
  return axios.get(`/users/${id}`)
}
