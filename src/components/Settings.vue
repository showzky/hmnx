<template>
  <div class="settings-page">
    <!-- ➜ Page Title -->
    <h1>Innstillinger</h1>
  
    <!-- ➜ Section to update Username -->
    <div class="settings-section">
      <h2>Endre Brukernavn</h2>
      <form @submit.prevent="updateUsername">
        <!-- ➜ Display current username (read-only) -->
        <div class="form-group">
          <label for="current-username">Nåværende Brukernavn:</label>
          <input type="text" id="current-username" :value="currentUser.username" readonly>
        </div>
        <!-- ➜ Input for new username -->
        <div class="form-group">
          <label for="new-username">Nytt Brukernavn:</label>
          <div class="input-with-status">
            <input 
              type="text" 
              id="new-username" 
              v-model="newUsername"
              @input="checkUsernameAvailability"
              :class="{
                'available': usernameStatus === 'available',
                'taken': usernameStatus === 'taken',
                'checking': usernameStatus === 'checking'
              }"
              placeholder="Skriv inn ønsket brukernavn"
            >
            <div class="status-indicator" :class="usernameStatus">
              <span v-if="usernameStatus === 'available'">🟢 Tilgjengelig</span>
              <span v-else-if="usernameStatus === 'taken'">🔴 Opptatt</span>
              <span v-else-if="usernameStatus === 'checking'">⏳ Sjekker...</span>
            </div>
          </div>
        </div>
        <!-- ➜ Submit button -->
        <button type="submit" class="save-button">Lagre Brukernavn</button>
        <!-- ➜ Display success or error message -->
        <div v-if="usernameUpdateMessage" class="message" :class="{'success': usernameUpdateSuccess, 'error': !usernameUpdateSuccess}">
          {{ usernameUpdateMessage }}
        </div>
      </form>
    </div>
  
    <!-- ➜ Section for password change (placeholder) -->
    <div class="settings-section">
      <h2>Endre Passord</h2>
      <p>Funksjonalitet for å endre passord kommer snart.</p>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios';

export default {
  name: 'Settings',
  data() {
    return {
      currentUser: {},             // ➜ Stores fetched user data
      newUsername: '',             // ➜ Model for the new username input
      usernameUpdateMessage: '',   // ➜ Message to display after update attempt
      usernameUpdateSuccess: false, // ➜ Flag for update success or error
      usernameStatus: null,
      debounceTimer: null
    };
  },
  computed: {
    // ➜ Provides easy access to the global auth store
    auth() {
      return useAuthStore();
    },
  },
  methods: {
    // ➜ Navigates to the settings page (if needed in dropdown)
    goToSettings() {
      // This method might be used by your Navbar dropdown. 
      // It navigates to the /settings route.
      this.$router.push('/settings');
    },
    // ➜ Fetches current user data from the backend
    async fetchUserData() {
      try {
        const response = await axios.get('/me');
        this.currentUser = response.data.user;
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    },
    // ➜ Updates the username by sending a request to the backend
    async updateUsername() {
      try {
        const response = await axios.post('/update-profile', { username: this.newUsername });
        this.usernameUpdateMessage = response.data.msg;
        this.usernameUpdateSuccess = true;
        // ➜ Update the auth store by directly setting the user property
        this.auth.user = { ...this.auth.user, username: this.newUsername };
        localStorage.setItem('user', JSON.stringify(this.auth.user));
        // ➜ Optionally clear the input field
        this.newUsername = '';
        // ➜ Re-fetch user data to update the displayed current username
        this.fetchUserData();
      } catch (error) {
        console.error('Error updating username:', error);
        this.usernameUpdateMessage = error.response?.data?.msg || 'Failed to update username.';
        this.usernameUpdateSuccess = false;
      } finally {
        setTimeout(() => {
          this.usernameUpdateMessage = '';
        }, 3000);
      }
    },
    async checkUsernameAvailability() {
      if (!this.newUsername) {
        this.usernameStatus = null;
        return;
      }

      // Clear previous timer
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }

      // Set checking status
      this.usernameStatus = 'checking';

      // Debounce the API call
      this.debounceTimer = setTimeout(async () => {
        try {
          const response = await axios.post('/check-username', { username: this.newUsername });
          this.usernameStatus = response.data.available ? 'available' : 'taken';
        } catch (error) {
          console.error('Error checking username:', error);
          this.usernameStatus = null;
        }
      }, 500);
    },
    // ➜ (Placeholder for password change functionality)
    // async changePassword() { ... },
  },
  mounted() {
    // ➜ Fetch the current user data when the component is mounted
    this.fetchUserData();
  },
};
</script>

<style scoped>
.settings-page {
  padding: 30px 20px;
  max-width: 800px;
  margin: 0 auto;
}

.settings-section {
  margin-bottom: 30px;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

h1 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #2c3e50;
  font-weight: 600;
}

h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #34495e;
  padding-bottom: 12px;
  border-bottom: 2px solid #ecf0f1;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-size: 0.9em;
  font-weight: 500;
}

.input-with-status {
  position: relative;
  width: 100%;
}

input[type="text"] {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #fff;
}

input[type="text"]:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
}

input[readonly] {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

/* Status indicator styles */
.status-indicator {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-indicator.available {
  color: #2e7d32;
}

.status-indicator.taken {
  color: #c62828;
}

.status-indicator.checking {
  color: #f57c00;
}

/* Input status styles */
input.available {
  border-color: #2e7d32;
}

input.taken {
  border-color: #c62828;
}

input.checking {
  border-color: #f57c00;
}

.save-button {
  margin-top: 16px;
  padding: 12px 24px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
  width: 100%;
}

.save-button:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.message {
  margin-top: 16px;
  padding: 14px;
  border-radius: 8px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: fadeIn 0.3s ease-out;
}

.message.success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.message.error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Dark mode styles */
:root.dark-mode .input-with-status input {
  background-color: #2d3748;
  border-color: #4a5568;
  color: #fff;
}

:root.dark-mode .input-with-status input:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66,153,225,0.1);
}

:root.dark-mode .message.success {
  background-color: #2f5233;
  color: #a5d6a7;
  border-color: #4caf50;
}

:root.dark-mode .message.error {
  background-color: #4a1f1f;
  color: #ef9a9a;
  border-color: #f44336;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .status-indicator {
    position: static;
    margin-top: 8px;
    display: block;
  }
}
</style>
  