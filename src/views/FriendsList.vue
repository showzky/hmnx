<template>
  <div class="friends-list">
    <h2 class="section-title">
      <i class="fas fa-user-friends icon-purple"></i> Your Friends
    </h2>
    <ul class="list">
      <li
        v-for="friend in cleanFriends"
        :key="friend.id"
        class="friend-card"
      >
        <router-link
          :to="{ name: 'UserProfile', params: { userId: friend.id } }"
          class="friend-link"
        >
          <img
            :src="friend.avatar"
            alt="avatar"
            class="avatar"
          />
          <span class="friend-name">
            {{ friend.username || friend.email }}
          </span>
        </router-link>
        <button
          @click="handleRemoveFriend(friend.id)"
          class="btn-remove"
        >
          Remove
        </button>
      </li>
      <li v-if="!cleanFriends.length" class="no-friends">
        <i class="fas fa-smile-wink icon-yellow"></i>
        You don't have any friends yet... go make someone's day!
      </li>
    </ul>

    <h2 class="section-title">
      <i class="fas fa-users icon-indigo"></i> People You May Know
    </h2>
    <ul class="list">
      <li
        v-for="user in potentialFriends"
        :key="user.id"
        class="user-card"
      >
        <div class="user-info">
          <img
            v-if="user.avatar"
            :src="user.avatar"
            alt="avatar"
            class="avatar-small"
          />
          <span class="user-name">{{ user.username || user.email }}</span>
        </div>
        <button
          @click="handleAddFriend(user.id)"
          class="btn-request"
        >
          Send Request
        </button>
      </li>
      <li v-if="!potentialFriends.length" class="no-friends">
        No users to add at the moment.
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, computed, onMounted, watchEffect } from 'vue';
import { fetchUsers } from '@/services/userService';
import { fetchFriends, removeFriend as removeFriendService } from '@/services/friendService';
import { sendFriendRequest } from '@/services/friendRequestService';

export default {
  name: 'FriendsList',
  expose: ['loadFriends'],
  setup() {
    const users = ref([]);
    const friends = ref([]);
    const loading = ref(false);

    const cleanFriends = computed(() =>
      friends.value.filter(friend =>
        friend.avatar &&
        !friend.avatar.includes('dicebear') &&
        !friend.avatar.includes('outdated')
      )
    );

    // 🛠️ TEMP: remove avatar filters to show all potential users
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
        console.log('✅ Users fetched:', users.value);
      } catch (err) {
        console.error('❌ Error fetching users:', err);
      } finally {
        loading.value = false;
      }
    }

    async function loadFriends() {
      loading.value = true;
      try {
        const res = await fetchFriends();
        friends.value = res.data.friends || res.data;
        console.log('✅ Friends fetched:', friends.value);
      } catch (err) {
        console.error('❌ Error fetching friends:', err);
      } finally {
        loading.value = false;
      }
    }

    async function handleAddFriend(userId) {
      try {
        await sendFriendRequest(userId);
        console.log(`📨 Friend request sent to user ${userId}`);
      } catch (err) {
        console.error('❌ Error sending friend request:', err);
      }
    }

    async function handleRemoveFriend(userId) {
      try {
        await removeFriendService(userId);
        console.log(`🗑️ Removed friend ${userId}`);
        await loadFriends();
      } catch (err) {
        console.error('❌ Error removing friend:', err);
      }
    }

    onMounted(async () => {
      await Promise.all([loadUsers(), loadFriends()]);
    });

    watchEffect(() => {
      console.log('🔍 Potential Friends:', potentialFriends.value);
    });

    return {
      friends,
      cleanFriends,
      potentialFriends,
      handleAddFriend,
      handleRemoveFriend,
      loading,
      loadFriends
    };
  }
};
</script>

<style scoped>
.friends-list {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2.5rem;
  /* use your palette: card-bg → background blend */
  background: linear-gradient(145deg, var(--card-bg), var(--background));
  border-radius: 2rem;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
              inset 0 4px 24px rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
}
.friends-list::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  /* subtle cosmic tints using your accent & secondary */
  background: radial-gradient(circle,
    rgba(255, 0, 110, 0.15) 0%,
    rgba(58, 134, 255, 0.1) 30%,
    transparent 70%);
  animation: cosmic-flow 20s linear infinite;
}

.section-title {
  color: var(--text);
  margin: 2rem 0;
  font-weight: 700;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  padding: 0.75rem 1.5rem;
  /* lighten your card-bg slightly */
  background: rgba( var(--card-bg-rgb, 22,21,29) , 0.1 );
  border-radius: 0.75rem;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Icons get palette tints */
.icon-purple { color: var(--secondary); text-shadow: 0 0 12px rgba(58,134,255,0.4); }
.icon-indigo { color: var(--primary); text-shadow: 0 0 12px rgba(123,44,191,0.4); }
.icon-yellow { color: var(--accent); text-shadow: 0 0 12px rgba(255,0,110,0.4); }

.list {
  list-style: none;
  padding: 0;
  margin: 2rem 0;
  display: grid;
  gap: 1.2rem;
}

.friend-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-radius: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  /* primary → secondary gradient */
  background: linear-gradient(135deg,
    rgba(var(--primary-rgb),0.8),
    rgba(var(--secondary-rgb),0.8));
  border: 1px solid rgba(255, 255, 255, 0.15);
  animation: float 4s ease-in-out infinite;
}
.friend-card:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 24px rgba(var(--primary-rgb), 0.3);
}

.user-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-radius: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  /* subtle card-bg overlay */
  background: rgba(var(--card-bg-rgb), 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}
.user-card:hover {
  background: rgba(var(--card-bg-rgb), 0.8);
  transform: translateY(-2px);
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}
.avatar:hover {
  transform: scale(1.1) rotate(8deg);
}

.friend-name,
.user-name {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.5px;
  position: relative;
  padding-left: 1rem;
}
.friend-name::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 60%;
  width: 2px;
  /* gradient using secondary → primary */
  background: linear-gradient(to bottom, var(--secondary), var(--primary));
}

.btn-remove,
.btn-request {
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.btn-remove {
  /* accent → primary */
  background: linear-gradient(135deg, var(--accent), var(--primary));
  box-shadow: 0 4px 12px rgba(var(--accent-rgb), 0.3);
}
.btn-request {
  /* secondary → accent */
  background: linear-gradient(135deg, var(--secondary), var(--accent));
  box-shadow: 0 4px 12px rgba(var(--secondary-rgb), 0.3);
}
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}
button:active {
  transform: translateY(1px);
}

.no-friends {
  color: rgba(156, 163, 175, 0.8);
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  margin: 1rem 0;
  border: 1px dashed rgba(255, 255, 255, 0.1);
}

/* Hover glow sweep */
.friend-card::after,
.user-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
    to right,
    transparent 0%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 100%
  );
  transition: left 0.6s ease;
}
.friend-card:hover::after,
.user-card:hover::after {
  left: 100%;
}

/* Scrollbar tinted to your palette */
ul::-webkit-scrollbar-thumb {
  background: linear-gradient(
    to bottom,
    var(--primary),
    var(--secondary)
  );
  border-radius: 4px;
}

/* Responsive tweaks */
@media (max-width: 768px) {
  .friends-list {
    margin: 1rem;
    padding: 1.5rem;
  }
  .avatar {
    width: 48px;
    height: 48px;
  }
  .btn-remove,
  .btn-request {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
