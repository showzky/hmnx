// src/services/friendRequestService.js
import axios from '@/axios';

// helpers --------------------------------------------------------------
const API = import.meta.env.VITE_API_URL;           // → ".../api"
const url  = (path) => `${API}${path}`;             // keeps code DRY
// ---------------------------------------------------------------------

/**
 * Send a friend request to another user.
 * POST  /api/friend-requests   { receiver_id }
 */
export function sendFriendRequest(receiverId) {
  return axios.post(url('/friend-requests'), {
    receiver_id: receiverId,
  });
}

/**
 * List all incoming friend requests for the current user.
 * GET  /api/friend-requests
 */
export function listIncomingRequests() {
  return axios.get(url('/friend-requests'));
}

/**
 * Accept a friend request.
 * POST  /api/friend-requests/:id/accept
 */
export function acceptFriendRequest(requestId) {
  return axios.post(url(`/friend-requests/${requestId}/accept`));
}

/**
 * Decline a friend request.
 * POST  /api/friend-requests/:id/decline
 */
export function declineFriendRequest(requestId) {
  return axios.post(url(`/friend-requests/${requestId}/decline`));
}
