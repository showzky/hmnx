// stores/useWebSocket.js
import { ref, onMounted, onBeforeUnmount } from 'vue';
import io from 'socket.io-client';
import { useAuthStore } from '@/stores/auth';

export function useWebSocket() {
  const auth = useAuthStore();

  // Use environment variable for production vs. development
  const apiBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
  const SOCKET_URL =
    (import.meta.env.VITE_SOCKET_URL || '').replace(/\/$/, '') ||
    (apiBase.endsWith('/api') ? apiBase.slice(0, -4) : apiBase) ||
    'http://localhost:5000';
  const socket = io(SOCKET_URL);

  const handleRoleUpdate = (newRoleData) => {
    if (auth.user?.id === newRoleData.userId) {
      auth.user.roles = newRoleData.roles;
      console.log('User roles updated:', newRoleData.roles);
    }
  };

  onMounted(() => {
    socket.on('roleUpdate', handleRoleUpdate);
  });

  onBeforeUnmount(() => {
    socket.off('roleUpdate', handleRoleUpdate);
    socket.disconnect();
  });

  return { socket };
}
