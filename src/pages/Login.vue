<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h1>🩺 Doc's Lounge</h1>
      <p class="subtitle">Login for medical mischief makers</p>
      <form @submit.prevent="login">
        <div class="input-group">
          <input type="text" v-model="username" placeholder="Physician ID" />
          <span class="icon">👨⚕️</span>
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Secret Serum" />
          <span class="icon">💉</span>
        </div>
        <button type="submit">Administer Login</button>
      </form>
      <p class="disclaimer">
        Warning: Side effects may include unlimited laughter and occasional bad puns
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import axios from 'axios'; // Adjust if you use your own axios instance.
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';

export default {
  name: 'Login',
  setup() {
    // Reactive variables for login data
    const username = ref('');
    const password = ref('');

    // Global auth store and router
    const auth = useAuthStore();
    const router = useRouter();

    // Computed property to ensure the API URL ends with a trailing slash.
    const apiUrl = computed(() => {
      let url = import.meta.env.VITE_API_URL || '';
      if (!url.endsWith('/')) {
        url += '/';
      }
      return url;
    });

    // Function to handle login
    async function login() {
      try {
        // Build the login URL from the computed apiUrl
        const loginUrl = apiUrl.value + 'login';
        const response = await axios.post(loginUrl, {
          email: username.value, // assuming your API uses email as the identifier
          password: password.value,
        });

        // Extract access token and user data from the response
        const { access_token, user } = response.data;

        // Update auth store with user data and token
        auth.login(user, access_token);

        // Navigate to dashboard after successful login
        router.push('/dashboard');
      } catch (error) {
        console.error('Login error:', error.response ? error.response.data : error);
      }
    }

    return {
      username,
      password,
      login,
    };
  },
};
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('@/assets/background-images/medical.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  backdrop-filter: blur(2px);
}

.login-container {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem 3rem;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(0, 102, 204, 0.2);
  max-width: 450px;
  width: 90%;
  transform: translateY(-10%);
  border: 3px solid #0077cc;
  position: relative;
}

.login-container::before {
  content: '⚕';
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.5rem;
  color: #0077cc;
}

h1 {
  color: #0077cc;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-style: italic;
}

.input-group {
  position: relative;
  margin-bottom: 1.5rem;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #99ccff;
  border-radius: 25px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f0f9ff;
}

input:focus {
  outline: none;
  border-color: #0077cc;
  box-shadow: 0 0 10px rgba(0, 119, 204, 0.3);
}

.icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
}

button[type="submit"] {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #0077cc, #00a8e8);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

button[type="submit"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 119, 204, 0.4);
  background: linear-gradient(135deg, #00a8e8, #0077cc);
}

.disclaimer {
  text-align: center;
  font-size: 0.8rem;
  color: #666;
  margin-top: 1.5rem;
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
}
</style>
