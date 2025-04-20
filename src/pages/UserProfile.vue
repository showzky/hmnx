<template>
    <div v-if="user" class="p-4 max-w-md mx-auto">
      <h1 class="text-2xl font-bold mb-2">
        {{ user.username || user.email }}
      </h1>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p v-if="user.bio"><strong>Bio:</strong> {{ user.bio }}</p>
      <!-- later: avatar, banner, roles, etc. -->
    </div>
    <div v-else class="p-4 text-center">Loading profile…</div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { fetchUsers } from '@/services/userService'
  
  export default {
    setup() {
      const route = useRoute()
      const user = ref(null)
  
      onMounted(async () => {
        const res = await fetchUsers()       // GET /api/users
        // find the one whose id matches the route param
        user.value = res.data.users.find(u => u.id === +route.params.userId)
      })
  
      return { user }
    }
  }
  </script>
  
  <style scoped>
  /* simple padding & centering for now */
  </style>
  