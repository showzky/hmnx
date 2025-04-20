<template>
  <div class="friends-list mx-auto p-6 bg-[var(--card-bg)] rounded-2xl shadow-lg">
    <h2 class="text-3xl font-extrabold text-[var(--text)] mb-6">Your Friends</h2>
    <ul class="space-y-4">
      <li
        v-for="friend in friends"
        :key="friend.id"
        class="flex items-center justify-between p-4 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl hover:scale-[1.02] transform transition"
      >
        <router-link
          :to="{ name: 'UserProfile', params: { userId: friend.id } }"
          class="flex items-center gap-4"
        >
          <img
            v-if="friend.avatar"
            :src="friend.avatar"
            alt="avatar"
            class="w-10 h-10 rounded-full object-cover"
          />
          <span class="text-lg font-medium text-white">
            {{ friend.username || friend.email }}
          </span>
        </router-link>
        <button
          @click="handleRemoveFriend(friend.id)"
          class="text-sm bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-full shadow-md transition"
        >
          Remove
        </button>
      </li>
      <li v-if="!friends.length" class="text-gray-400 text-center py-6">
        You have no friends yet.
      </li>
    </ul>

    <h2 class="text-3xl font-extrabold text-[var(--text)] mt-12 mb-6">People You May Know</h2>
    <ul class="space-y-4">
      <li
        v-for="user in potentialFriends"
        :key="user.id"
        class="flex items-center justify-between p-4 bg-[var(--card-bg)] border border-gray-700 rounded-xl hover:bg-gray-800 transition"
      >
        <div class="flex items-center gap-4">
          <img
            v-if="user.avatar"
            :src="user.avatar"
            alt="avatar"
            class="w-10 h-10 rounded-full object-cover"
          />
          <span class="text-white font-medium">{{ user.username || user.email }}</span>
        </div>
        <button
          :disabled="sentRequests.includes(user.id)"
          @click="handleAddFriend(user.id)"
          class="text-sm text-white py-2 px-5 rounded-full shadow-md transition disabled:opacity-50 disabled:cursor-default"
          :class="sentRequests.includes(user.id)
            ? 'bg-gray-600'
            : 'bg-[var(--accent)] hover:bg-pink-500'
          "
        >
          {{ sentRequests.includes(user.id) ? 'Pending' : 'Send Request' }}
        </button>
      </li>
      <li v-if="!potentialFriends.length" class="text-gray-400 text-center py-6">
        No users to add at the moment.
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { fetchUsers } from '@/services/userService';
import { fetchFriends, removeFriend as removeFriendService } from '@/services/friendService';
import { sendFriendRequest, listSentRequests } from '@/services/friendRequestService';

export default {
  name: 'FriendsList',
  setup() {
    const users = ref([]);
    const friends = ref([]);
    const sentRequests = ref([]);
    const loading = ref(false);

    const potentialFriends = computed(() =>
      users.value.filter(user =>
        !friends.value.some(f => f.id === user.id)
      )
    );

    async function loadUsers() {
      loading.value = true;
      try {
        const res = await fetchUsers();
        users.value = res.data.users || res.data;
      } catch (err) {
        console.error('Error fetching users:', err);
      } finally {
        loading.value = false;
      }
    }

    async function loadFriends() {
      loading.value = true;
      try {
        const res = await fetchFriends();
        friends.value = res.data.friends || res.data;
      } catch (err) {
        console.error('Error fetching friends:', err);
      } finally {
        loading.value = false;
      }
    }

    async function loadSentRequests() {
      try {
        const res = await listSentRequests();
        sentRequests.value = res.data.map(r => r.receiver_id || r.receiver);
      } catch (err) {
        console.error('Error fetching sent requests:', err);
      }
    }

    async function handleAddFriend(userId) {
      // Optimistic UI: mark as pending immediately
      if (!sentRequests.value.includes(userId)) {
        sentRequests.value.push(userId);
      }
      try {
        await sendFriendRequest(userId);
      } catch (err) {
        // If conflict, it was already sent, so keep pending; otherwise revert
        if (!err.response || err.response.status !== 409) {
          sentRequests.value = sentRequests.value.filter(id => id !== userId);
          console.error('Error sending friend request:', err);
        }
      }
    }

    async function handleRemoveFriend(userId) {
      try {
        await removeFriendService(userId);
        await loadFriends();
      } catch (err) {
        console.error('Error removing friend:', err);
      }
    }

    onMounted(async () => {
      await Promise.all([loadUsers(), loadFriends(), loadSentRequests()]);
    });

    return {
      friends,
      potentialFriends,
      sentRequests,
      handleAddFriend,
      handleRemoveFriend,
      loading
    };
  }
};
</script>

<style scoped>
.friends-list { max-width: 700px; }
/* Scrollbar styling */
ul { scrollbar-width: thin; scrollbar-color: rgba(200,200,200,0.3) transparent; }
ul::-webkit-scrollbar { width: 6px; }
ul::-webkit-scrollbar-track { background: transparent; }
ul::-webkit-scrollbar-thumb { background-color: rgba(200,200,200,0.3); border-radius: 3px; }
</style>
