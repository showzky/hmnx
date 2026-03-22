<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <HmnModal :show="show" max-width="420px" @close="$emit('close')">
    <template #header>
      <div class="login-header">
        <div class="login-brand-mark">
          <div class="bmi"><span /><span /><span /></div>
        </div>
        <div class="login-title">Logg Inn</div>
        <div class="login-sub">Velkommen tilbake, pasient.</div>
      </div>
    </template>

    <div v-if="status" class="login-status">{{ status }}</div>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label class="form-label">E-post</label>
        <input
          v-model="email"
          type="email"
          class="form-input"
          placeholder="din@epost.no"
          required
          autocomplete="email"
        />
      </div>
      <div class="form-group">
        <label class="form-label">Passord</label>
        <input
          v-model="password"
          type="password"
          class="form-input"
          placeholder="••••••••"
          required
          autocomplete="current-password"
        />
      </div>
      <button type="submit" class="login-submit" :disabled="loading">
        {{ loading ? 'Logger inn…' : 'Logg inn' }}
      </button>
    </form>

    <div class="form-divider">eller</div>

    <button class="discord-btn" @click="handleDiscordLogin">
      <i class="fab fa-discord"></i> Logg inn med Discord
    </button>

    <div class="login-register-link">
      Ikke registrert?
      <a href="#" @click.prevent="$emit('switch-register')">Opprett ny konto</a>
    </div>

    <div class="login-page-link">
      Foretrekker full side?
      <RouterLink to="/login" @click="$emit('close')">Åpne innloggingsside</RouterLink>
    </div>
  </HmnModal>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import HmnModal from './HmnModal.vue'

defineProps({ show: Boolean })
const emit = defineEmits(['close', 'switch-register'])

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const status = ref('')
const loading = ref(false)

const apiUrl = (() => {
  let url = import.meta.env.VITE_API_URL || ''
  return url.endsWith('/') ? url : url + '/'
})()

async function handleLogin() {
  loading.value = true
  status.value = ''
  try {
    const { data } = await axios.post(apiUrl + 'login', {
      email: email.value,
      password: password.value,
    })
    auth.login(data.user, data.access_token)
    emit('close')
    router.push('/dashboard')
  } catch {
    status.value = 'Feil e-post eller passord. Prøv igjen.'
  } finally {
    loading.value = false
  }
}

function handleDiscordLogin() {
  window.location.href = apiUrl + 'login/discord'
}
</script>

<style scoped>
.login-header { text-align: center; padding-top: 8px; }

.login-brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(145deg, var(--red), #7a0e1e);
  box-shadow: 0 0 20px var(--red-glow);
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bmi { display: flex; flex-direction: column; gap: 3px; align-items: center; }
.bmi span { display: block; background: white; height: 2px; border-radius: 1px; }
.bmi span:nth-child(1) { width: 14px; }
.bmi span:nth-child(2) { width: 8px; align-self: flex-start; margin-left: 5px; }
.bmi span:nth-child(3) { width: 14px; }

.login-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 900;
  color: var(--text-bright);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.login-sub { font-size: 13px; color: var(--text-muted); font-family: var(--font-ui); }

.login-status {
  background: var(--red-bg);
  border: 1px solid var(--red-border);
  border-radius: var(--r-sm);
  padding: 10px 14px;
  font-size: 13px;
  color: var(--red2);
  font-family: var(--font-ui);
  margin-bottom: 16px;
  text-align: center;
}

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-group:last-of-type { margin-bottom: 0; }

.form-label {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.form-input {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: var(--r-md);
  padding: 11px 14px;
  font-size: 14px;
  color: var(--text-bright);
  font-family: var(--font-ui);
  width: 100%;
  transition: all var(--transition-fast);
  outline: none;
}
.form-input::placeholder { color: var(--text-muted); }
.form-input:hover { border-color: var(--border3); }
.form-input:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 0 3px rgba(0,184,208,0.12);
  background: var(--surface3);
}

.login-submit {
  width: 100%;
  padding: 12px;
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  color: white;
  border: none;
  border-radius: var(--r-md);
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 15px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--shadow-red);
  transition: all var(--transition-base);
  margin-top: 20px;
}
.login-submit:hover { box-shadow: var(--shadow-red2); transform: translateY(-1px); }
.login-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.form-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0;
  color: var(--text-muted);
  font-size: 12px;
  font-family: var(--font-ui);
}
.form-divider::before,
.form-divider::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.discord-btn {
  width: 100%;
  padding: 11px;
  background: var(--discord-bg);
  border: 1px solid var(--discord-border);
  border-radius: var(--r-md);
  color: var(--discord-text);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.discord-btn:hover { background: rgba(88,101,242,0.25); }

.login-register-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-ui);
}
.login-register-link a { color: var(--cyan); text-decoration: none; font-weight: 500; }
.login-register-link a:hover { text-decoration: underline; }

.login-page-link {
  text-align: center;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-ui);
}
.login-page-link a { color: var(--cyan2); text-decoration: none; font-weight: 500; }
.login-page-link a:hover { text-decoration: underline; }
</style>
