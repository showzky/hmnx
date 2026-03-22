<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <HmnModal :show="show" max-width="480px" @close="$emit('close')">
    <template #header>
      <div class="register-header">
        <div class="register-title">Opprett Konto</div>
        <div class="register-sub">Bli en del av kaoset.</div>
      </div>
    </template>

    <div v-if="status" class="register-status">{{ status }}</div>

    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label class="form-label">E-post</label>
        <input v-model="email" type="email" class="form-input" placeholder="din@epost.no" required autocomplete="email" />
      </div>

      <div class="form-group">
        <label class="form-label">Passord</label>
        <input v-model="password" type="password" class="form-input" placeholder="••••••••" required autocomplete="new-password" />
        <div v-if="password" class="password-strength">
          <div v-for="i in 4" :key="i" class="strength-bar" :class="strengthClass(i)" />
          <span class="strength-label">{{ strengthLabel }}</span>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Bekreft passord</label>
        <input
          v-model="confirmPassword"
          type="password"
          class="form-input"
          :class="{ error: confirmPassword && confirmPassword !== password }"
          placeholder="••••••••"
          required
          autocomplete="new-password"
        />
        <span v-if="confirmPassword && confirmPassword !== password" class="form-error">
          Passordene stemmer ikke
        </span>
      </div>

      <div class="form-checkbox-row">
        <input v-model="acceptedTerms" type="checkbox" class="form-checkbox" required />
        <span class="form-checkbox-label">
          Jeg godtar <router-link to="/tos" @click="$emit('close')">vilkårene</router-link> og eventuelle konsekvenser
        </span>
      </div>

      <button type="submit" class="register-submit" :disabled="loading || !canSubmit">
        {{ loading ? 'Oppretter…' : 'Opprett konto' }}
      </button>
    </form>

    <div class="register-login-link">
      Allerede registrert?
      <a href="#" @click.prevent="$emit('switch-login')">Logg inn</a>
    </div>

    <div class="register-page-link">
      Trenger du mer plass?
      <RouterLink to="/register" @click="$emit('close')">Åpne registreringsside</RouterLink>
    </div>
  </HmnModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import HmnModal from './HmnModal.vue'

defineProps({ show: Boolean })
const emit = defineEmits(['close', 'switch-login'])

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptedTerms = ref(false)
const status = ref('')
const loading = ref(false)

const apiUrl = (() => {
  let url = import.meta.env.VITE_API_URL || ''
  return url.endsWith('/') ? url : url + '/'
})()

const strength = computed(() => {
  const p = password.value
  if (!p) return 0
  let s = 0
  if (p.length >= 6) s++
  if (p.length >= 10) s++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s++
  if (/\d/.test(p) || /[^a-zA-Z0-9]/.test(p)) s++
  return s
})

const strengthLabel = computed(() =>
  ['', 'Svak', 'OK', 'Bra', 'Sterk'][strength.value] || ''
)

function strengthClass(i) {
  if (i > strength.value) return ''
  return ['', 'weak', 'weak', 'medium', 'strong'][strength.value]
}

const canSubmit = computed(() =>
  email.value &&
  password.value &&
  confirmPassword.value === password.value &&
  acceptedTerms.value
)

async function handleRegister() {
  loading.value = true
  status.value = ''
  try {
    await axios.post(apiUrl + 'register', {
      email: email.value,
      password: password.value,
    })
    const { data } = await axios.post(apiUrl + 'login', {
      email: email.value,
      password: password.value,
    })
    auth.login(data.user, data.access_token)
    emit('close')
    router.push('/dashboard')
  } catch {
    status.value = 'Registrering feilet. Prøv igjen.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-header { text-align: center; padding-top: 4px; }
.register-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 900;
  color: var(--text-bright);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.register-sub { font-size: 13px; color: var(--text-muted); font-family: var(--font-ui); }

.register-status {
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
.form-input.error {
  border-color: var(--red2);
  box-shadow: 0 0 0 3px rgba(200,16,46,0.12);
}
.form-error { font-size: 11px; color: var(--red2); font-family: var(--font-ui); }

.password-strength { margin-top: 8px; display: flex; gap: 4px; align-items: center; }
.strength-bar {
  flex: 1;
  height: 3px;
  border-radius: 2px;
  background: var(--border);
  transition: background var(--transition-base);
}
.strength-bar.weak   { background: var(--red2); }
.strength-bar.medium { background: var(--gold); }
.strength-bar.strong { background: var(--green); }
.strength-label {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-ui);
  white-space: nowrap;
  min-width: 50px;
  text-align: right;
}

.form-checkbox-row { display: flex; align-items: flex-start; gap: 10px; margin-top: 16px; }
.form-checkbox {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid var(--border2);
  background: var(--surface2);
  flex-shrink: 0;
  cursor: pointer;
  margin-top: 1px;
  accent-color: var(--cyan);
}
.form-checkbox-label {
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-ui);
  line-height: 1.6;
}
.form-checkbox-label a { color: var(--cyan); text-decoration: none; }

.register-submit {
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
.register-submit:hover { box-shadow: var(--shadow-red2); transform: translateY(-1px); }
.register-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.register-login-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-ui);
}
.register-login-link a { color: var(--cyan); text-decoration: none; font-weight: 500; }

.register-page-link {
  text-align: center;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-ui);
}
.register-page-link a { color: var(--cyan2); text-decoration: none; font-weight: 500; }
.register-page-link a:hover { text-decoration: underline; }
</style>
