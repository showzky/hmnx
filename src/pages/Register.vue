<template>
  <div class="auth-page">
    <div class="auth-shell">
      <div class="auth-panel">
        <div class="auth-head">
          <div class="auth-brand-mark">
            <div class="bmi"><span /><span /><span /></div>
          </div>
          <div class="auth-kicker">Registrering</div>
          <h1 class="auth-title">Opprett Konto</h1>
          <p class="auth-sub">Dette er den fulle registreringsflyten. Modalen kan fortsatt være en rask snarvei.</p>
        </div>

        <div v-if="status" class="auth-status error">
          {{ status }}
        </div>

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
              Jeg godtar <RouterLink to="/tos">vilkårene</RouterLink> og eventuelle konsekvenser
            </span>
          </div>

          <button type="submit" class="auth-submit" :disabled="loading || !canSubmit">
            {{ loading ? 'Oppretter...' : 'Opprett konto' }}
          </button>
        </form>

        <div class="auth-footer">
          Allerede registrert?
          <RouterLink to="/login">Logg inn</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptedTerms = ref(false)
const status = ref('')
const loading = ref(false)

const apiUrl = computed(() => {
  let url = import.meta.env.VITE_API_URL || ''
  if (!url.endsWith('/')) {
    url += '/'
  }
  return url
})

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
    await axios.post(apiUrl.value + 'register', {
      email: email.value,
      password: password.value,
    })

    const { data } = await axios.post(apiUrl.value + 'login', {
      email: email.value,
      password: password.value,
    })

    auth.login(data.user, data.access_token)
    router.push('/dashboard')
  } catch {
    status.value = 'Registrering feilet. Prøv igjen.'
  } finally {
    loading.value = false
  }
}
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

.auth-shell { width: min(100%, 1040px); display: grid; place-items: center; }

.auth-panel {
  width: min(100%, 500px);
  padding: 30px 28px 24px;
  border-radius: 20px;
  background: rgba(15, 23, 32, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
}

.auth-head { text-align: center; margin-bottom: 22px; }
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
  color: var(--red2);
  background: var(--red-bg);
  border: 1px solid var(--red-border);
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

.form-input.error {
  border-color: var(--red2);
  box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.12);
}

.form-error { font-size: 11px; color: var(--red2); font-family: var(--font-ui); }

.password-strength { margin-top: 8px; display: flex; gap: 4px; align-items: center; }
.strength-bar { flex: 1; height: 3px; border-radius: 2px; background: var(--border); transition: background var(--transition-base); }
.strength-bar.weak { background: var(--red2); }
.strength-bar.medium { background: var(--gold); }
.strength-bar.strong { background: var(--green); }
.strength-label { font-size: 10px; color: var(--text-muted); font-family: var(--font-ui); white-space: nowrap; min-width: 50px; text-align: right; }

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

.auth-submit {
  width: 100%;
  margin-top: 20px;
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
