<template>
  <div class="ev2-page">
    <div class="hmn-container">

      <!-- Hero banner -->
      <div class="ev2-hero">
        <div class="ev2-hero-tag">HENDELSE</div>
        <h1 class="ev2-title">{{ eventTitle }}</h1>
        <div class="ev2-meta-row">
          <div class="ev2-meta-chip">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ formatDate(eventDate) }}
          </div>
          <div class="ev2-meta-chip">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ eventTime }}
          </div>
          <div v-if="eventLocation" class="ev2-meta-chip">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            {{ eventLocation }}
          </div>
          <div class="ev2-status-chip" :class="isPast ? 'past' : isToday ? 'today' : 'upcoming'">
            {{ isPast ? 'Avsluttet' : isToday ? 'I dag' : 'Kommende' }}
          </div>
        </div>
      </div>

      <div class="ev2-layout">
        <div class="ev2-main">

          <!-- Countdown -->
          <div v-if="showCountdown && !isPast" class="ev2-card ev2-countdown-card">
            <div class="ev2-card-label">NEDTELLING</div>
            <div class="ev2-countdown">
              <div class="ev2-cd-unit">
                <span class="ev2-cd-num">{{ countdown.days }}</span>
                <span class="ev2-cd-label">Dager</span>
              </div>
              <span class="ev2-cd-sep">:</span>
              <div class="ev2-cd-unit">
                <span class="ev2-cd-num">{{ countdown.hours }}</span>
                <span class="ev2-cd-label">Timer</span>
              </div>
              <span class="ev2-cd-sep">:</span>
              <div class="ev2-cd-unit">
                <span class="ev2-cd-num">{{ countdown.minutes }}</span>
                <span class="ev2-cd-label">Min</span>
              </div>
              <span class="ev2-cd-sep">:</span>
              <div class="ev2-cd-unit">
                <span class="ev2-cd-num">{{ countdown.seconds }}</span>
                <span class="ev2-cd-label">Sek</span>
              </div>
            </div>
          </div>

          <div v-if="isPast && showCountdown" class="ev2-card ev2-ended-card">
            <div class="ev2-ended-text">Denne hendelsen er over.</div>
          </div>

          <!-- Description -->
          <div v-if="eventDescription" class="ev2-card">
            <div class="ev2-card-label">OM HENDELSEN</div>
            <p class="ev2-desc">{{ eventDescription }}</p>
          </div>

          <!-- Warning -->
          <div v-if="eventWarning" class="ev2-card ev2-warn-card">
            <div class="ev2-card-label ev2-warn-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              VIKTIG
            </div>
            <p class="ev2-warn-text">{{ eventWarning }}</p>
          </div>

        </div>

        <!-- Sidebar -->
        <div class="ev2-sidebar">

          <!-- Sign up -->
          <div class="ev2-card ev2-signup-card">
            <div class="ev2-card-label">MELD DEG PÅ</div>
            <p class="ev2-signup-sub">Sikre plassen din til hendelsen.</p>
            <form @submit.prevent="signUpForEvent" class="ev2-form">
              <input
                type="email"
                class="ev2-input"
                v-model="signupEmail"
                placeholder="din@epost.no"
                required
              />
              <button type="submit" class="ev2-btn">
                Meld på
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              </button>
            </form>
            <p v-if="signupSuccess" class="ev2-signup-ok">Du er påmeldt!</p>
          </div>

          <!-- Details -->
          <div class="ev2-card ev2-details-card">
            <div class="ev2-card-label">DETALJER</div>
            <div class="ev2-detail-row">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              <span>{{ formatDate(eventDate) }}</span>
            </div>
            <div class="ev2-detail-row">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span>{{ eventTime }}</span>
            </div>
            <div v-if="eventLocation" class="ev2-detail-row">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>{{ eventLocation }}</span>
            </div>
            <div v-if="eventContactEmail" class="ev2-detail-row">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <a :href="`mailto:${eventContactEmail}`" class="ev2-contact-link">{{ eventContactEmail }}</a>
            </div>
            <div v-if="eventPhoneNumber" class="ev2-detail-row">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13 19.79 19.79 0 0 1 1.61 4.38 2 2 0 0 1 3.58 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 9.91a16 16 0 0 0 6.06 6.06l1.57-1.57a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <span>{{ eventPhoneNumber }}</span>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'Template2',
  props: {
    eventTitle:        { type: String, required: true },
    eventDate:         { type: String, required: true },
    eventTime:         { type: String, required: true },
    eventDescription:  { type: String, default: '' },
    eventLocation:     { type: String, default: '' },
    eventPhoneNumber:  { type: String, default: '' },
    eventWarning:      { type: String, default: '' },
    eventContactEmail: { type: String, default: '' },
    showCountdown:     { type: Boolean, default: false },
  },
  data() {
    return {
      signupEmail: '',
      signupSuccess: false,
      countdown: { days: '00', hours: '00', minutes: '00', seconds: '00' },
      _timer: null,
    };
  },
  computed: {
    eventDateTime() {
      if (!this.eventDate || !this.eventTime) return null;
      return new Date(`${this.eventDate}T${this.eventTime}`);
    },
    isPast() {
      if (!this.eventDateTime) return false;
      return this.eventDateTime < new Date();
    },
    isToday() {
      if (!this.eventDateTime) return false;
      const today = new Date();
      const d = this.eventDateTime;
      return d.getFullYear() === today.getFullYear() &&
             d.getMonth() === today.getMonth() &&
             d.getDate() === today.getDate();
    },
  },
  mounted() {
    if (this.showCountdown) {
      this.tick();
      this._timer = setInterval(this.tick, 1000);
    }
  },
  beforeUnmount() {
    if (this._timer) clearInterval(this._timer);
  },
  methods: {
    tick() {
      const target = this.eventDateTime;
      if (!target) return;
      const diff = target - new Date();
      if (diff <= 0) {
        this.countdown = { days: '00', hours: '00', minutes: '00', seconds: '00' };
        clearInterval(this._timer);
        return;
      }
      const pad = n => String(Math.floor(n)).padStart(2, '0');
      this.countdown = {
        days:    pad(diff / 86400000),
        hours:   pad((diff % 86400000) / 3600000),
        minutes: pad((diff % 3600000) / 60000),
        seconds: pad((diff % 60000) / 1000),
      };
    },
    signUpForEvent() {
      console.log('Signup:', this.signupEmail);
      this.signupSuccess = true;
      this.signupEmail = '';
      setTimeout(() => { this.signupSuccess = false; }, 4000);
    },
    formatDate(raw) {
      if (!raw) return '';
      const d = new Date(raw);
      if (isNaN(d)) return raw;
      return d.toLocaleDateString('nb-NO', { year: 'numeric', month: 'long', day: 'numeric' });
    },
  },
};
</script>

<style scoped>
.ev2-page {
  padding: 60px 0 80px;
  min-height: 80vh;
}

/* Hero */
.ev2-hero {
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border);
}
.ev2-hero-tag {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 10px;
}
.ev2-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 900;
  text-transform: uppercase;
  color: var(--text-bright);
  line-height: 1;
  margin: 0 0 18px;
  letter-spacing: 0.02em;
}
.ev2-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.ev2-meta-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border2);
  font-family: 'Barlow', sans-serif;
  font-size: 12px;
  color: var(--text-muted);
}
.ev2-meta-chip svg { opacity: 0.55; flex-shrink: 0; }
.ev2-status-chip {
  padding: 4px 12px;
  border-radius: 999px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.ev2-status-chip.upcoming { background: rgba(0,184,208,0.1); color: var(--cyan); border: 1px solid rgba(0,184,208,0.2); }
.ev2-status-chip.today    { background: rgba(34,197,94,0.1);  color: #4ade80;     border: 1px solid rgba(34,197,94,0.2); }
.ev2-status-chip.past     { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px solid var(--border); }

/* Layout */
.ev2-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  align-items: start;
}
@media (max-width: 760px) {
  .ev2-layout { grid-template-columns: 1fr; }
}

/* Cards */
.ev2-card {
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px 22px;
  margin-bottom: 12px;
}
.ev2-card:last-child { margin-bottom: 0; }
.ev2-card-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 14px;
}

/* Countdown */
.ev2-countdown-card {
  border-color: rgba(0,184,208,0.2);
  background: rgba(0,184,208,0.04);
}
.ev2-countdown {
  display: flex;
  align-items: center;
  gap: 6px;
}
.ev2-cd-unit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
  background: rgba(0,0,0,0.25);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 14px 8px;
}
.ev2-cd-num {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: clamp(28px, 4vw, 44px);
  font-weight: 900;
  color: var(--cyan);
  line-height: 1;
  letter-spacing: 0.04em;
}
.ev2-cd-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.ev2-cd-sep {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 28px;
  font-weight: 900;
  color: var(--border2);
  line-height: 1;
  padding-bottom: 18px;
}

/* Ended */
.ev2-ended-card {
  border-color: rgba(255,255,255,0.08);
}
.ev2-ended-text {
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  color: var(--text-muted);
}

/* Description */
.ev2-desc {
  font-family: 'Barlow', sans-serif;
  font-size: 14px;
  color: var(--text);
  line-height: 1.75;
  margin: 0;
}

/* Warning */
.ev2-warn-card {
  border-color: rgba(239,68,68,0.2);
  background: rgba(239,68,68,0.04);
}
.ev2-warn-label {
  color: #f87171;
  display: flex;
  align-items: center;
  gap: 5px;
}
.ev2-warn-text {
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  color: #fca5a5;
  margin: 0;
  line-height: 1.6;
}

/* Signup */
.ev2-signup-card {
  border-color: rgba(0,184,208,0.18);
  background: rgba(0,184,208,0.03);
}
.ev2-signup-sub {
  font-family: 'Barlow', sans-serif;
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 14px;
}
.ev2-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ev2-input {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border2);
  border-radius: 6px;
  padding: 9px 12px;
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  color: var(--text);
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
  box-sizing: border-box;
}
.ev2-input:focus { border-color: var(--cyan); }
.ev2-input::placeholder { color: var(--text-muted); }
.ev2-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--cyan);
  color: #000;
  border: none;
  border-radius: 6px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity 0.15s;
  width: 100%;
}
.ev2-btn:hover { opacity: 0.85; }
.ev2-signup-ok {
  font-family: 'Barlow', sans-serif;
  font-size: 12px;
  color: #4ade80;
  margin: 8px 0 0;
}

/* Details */
.ev2-details-card { }
.ev2-detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  color: var(--text-muted);
  padding: 6px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.ev2-detail-row:last-child { border-bottom: none; }
.ev2-detail-row svg { opacity: 0.45; flex-shrink: 0; }
.ev2-contact-link {
  color: var(--cyan);
  text-decoration: none;
}
.ev2-contact-link:hover { text-decoration: underline; }
</style>
