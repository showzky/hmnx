<template>
  <section class="settings-admin settings-ref">
    <div class="settings-page-head">
      <div class="settings-page-title">Inn<em>stillinger</em></div>
      <div class="settings-page-sub">
        Globale sideinnstillinger. Endre med forsiktighet. Thomas har skylda uansett.
      </div>
    </div>

    <div class="settings-section">
      <div class="settings-section-label">Generelt</div>
      <div class="settings-panel">
        <div class="settings-input-row">
          <label class="settings-form-label" for="site-name">Sitenavn</label>
          <input
            id="site-name"
            v-model="siteName"
            class="settings-form-input"
            type="text"
          />
          <div class="settings-form-hint">
            Vises i nettleser-fanen og overst i admin-panelet.
          </div>
        </div>

        <div class="settings-input-row">
          <label class="settings-form-label" for="banner-message">Driftsmelding</label>
          <textarea
            id="banner-message"
            v-model="operationsMessage"
            class="settings-form-textarea"
            rows="2"
          ></textarea>
          <div class="settings-inline-actions">
            <button class="btn btn-red btn-sm" type="button" @click="confirmDriftsmelding">
              Bekreft driftsmelding
            </button>
          </div>
          <div class="settings-form-hint">
            Vises i den rode bannerbaren overst pa alle sider. Hold den kort og tydelig.
          </div>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="settings-section-label">Tilgangskontroll</div>
      <div class="settings-panel">
        <div class="settings-row">
          <div class="settings-info">
            <div class="settings-title">Registrering apen</div>
            <div class="settings-desc">
              Lar nye brukere opprette konto. Skru av for a lukke portalen, ingen nye pasienter slipper inn.
              <br>
              Nyttig nar alle er registrert og du ikke vil ha uonskede gjester.
              <em>Eksisterende brukere pavirkes ikke.</em>
            </div>
          </div>
          <div class="settings-control">
            <label class="settings-toggle" aria-label="Registrering apen">
              <input v-model="registrationOpen" type="checkbox" />
              <span class="settings-toggle-track"></span>
              <span class="settings-toggle-thumb"></span>
            </label>
          </div>
        </div>

        <div class="settings-row">
          <div class="settings-info">
            <div class="settings-title">Maks antall pasienter</div>
            <div class="settings-desc">
              Maksimalt antall registrerte brukere. Nar grensen er nadd blokkeres nye registreringer automatisk, selv om registrering er apen.
              <br>
              <em>Sett til 0 for ubegrenset.</em>
            </div>
          </div>
          <div class="settings-control">
            <div class="settings-number-wrap">
              <input
                v-model.number="maxPatients"
                class="settings-form-input settings-number-input"
                type="number"
                min="0"
              />
              <span class="settings-number-hint">maks</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="settings-section-label">Vedlikehold</div>
      <div class="settings-panel">
        <div v-if="maintenanceMode" class="maintenance-banner">
          <div class="maintenance-banner-dot"></div>
          <div class="maintenance-banner-text">
            <strong>Vedlikeholdsmodus er aktiv.</strong> Vanlige brukere ser vedlikeholdssiden. Admins kan fortsatt bruke alt.
          </div>
        </div>

        <div class="settings-row danger">
          <div class="settings-info">
            <div class="settings-title">Vedlikeholdsmodus</div>
            <div class="settings-desc">
              Viser en vedlikeholdsside til alle ikke-admin brukere. Du og andre admins kan fortsatt logge inn og bruke hele siden normalt.
              <br>
              <em>Skru pa mens du oppdaterer eller feilsoker.</em>
            </div>
          </div>
          <div class="settings-control">
            <label class="settings-toggle settings-toggle-danger" aria-label="Vedlikeholdsmodus">
              <input
                :checked="maintenanceMode"
                type="checkbox"
                @change="updateMaintenanceMode($event.target.checked)"
              />
              <span class="settings-toggle-track"></span>
              <span class="settings-toggle-thumb"></span>
            </label>
          </div>
        </div>

        <div class="settings-input-row">
          <label class="settings-form-label" for="maintenance-message">Vedlikeholdsmelding</label>
          <textarea
            id="maintenance-message"
            v-model="maintenancePageMessage"
            class="settings-form-textarea"
            rows="2"
            placeholder="Vi er snart tilbake. Thomas fikser det."
          ></textarea>
          <div class="settings-form-hint">
            Vises til brukere som prover a besoke siden under vedlikehold.
          </div>
        </div>
      </div>
    </div>

    <div class="settings-save-row">
      <span class="settings-save-hint">SS 7.7 - Endringer lagres ikke automatisk.</span>
      <div class="settings-save-actions">
        <button class="btn btn-ghost btn-sm" type="button" @click="resetForm">Nullstill</button>
        <button class="btn btn-red btn-sm" type="button" @click="saveSettings">Lagre innstillinger</button>
      </div>
    </div>

    <div
      v-if="noticeMaintenanceMessage || maintenanceMessage"
      class="form-message settings-status"
      :class="{ success: activeStatusSuccess, error: !activeStatusSuccess }"
    >
      {{ activeStatusMessage }}
    </div>
  </section>
</template>

<script>
export default {
  props: [
    'maintenanceMode',
    'noticeMaintenanceMode',
    'maintenanceBannerMessage',
    'maintenanceMessage',
    'maintenanceSuccess',
    'noticeMaintenanceMessage',
    'noticeMaintenanceSuccess'
  ],
  emits: [
    'onToggleMaintenance',
    'onToggleNoticeMaintenance',
    'update:maintenanceMode',
    'update:noticeMaintenanceMode',
    'update:maintenanceBannerMessage'
  ],
  data() {
    return {
      siteName: 'HMN Mental Pasienter',
      operationsMessage: this.maintenanceBannerMessage || 'Forum-tjenesten er utilgjengelig grunnet eksistensiell krise. Forventet retur: Aldri.',
      registrationOpen: true,
      maxPatients: 0,
      maintenancePageMessage: 'Vi er snart tilbake. Thomas fikser det.'
    };
  },
  computed: {
    activeStatusMessage() {
      return this.noticeMaintenanceMessage || this.maintenanceMessage;
    },
    activeStatusSuccess() {
      return this.noticeMaintenanceMessage ? this.noticeMaintenanceSuccess : this.maintenanceSuccess;
    }
  },
  watch: {
    maintenanceBannerMessage(newValue) {
      if (newValue !== this.operationsMessage) {
        this.operationsMessage = newValue || 'Forum-tjenesten er utilgjengelig grunnet eksistensiell krise. Forventet retur: Aldri.';
      }
    }
  },
  methods: {
    updateMaintenanceMode(value) {
      this.$emit('update:maintenanceMode', value);
      this.$emit('onToggleMaintenance');
    },
    confirmDriftsmelding() {
      const trimmedMessage = this.operationsMessage.trim();
      this.$emit('update:maintenanceBannerMessage', trimmedMessage);
      this.$emit('update:noticeMaintenanceMode', Boolean(trimmedMessage));
      this.$emit('onToggleNoticeMaintenance');
    },
    saveSettings() {
      this.confirmDriftsmelding();
    },
    resetForm() {
      this.siteName = 'HMN Mental Pasienter';
      this.operationsMessage = this.maintenanceBannerMessage || 'Forum-tjenesten er utilgjengelig grunnet eksistensiell krise. Forventet retur: Aldri.';
      this.registrationOpen = true;
      this.maxPatients = 0;
      this.maintenancePageMessage = 'Vi er snart tilbake. Thomas fikser det.';
    }
  }
};
</script>

<style scoped>
.settings-ref {
  width: min(100%, 860px);
}

.settings-page-head {
  margin-bottom: 28px;
}

.settings-page-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 32px;
  font-weight: 900;
  color: var(--bright);
  text-transform: uppercase;
  letter-spacing: -0.01em;
  line-height: 1;
  margin-bottom: 6px;
}

.settings-page-title em {
  color: var(--cyan);
  font-style: normal;
}

.settings-page-sub {
  font-size: 13px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
}

.settings-section {
  margin-bottom: 24px;
}

.settings-section-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.settings-section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.settings-panel {
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border2);
  border-radius: 12px;
  overflow: hidden;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s;
}

.settings-row:last-child {
  border-bottom: none;
}

.settings-row:hover {
  background: rgba(255,255,255,0.02);
}

.settings-row.danger:hover {
  background: rgba(200,16,46,0.04);
}

.settings-info {
  flex: 1;
  min-width: 0;
}

.settings-title {
  margin-bottom: 3px;
  font-size: 14px;
  font-weight: 600;
  color: var(--bright);
  font-family: 'Barlow', sans-serif;
}

.settings-desc {
  font-size: 12px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
  line-height: 1.55;
}

.settings-desc em {
  display: inline-block;
  margin-top: 3px;
  color: var(--text);
  font-style: normal;
}

.settings-control {
  flex-shrink: 0;
}

.settings-input-row {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
}

.settings-input-row:last-child {
  border-bottom: none;
}

.settings-form-label {
  display: block;
  margin-bottom: 5px;
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
}

.settings-form-input,
.settings-form-textarea {
  width: 100%;
  background: var(--s2);
  border: 1px solid var(--border2);
  border-radius: 7px;
  padding: 10px 13px;
  font-size: 13px;
  color: var(--bright);
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: all 0.15s;
}

.settings-form-input:focus,
.settings-form-textarea:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 0 3px rgba(0,184,208,0.1);
  background: var(--s3);
}

.settings-form-textarea {
  resize: none;
  line-height: 1.6;
}

.settings-form-hint {
  margin-top: 5px;
  font-size: 11px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
  font-style: italic;
}

.settings-inline-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.settings-number-wrap {
  position: relative;
  width: 120px;
}

.settings-number-input {
  padding-right: 36px;
  text-align: center;
}

.settings-number-hint {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 10px;
  color: var(--muted);
  font-family: 'Barlow Condensed', sans-serif;
  pointer-events: none;
}

.settings-toggle {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  cursor: pointer;
}

.settings-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.settings-toggle-track {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border2);
  transition: all 0.2s;
}

.settings-toggle input:checked + .settings-toggle-track {
  background: rgba(40,184,96,0.3);
  border-color: rgba(40,184,96,0.5);
}

.settings-toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--muted);
  transition: all 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

.settings-toggle input:checked ~ .settings-toggle-thumb {
  left: 23px;
  background: var(--green);
  box-shadow: 0 0 8px rgba(40,184,96,0.5);
}

.settings-toggle-danger input:checked + .settings-toggle-track {
  background: rgba(200,16,46,0.25);
  border-color: rgba(200,16,46,0.4);
}

.settings-toggle-danger input:checked ~ .settings-toggle-thumb {
  background: var(--red2);
  box-shadow: 0 0 8px rgba(200,16,46,0.5);
}

.maintenance-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 18px 14px;
  padding: 12px 14px;
  border-radius: 8px;
  background: rgba(200,16,46,0.08);
  border: 1px solid rgba(200,16,46,0.2);
}

.maintenance-banner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--red2);
  box-shadow: 0 0 8px var(--red2);
  flex-shrink: 0;
  animation: blink 2s infinite;
}

.maintenance-banner-text {
  flex: 1;
  font-size: 12px;
  color: var(--red2);
  font-family: 'Barlow', sans-serif;
}

.maintenance-banner-text strong {
  font-weight: 600;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.settings-save-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.settings-save-hint {
  font-size: 12px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
  font-style: italic;
}

.settings-save-actions {
  display: flex;
  gap: 10px;
}

.settings-status {
  margin-top: 14px;
  max-width: 520px;
}

@media (max-width: 700px) {
  .settings-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .settings-control {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }

  .settings-number-wrap {
    width: 100%;
    max-width: 150px;
  }
}
</style>
