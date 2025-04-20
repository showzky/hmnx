<template>
  <!-- The modal overlay covers the entire viewport. Clicking outside the modal content triggers hideModal -->
  <div class="modal-overlay" @click.self="hideModal">
    <div class="modal-content">
      <!-- Close Button -->
      <span class="close-btn" @click="hideModal">&times;</span>
      
      <!-- Header -->
      <h2 v-if="!isRegistering">Logg inn</h2>
      <h2 v-else>Opprett ny konto</h2>
      
      <!-- Authentication Form -->
      <form @submit.prevent="handleSubmit" class="auth-form">
        <input
          id="email"
          name="email"
          v-model="email"
          type="email"
          placeholder="E-post"
          required
          autocomplete="email"
        />
        <input
          id="password"
          name="password"
          v-model="password"
          type="password"
          placeholder="Passord"
          required
          autocomplete="new-password"
        />
        <!-- Confirm Password (only in registration mode) -->
        <input
          v-if="isRegistering"
          id="confirmPassword"
          name="confirmPassword"
          v-model="confirmPassword"
          type="password"
          placeholder="Bekreft passord"
          required
          autocomplete="new-password"
        />
        <button type="submit">
          {{ isRegistering ? 'Registrer konto' : 'Logg inn' }}
        </button>
      </form>
      
      <!-- Social Login Options -->
      <div class="social-login">
        <button class="google-btn">Logg inn med Google</button>
        <button class="discord-btn" @click="handleDiscordLogin">Logg inn med Discord</button>
      </div>
      
      <!-- Divider -->
      <div class="auth-divider"></div>
      
      <!-- Toggle between Login and Registration -->
      <div class="toggle-auth">
        <span v-if="!isRegistering">
          Ikke registrert? 
          <button type="button" @click="toggleAuthMode">Opprett ny konto</button>
        </span>
        <span v-else>
          Allerede registrert? 
          <button type="button" @click="toggleAuthMode">Logg inn</button>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

export default {
  name: 'LoginModal',
  data() {
    return {
      isRegistering: false,
      email: '',
      password: '',
      confirmPassword: '' // Used only in registration mode
    }
  },
  computed: {
    // Ensure the API URL always ends with a trailing slash
    apiUrl() {
      let url = import.meta.env.VITE_API_URL || ''
      if (!url.endsWith('/')) {
        url += '/'
      }
      return url
    }
  },
  methods: {
    // Hide the modal by emitting an event to the parent component
    hideModal() {
      this.$emit('hide-login')
    },
    // Toggle between login and registration modes and clear password fields
    toggleAuthMode() {
      this.isRegistering = !this.isRegistering
      this.password = ''
      this.confirmPassword = ''
    },
    // Discord Login: redirect to the Discord OAuth endpoint using the computed apiUrl
    handleDiscordLogin() {
      window.location.href = this.apiUrl + 'login/discord'
    },
    // Handle form submission for login/registration
    async handleSubmit() {
      const auth = useAuthStore()
      try {
        if (this.isRegistering) {
          if (this.password !== this.confirmPassword) {
            alert('Passordene stemmer ikke overens. Vennligst prøv igjen.')
            return
          }
          // Register the user
          await axios.post(this.apiUrl + 'register', {
            email: this.email,
            password: this.password
          })
          // Log in the user automatically
          const loginResponse = await axios.post(this.apiUrl + 'login', {
            email: this.email,
            password: this.password
          })
          const token = loginResponse.data.access_token
          const user = loginResponse.data.user
          auth.login(user, token)
        } else {
          // Login mode
          const loginResponse = await axios.post(this.apiUrl + 'login', {
            email: this.email,
            password: this.password
          })
          const token = loginResponse.data.access_token
          const user = loginResponse.data.user
          auth.login(user, token)
        }
        // Hide modal and navigate to the dashboard
        this.hideModal()
        this.$router.push('/dashboard')
      } catch (error) {
        console.error('Login error:', error)
        alert('En feil oppstod under autentisering. Vennligst prøv igjen.')
      }
    }
  }
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  justify-content: center;
  align-items: center;
}

/* Modal Content */
.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  position: relative;
}

/* Close Button */
.close-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Form Styling */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}

.auth-form input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.auth-form button {
  background-color: #3498db;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

/* Social Login Buttons */
.social-login {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.google-btn,
.discord-btn {
  padding: 0.75rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
}

.google-btn {
  background-color: #db4437;
}

.discord-btn {
  background-color: #7289da;
}

/* Divider */
.auth-divider {
  border-top: 1px solid #ddd;
  margin: 1rem 0;
}

/* Toggle Authentication */
.toggle-auth {
  text-align: center;
  font-size: 0.9rem;
}

.toggle-auth button {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  text-decoration: underline;
}

/* Dark Mode Styles */
:root.dark-mode .modal-content {
  background: #1a1a1a;
  color: #ffffff;
}

:root.dark-mode .auth-form input {
  background-color: #2d2d2d;
  border-color: #404040;
  color: #ffffff;
}

:root.dark-mode .auth-form input::placeholder {
  color: #a0a0a0;
}

:root.dark-mode .auth-divider {
  border-color: #404040;
}

:root.dark-mode .toggle-auth {
  color: #ffffff;
}

:root.dark-mode .toggle-auth button {
  color: #3498db;
}

:root.dark-mode .close-btn {
  color: #ffffff;
}
</style>
