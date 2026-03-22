<template>
  <div class="auth-page">
    <div class="auth-shell">
      <div class="auth-panel">
        <div class="auth-head">
          <div class="auth-brand-mark">
            <div class="bmi"><span /><span /><span /></div>
          </div>
          <div class="auth-kicker">Innlogging</div>
          <h1 class="auth-title">Logg Inn</h1>
          <p class="auth-sub">Discord callback, vanlige innlogginger og feilmeldinger samles her.</p>
        </div>

        <div v-if="status" class="auth-status" :class="statusTone">
          {{ status }}
        </div>

        <form v-if="!oauthLoading" @submit.prevent="handleLogin">
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

          <button type="submit" class="auth-submit" :disabled="loading">
            {{ loading ? 'Logger inn...' : 'Logg inn' }}
          </button>
        </form>

        <div class="form-divider">eller</div>

        <button class="discord-btn" type="button" :disabled="oauthLoading" @click="handleDiscordLogin">
          <i class="fab fa-discord"></i> Logg inn med Discord
        </button>

        <div class="auth-footer">
          Ikke registrert?
          <RouterLink to="/register">Opprett ny konto</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const status = ref('')
const statusTone = ref('error')
const loading = ref(false)
const oauthLoading = ref(false)

const apiUrl = computed(() => {
  let url = import.meta.env.VITE_API_URL || ''
  if (!url.endsWith('/')) {
    url += '/'
  }
  return url
})

async function handleLogin() {
  loading.value = true
  status.value = ''

  try {
    const { data } = await axios.post(apiUrl.value + 'login', {
      email: email.value,
      password: password.value,
    })

    auth.login(data.user, data.access_token)
    router.push('/dashboard')
  } catch {
    statusTone.value = 'error'
    status.value = 'Feil e-post eller passord. Prøv igjen.'
  } finally {
    loading.value = false
  }
}

function handleDiscordLogin() {
  window.location.href = apiUrl.value + 'login/discord'
}

onMounted(async () => {
  if (route.query.error) {
    statusTone.value = 'error'
    status.value = 'Discord-innlogging feilet. Sjekk callback-URL og prøv igjen.'
  }

  if (route.query.token) {
    oauthLoading.value = true
    statusTone.value = 'info'
    status.value = 'Logger deg inn med Discord...'

    const token = Array.isArray(route.query.token) ? route.query.token[0] : route.query.token
    const user = await auth.hydrateFromToken(token)

    if (user) {
      router.replace('/dashboard')
      return
    }

    oauthLoading.value = false
    statusTone.value = 'error'
    status.value = 'Kunne ikke fullføre Discord-innloggingen.'
  }
})
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 160px);
  background:
    radial-gradient(circle at top, rgba(0, 184, 208, 0.08), transparent 34%),
    linear-gradient(180deg, #060a0f 0%, #0a1119 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.auth-shell {
  width: min(100%, 1040px);
  display: grid;
  place-items: center;
}

.auth-panel {
  width: min(100%, 460px);
  padding: 30px 28px 24px;
  border-radius: 20px;
  background: rgba(15, 23, 32, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
}

.auth-head {
  text-align: center;
  margin-bottom: 22px;
}

.auth-brand-mark {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  border-radius: 12px;
  background: linear-gradient(145deg, var(--red), #7a0e1e);
  box-shadow: 0 0 22px var(--red-glow);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bmi { display: flex; flex-direction: column; gap: 3px; align-items: center; }
.bmi span { display: block; background: white; height: 2px; border-radius: 1px; }
.bmi span:nth-child(1) { width: 14px; }
.bmi span:nth-child(2) { width: 8px; align-self: flex-start; margin-left: 5px; }
.bmi span:nth-child(3) { width: 14px; }

.auth-kicker {
  color: var(--cyan);
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.auth-title {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 900;
  color: var(--text-bright);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  line-height: 1;
  margin: 0 0 10px;
}

.auth-sub {
  margin: 0;
  color: var(--text-muted);
  font-family: var(--font-ui);
  font-size: 14px;
  line-height: 1.6;
}

.auth-status {
  padding: 11px 14px;
  border-radius: var(--r-sm);
  margin-bottom: 16px;
  text-align: center;
  font-family: var(--font-ui);
  font-size: 13px;
}

.auth-status.error {
  color: var(--red2);
  background: var(--red-bg);
  border: 1px solid var(--red-border);
}

.auth-status.info {
  color: var(--cyan);
  background: rgba(0, 184, 208, 0.08);
  border: 1px solid rgba(0, 184, 208, 0.18);
}

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-label {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.form-input {
  width: 100%;
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: var(--r-md);
  padding: 12px 14px;
  font-size: 14px;
  color: var(--text-bright);
  font-family: var(--font-ui);
  outline: none;
  transition: all var(--transition-fast);
}

.form-input::placeholder { color: var(--text-muted); }
.form-input:hover { border-color: var(--border3); }
.form-input:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 0 3px rgba(0, 184, 208, 0.12);
  background: var(--surface3);
}

.auth-submit {
  width: 100%;
  margin-top: 8px;
  padding: 12px;
  border: none;
  border-radius: var(--r-md);
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  color: white;
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 15px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--shadow-red);
  transition: all var(--transition-base);
}

.auth-submit:hover { box-shadow: var(--shadow-red2); transform: translateY(-1px); }
.auth-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

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

.discord-btn:hover { background: rgba(88, 101, 242, 0.25); }
.discord-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.auth-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-ui);
}

.auth-footer a {
  color: var(--cyan);
  text-decoration: none;
  font-weight: 600;
}

.auth-footer a:hover { text-decoration: underline; }
</style>
