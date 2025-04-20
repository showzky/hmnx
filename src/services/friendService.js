// friendservice.js
import axios from '@/axios'

export function fetchFriends() {
  return axios.get('/friends')
}

export function addFriend(friendId) {
  return axios.post('/friends', { friend_id: friendId })
}

export function removeFriend(friendId) {
  return axios.delete(`/friendship/${friendId}`) // <-- fixed endpoint
}