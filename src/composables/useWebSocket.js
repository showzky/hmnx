import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

export function useWebSocket(url = import.meta.env.VITE_SOCKET_URL) {
  const socket = ref(null);
  const isConnected = ref(false);
  const defaultMessage = 'System maintenance in progress. Please try again later.';
  const maintenanceStatus = ref({
    isActive: false,
    message: '',
    title: '',
    updatedAt: '',
    ref: ''
  });

  // Initial HTTP fetch for maintenance status
  const fetchMaintenanceStatus = async () => {
    try {
      console.log('🔍 Fetching initial maintenance status...');
      const response = await fetch('/api/notice-maintenance');
      const data = await response.json();
      console.log('📥 Received initial maintenance data:', data);
      updateMaintenanceStatus(data);
    } catch (error) {
      console.error('Failed to fetch initial maintenance status:', error);
    }
  };

  const updateMaintenanceStatus = (data) => {
    console.log('🔄 Updating maintenance status with:', data);
    maintenanceStatus.value = {
      isActive: data.notice_maintenance_mode === 'on',
      message: data.notice_maintenance_message || defaultMessage,
      title: data.notice_maintenance_title || 'Driftsmelding',
      updatedAt: data.notice_maintenance_updated_at || '',
      ref: data.notice_maintenance_ref || ''
    };
    console.log('✨ New maintenance status:', maintenanceStatus.value);
  };

  const connect = () => {
    if (!url) {
      console.error('No WebSocket URL provided.');
      return;
    }

    console.log('🔌 Connecting to WebSocket at:', url);
    
    socket.value = io(url, {
      path: '/socket.io',
      transports: ['websocket'],
      withCredentials: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    socket.value.on('connect', () => {
      console.log('✅ WebSocket connected:', socket.value.id);
      isConnected.value = true;
      // Request maintenance status after connection
      socket.value.emit('request_maintenance_status');
    });

    socket.value.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      isConnected.value = false;
    });

    socket.value.on('disconnect', (reason) => {
      console.warn('🔌 WebSocket disconnected:', reason);
      isConnected.value = false;
    });

    // Listen for maintenance status updates
    socket.value.on('maintenance_status', (data) => {
      console.log('🔔 Received maintenance status:', data);
      updateMaintenanceStatus(data);
    });

    socket.value.on('reconnect', (attemptNumber) => {
      console.log('🔄 WebSocket reconnected after', attemptNumber, 'attempts');
      isConnected.value = true;
      socket.value.emit('request_maintenance_status');
    });
  };

  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect();
      console.log('🔌 WebSocket manually disconnected');
      socket.value = null;
      isConnected.value = false;
    }
  };

  onMounted(() => {
    // First fetch initial status via HTTP
    fetchMaintenanceStatus();
    // Then establish WebSocket connection
    connect();
  });

  onUnmounted(() => {
    disconnect();
  });

  return {
    socket,
    isConnected,
    maintenanceStatus,
    connect,
    disconnect,
    fetchMaintenanceStatus
  };
}
