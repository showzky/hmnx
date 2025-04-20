<template>
    <div class="pending-requests mx-auto p-6 bg-[var(--card-bg)] rounded-2xl shadow-lg">
      <h2 class="text-3xl font-extrabold text-[var(--text)] mb-6">Friend Requests</h2>
      <ul class="space-y-4">
        <li
          v-for="req in requests"
          :key="req.id"
          class="flex items-center justify-between p-4 bg-[var(--card-bg)] border border-gray-700 rounded-xl hover:bg-gray-800 transition"
        >
          <div class="flex items-center gap-4">
            <img
              v-if="req.sender.avatar"
              :src="req.sender.avatar"
              alt="avatar"
              class="w-10 h-10 rounded-full object-cover"
            />
            <span class="text-white font-medium">{{ req.sender.username || req.sender.email }}</span>
          </div>
          <div class="flex gap-2">
            <button
              @click="accept(req.id)"
              class="text-sm bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-full transition"
            >Accept</button>
            <button
              @click="decline(req.id)"
              class="text-sm bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-full transition"
            >Decline</button>
          </div>
        </li>
        <li v-if="!requests.length" class="text-gray-400 text-center py-6">
          You have no pending friend requests.
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import {
    listIncomingRequests,
    acceptFriendRequest,
    declineFriendRequest
  } from '@/services/friendRequestService';
  
  export default {
    name: 'PendingRequests',
    setup() {
      const requests = ref([]);
  
      async function loadRequests() {
        try {
          const res = await listIncomingRequests();
          // API returns array of { id, sender: { id, username, email, avatar } }
          requests.value = res.data;
        } catch (e) {
          console.error('Error loading friend requests:', e);
        }
      }
  
      async function accept(requestId) {
        try {
          await acceptFriendRequest(requestId);
          requests.value = requests.value.filter(r => r.id !== requestId);
        } catch (e) {
          console.error('Error accepting friend request:', e);
        }
      }
  
      async function decline(requestId) {
        try {
          await declineFriendRequest(requestId);
          requests.value = requests.value.filter(r => r.id !== requestId);
        } catch (e) {
          console.error('Error declining friend request:', e);
        }
      }
  
      onMounted(loadRequests);
  
      return { requests, accept, decline };
    }
  };
  </script>
  
  <style scoped>
  .pending-requests { max-width: 700px; }
  </style>
  