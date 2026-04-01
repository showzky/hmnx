
<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="settings-shell">
    <div class="settings-frame">
      <aside class="settings-sidebar">
        <div class="settings-sidebar-head">
          <p class="settings-kicker settings-kicker-muted">Innstillinger</p>
          <h1>Innstillinger</h1>
          <p>Juster profil, koblinger og intern portaloppforsel.</p>
        </div>

        <div class="settings-nav-list">
          <button
            v-for="tab in settingsTabs"
            :key="tab.id"
            type="button"
            class="settings-nav-btn"
            :class="{ active: activeSettingsTab === tab.id, danger: tab.id === 'faresone' }"
            @click="activeSettingsTab = tab.id"
          >
            <span class="settings-nav-dot"></span>
            <span class="settings-nav-copy">
              <span class="settings-nav-label">{{ tab.label }}</span>
              <span class="settings-nav-hint">{{ tab.hint }}</span>
            </span>
            <span v-if="tab.id === 'faresone'" class="settings-nav-badge">!</span>
          </button>
        </div>
      </aside>

      <main class="settings-main">
        <header class="settings-page-header">
          <p class="settings-kicker">{{ activeSettingsMeta.kicker }}</p>
          <h2>Inn<em>stillinger</em></h2>
          <p>{{ activeSettingsMeta.description }}</p>
        </header>

        <section v-show="activeSettingsTab === 'profil'" class="settings-panel" id="profil">
          <div class="settings-panel-head">
            <span class="settings-panel-title">Profil</span>
          </div>
          <div class="settings-panel-body">
            <div class="settings-profile-identity">
              <img
                v-if="patientProfileDraft.avatarPreview"
                :src="patientProfileDraft.avatarPreview"
                alt="Profilbilde"
                class="settings-profile-avatar"
              />
              <div v-else class="settings-profile-avatar settings-profile-avatar-fallback">{{ profileInitials }}</div>

              <div class="settings-profile-copy">
                <strong>{{ patientProfileDraft.displayName || patientProfileDraft.username || 'Pasient' }}</strong>
                <span>Profilbilde · JPG, PNG eller GIF · maks 4MB</span>
                <div class="settings-profile-actions">
                  <button type="button" class="settings-secondary-btn settings-btn-sm" @click="triggerAvatarUpload" :disabled="isUploadingAvatarAsset">
                    {{ isUploadingAvatarAsset ? 'Laster opp...' : 'Endre bilde' }}
                  </button>
                  <input ref="avatarUploadInput" type="file" accept="image/*" hidden @change="handleAvatarFileChange" />
                </div>
              </div>
            </div>

            <div class="settings-form-grid settings-form-grid-two">
              <label class="settings-field">
                <span>Brukernavn</span>
                <input v-model.trim="patientProfileDraft.username" type="text" placeholder="Brukernavn..." @blur="runUsernameAvailabilityCheck" />
                <small :class="usernameCheckStateClass">{{ usernameCheckMessage }}</small>
              </label>

              <label class="settings-field">
                <span>Visningsnavn</span>
                <input v-model.trim="patientProfileDraft.displayName" type="text" placeholder="Visningsnavn..." />
              </label>
            </div>

            <label class="settings-field settings-field-spaced">
              <span>Bio</span>
              <textarea v-model="patientProfileDraft.bio" rows="4" maxlength="300" placeholder="Skriv litt om deg selv... eller ikke. § 3.3 krever ingenting."></textarea>
              <small>Vises på profilsiden din. {{ patientProfileDraft.bio.length }}/300 tegn.</small>
            </label>

            <label class="settings-field settings-field-spaced">
              <span>Profilbanner (URL)</span>
              <div class="settings-inline-field">
                <input v-model.trim="patientProfileDraft.bannerUrl" type="url" placeholder="https://..." />
                <button type="button" class="settings-secondary-btn settings-btn-sm" @click="triggerBannerUpload" :disabled="isUploadingBannerAsset">
                  {{ isUploadingBannerAsset ? 'Laster opp...' : 'Last opp' }}
                </button>
              </div>
              <input ref="bannerUploadInput" type="file" accept="image/*" hidden @change="handleBannerFileChange" />
              <small>Lenke til bannerbilde. Anbefalt 1200x300px.</small>
            </label>

            <div class="settings-button-row">
              <button type="button" class="settings-primary-btn" @click="savePatientProfile" :disabled="isSavingProfile">
                {{ isSavingProfile ? 'Lagrer...' : 'Lagre profil' }}
              </button>
              <button type="button" class="settings-secondary-btn" @click="resetPatientProfile" :disabled="isSavingProfile || isUploadingAvatarAsset || isUploadingBannerAsset">
                Avbryt
              </button>
            </div>

            <p v-if="profileStatusMessage" class="settings-status" :class="profileStatusTone">{{ profileStatusMessage }}</p>
          </div>
        </section>

        <section v-show="activeSettingsTab === 'konto'" class="settings-panel" id="konto">
          <div class="settings-panel-head">
            <span class="settings-panel-title">Konto</span>
          </div>
          <div class="settings-panel-body">
            <label class="settings-field">
              <span>E-postadresse</span>
              <input v-model.trim="accountSecurityDraft.email" type="email" placeholder="showzky@example.com" />
            </label>

            <label class="settings-field settings-field-spaced">
              <span>Navarende passord</span>
              <input v-model="accountSecurityDraft.currentPassword" type="password" placeholder="••••••••" />
            </label>

            <div class="settings-form-grid settings-form-grid-two settings-field-spaced">
              <label class="settings-field">
                <span>Nytt passord</span>
                <input v-model="accountSecurityDraft.newPassword" type="password" placeholder="••••••••" />
              </label>

              <label class="settings-field">
                <span>Bekreft nytt passord</span>
                <input v-model="accountSecurityDraft.confirmPassword" type="password" placeholder="••••••••" />
                <small v-if="accountPasswordMismatch" class="settings-status-error">Passordene matcher ikke.</small>
              </label>
            </div>

            <div class="settings-button-row">
              <button type="button" class="settings-primary-btn" @click="saveAccountSecurity" :disabled="isSavingAccountSecurity">
                {{ isSavingAccountSecurity ? 'Lagrer...' : 'Oppdater konto' }}
              </button>
              <button type="button" class="settings-secondary-btn" @click="resetAccountSecurity" :disabled="isSavingAccountSecurity">
                Avbryt
              </button>
            </div>

            <p v-if="accountStatusMessage" class="settings-status" :class="accountStatusTone">{{ accountStatusMessage }}</p>
          </div>
        </section>

        <section v-show="activeSettingsTab === 'tilkoblede'" class="settings-panel" id="tilkoblede">
          <div class="settings-panel-head">
            <span class="settings-panel-title">Tilkoblede kontoer</span>
            <span class="settings-panel-meta">{{ connectedPortalCount }} av 6 koblet til</span>
          </div>
          <div class="settings-panel-body">
            <div class="settings-connection-divider">
              <span>OAuth - automatisk innlogging</span>
              <div></div>
            </div>

            <div class="settings-connection-list">
              <article
                v-for="connection in oauthConnectionCards"
                :key="connection.provider"
                class="settings-connection-card"
                :class="[{ connected: connection.connected }, `provider-${connection.provider}`]"
              >
                <div class="settings-connection-icon">{{ getConnectionGlyph(connection.provider) }}</div>
                <div class="settings-connection-copy">
                  <strong>{{ connection.label }}</strong>
                  <span :class="connection.connected ? 'is-on' : 'is-off'">
                    {{ connection.connected ? '✓ Koblet til' : 'Ikke tilkoblet' }}
                  </span>
                  <small v-if="connection.connected && connection.subtitle">{{ connection.subtitle }}</small>
                </div>
                <div class="settings-connection-actions">
                  <button
                    v-if="connection.connected && connection.canDisconnect"
                    type="button"
                    class="settings-danger-btn settings-btn-sm"
                    @click="disconnectPortalConnection(connection.provider)"
                    :disabled="isSyncingConnections"
                  >
                    Koble fra
                  </button>
                  <button
                    v-else
                    type="button"
                    class="settings-secondary-btn settings-btn-sm"
                    @click="startPortalConnection(connection.provider)"
                    :disabled="isSyncingConnections"
                  >
                    Koble til
                  </button>
                </div>
              </article>
            </div>

            <div class="settings-connection-divider spaced">
              <span>Spillernavn - manuell kobling</span>
              <div></div>
            </div>

            <article class="settings-connection-card provider-cod manual-card">
              <div class="settings-connection-icon">🎯</div>
              <div class="settings-connection-copy grow">
                <strong>CoD Esports-profil</strong>
                <span class="is-off">{{ linkedCodProfileState ? 'Koblet til esports-profil.' : 'Ikke koblet - sok etter din esports-profil' }}</span>

                <div v-if="linkedCodProfileState" class="settings-manual-linked">
                  <img v-if="linkedCodProfileState.avatarUrl" :src="linkedCodProfileState.avatarUrl" alt="CoD avatar" class="settings-linked-avatar" />
                  <div v-else class="settings-linked-avatar settings-linked-avatar-fallback">{{ getProfileInitial(linkedCodProfileState.displayName) }}</div>
                  <div class="settings-linked-copy">
                    <strong>{{ linkedCodProfileState.displayName }}</strong>
                    <span>{{ linkedCodProfileState.subtitle }}</span>
                  </div>
                  <button type="button" class="settings-danger-btn settings-btn-sm" @click="disconnectCodProfile" :disabled="isSyncingConnections">
                    Koble fra
                  </button>
                </div>

                <div class="settings-inline-field settings-inline-field-compact">
                  <input
                    v-model.trim="codProfileSearchDraft"
                    type="text"
                    placeholder="Sok etter spillernavn..."
                    @keydown.enter.prevent="searchCodProfiles"
                  />
                  <button type="button" class="settings-secondary-btn settings-btn-sm" @click="searchCodProfiles" :disabled="isSearchingCodProfiles">
                    {{ isSearchingCodProfiles ? 'Soker...' : 'Sok' }}
                  </button>
                </div>

                <p v-if="codSearchStatusMessage" class="settings-status compact" :class="codSearchStatusTone">{{ codSearchStatusMessage }}</p>
              </div>
            </article>

            <div v-if="codProfileSearchResults.length" class="settings-cod-results">
              <button
                v-for="result in codProfileSearchResults"
                :key="result.providerAccountId"
                type="button"
                class="settings-cod-result"
                @click="linkCodProfile(result)"
                :disabled="isSyncingConnections"
              >
                <img v-if="result.avatarUrl" :src="result.avatarUrl" alt="CoD spiller" class="settings-linked-avatar" />
                <div v-else class="settings-linked-avatar settings-linked-avatar-fallback">{{ getProfileInitial(result.displayName) }}</div>
                <div class="settings-cod-copy">
                  <strong>{{ result.displayName }}</strong>
                  <span>{{ result.realName || 'Ukjent navn' }}</span>
                  <small>{{ result.subtitle }}</small>
                </div>
                <span class="settings-cod-action">Velg profil</span>
              </button>
            </div>

            <article class="settings-connection-card provider-epic manual-card">
              <div class="settings-connection-icon">🏗️</div>
              <div class="settings-connection-copy grow">
                <strong>Fortnite / Epic Games</strong>
                <span class="is-off">{{ linkedEpicProfileState ? 'Koblet til Epic-bruker.' : 'Ikke koblet' }}</span>
                <div class="settings-inline-field settings-inline-field-compact">
                  <input v-model.trim="epicProfileDraft" type="text" placeholder="Epic Games brukernavn..." />
                  <button type="button" class="settings-secondary-btn settings-btn-sm" @click="saveEpicProfile" :disabled="isSyncingConnections">
                    Lagre
                  </button>
                </div>
              </div>
              <div class="settings-connection-actions" v-if="linkedEpicProfileState">
                <button type="button" class="settings-danger-btn settings-btn-sm" @click="disconnectEpicProfile" :disabled="isSyncingConnections">
                  Koble fra
                </button>
              </div>
            </article>

            <p v-if="connectionStatusMessage" class="settings-status" :class="connectionStatusTone">{{ connectionStatusMessage }}</p>
          </div>
        </section>

        <section v-show="activeSettingsTab === 'varsler'" class="settings-panel" id="varsler">
          <div class="settings-panel-head">
            <span class="settings-panel-title">Varsler</span>
          </div>
          <div class="settings-panel-body">
            <div class="settings-toggle-list">
              <label v-for="item in alertPreferenceBlueprint" :key="item.key" class="settings-toggle-row">
                <div class="settings-toggle-copy">
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.description }}</span>
                </div>
                <span class="settings-toggle-switch">
                  <input v-model="alertPreferenceDraft[item.key]" type="checkbox" />
                  <span class="settings-toggle-track"></span>
                  <span class="settings-toggle-thumb"></span>
                </span>
              </label>
            </div>

            <div class="settings-button-row top-gap">
              <button type="button" class="settings-primary-btn" @click="saveAlertPreferences" :disabled="isSavingAlertPreferences">
                {{ isSavingAlertPreferences ? 'Lagrer...' : 'Lagre varsler' }}
              </button>
            </div>

            <p v-if="alertStatusMessage" class="settings-status" :class="alertStatusTone">{{ alertStatusMessage }}</p>
          </div>
        </section>

        <section v-show="activeSettingsTab === 'personvern'" class="settings-panel" id="personvern">
          <div class="settings-panel-head">
            <span class="settings-panel-title">Personvern</span>
          </div>
          <div class="settings-panel-body">
            <div class="settings-toggle-list">
              <label v-for="item in privacyWardBlueprint" :key="item.key" class="settings-toggle-row">
                <div class="settings-toggle-copy">
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.description }}</span>
                </div>
                <span class="settings-toggle-switch">
                  <input v-model="privacyWardDraft[item.key]" type="checkbox" />
                  <span class="settings-toggle-track"></span>
                  <span class="settings-toggle-thumb"></span>
                </span>
              </label>
            </div>

            <div class="settings-button-row top-gap">
              <button type="button" class="settings-primary-btn" @click="savePrivacyWard" :disabled="isSavingPrivacyWard">
                {{ isSavingPrivacyWard ? 'Lagrer...' : 'Lagre personvern' }}
              </button>
            </div>

            <p v-if="privacyStatusMessage" class="settings-status" :class="privacyStatusTone">{{ privacyStatusMessage }}</p>
          </div>
        </section>

        <section v-show="activeSettingsTab === 'faresone'" class="settings-panel settings-panel-danger" id="faresone">
          <div class="settings-panel-head settings-panel-head-danger">
            <span class="settings-panel-title">⚠ Faresone</span>
          </div>
          <div class="settings-panel-body settings-danger-body">
            <div class="settings-danger-row">
              <div class="settings-danger-copy">
                <strong>Logg ut av alle enheter</strong>
                <span>Ugyldiggjør alle aktive sesjoner. Du ma logge inn pa nytt. § 5.1 - ingen angrerett.</span>
              </div>
              <button type="button" class="settings-danger-btn settings-btn-sm" @click="openDangerZoneModal('revoke_all')">
                Logg ut overalt
              </button>
            </div>

            <div class="settings-danger-divider"></div>

            <div class="settings-danger-row">
              <div class="settings-danger-copy">
                <strong>Slett konto</strong>
                <span>Permanent sletting av konto og tilhorende data. Thomas vil sannsynligvis fa skylda.</span>
              </div>
              <button type="button" class="settings-danger-btn settings-btn-sm" @click="openDangerZoneModal('delete_account')">
                Slett konto
              </button>
            </div>

            <p v-if="dangerZoneStatusMessage" class="settings-status" :class="dangerZoneStatusTone">{{ dangerZoneStatusMessage }}</p>
          </div>
        </section>
      </main>
    </div>

    <div v-if="dangerZoneModalState.isOpen" class="danger-modal-backdrop" @click.self="closeDangerZoneModal">
      <div class="danger-modal-card">
        <p class="settings-kicker">Bekreft handling</p>
        <h3>{{ dangerZoneModalTitle }}</h3>
        <p class="danger-modal-copy">{{ dangerZoneModalCopy }}</p>

        <label v-if="dangerZoneModalState.requiresPassword" class="settings-field settings-field-spaced">
          <span>Navarende passord</span>
          <input v-model="dangerZoneModalState.currentPassword" type="password" placeholder="Pakrevd for sletting" />
        </label>

        <div class="danger-modal-actions">
          <button type="button" class="settings-secondary-btn" @click="closeDangerZoneModal">Avbryt</button>
          <button type="button" class="settings-danger-btn" @click="executeDangerZoneAction" :disabled="isExecutingDangerAction">
            {{ isExecutingDangerAction ? 'Jobber...' : dangerZoneModalState.confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/axios'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()
const portalApiRoot = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

const settingsTabs = [
  { id: 'profil', label: 'Profil', hint: 'avatar, banner og bio', kicker: 'profil', description: 'Juster synlig profilinformasjon og mediefelter.' },
  { id: 'konto', label: 'Konto', hint: 'e-post og passord', kicker: 'konto', description: 'Sikre kontoopplysninger og bytt passord ved behov.' },
  { id: 'tilkoblede', label: 'Tilkoblede kontoer', hint: 'steam, discord, cod', kicker: 'koblinger', description: 'Administrer OAuth-forbindelser og manuelle profiler.' },
  { id: 'varsler', label: 'Varsler', hint: 'interne signaler', kicker: 'varsler', description: 'Velg hvilke signaler portalen skal sende deg.' },
  { id: 'personvern', label: 'Personvern', hint: 'synlighet og grenser', kicker: 'personvern', description: 'Bestem hva andre skal kunne se om deg.' },
  { id: 'faresone', label: 'Faresone', hint: 'kraftige handlinger', kicker: 'faresone', description: 'Logg ut overalt eller slett hele kontoen.' },
]

const alertPreferenceBlueprint = [
  { key: 'friend_requests', label: 'Venneforesporsler', description: 'Varsle når noen vil inn i kretsen.' },
  { key: 'direct_messages', label: 'Direktemeldinger', description: 'Fa beskjed om nye meldinger og ping.' },
  { key: 'event_updates', label: 'Hendelsesoppdateringer', description: 'Hold deg oppdatert når hendelser endres.' },
  { key: 'bedriftsmeldinger', label: 'Bedriftsmeldinger', description: 'Motta signal når nye bedriftsmeldinger publiseres.' },
  { key: 'music_releases', label: 'Musikk og slipp', description: 'Varsle når noe nytt lander i Bangerfabrikken.' },
]

const privacyWardBlueprint = [
  { key: 'show_email', label: 'Vis e-post til venner', description: 'Lar venner se e-postadressen din.' },
  { key: 'show_activity', label: 'Vis aktivitet', description: 'Vis nylige hendelser, spill og intern aktivitet.' },
  { key: 'show_connections', label: 'Vis tilkoblede kontoer', description: 'Vis Steam, Discord, CoD og andre koblinger offentlig.' },
]

const providerLabelMap = {
  steam: 'Steam',
  xbox: 'Xbox',
  battlenet: 'Battle.net',
  discord: 'Discord',
  cod: 'CoD esports-profil',
  epic: 'Epic-bruker',
}

const activeSettingsTab = ref('profil')
const patientProfileDraft = reactive({ username: '', displayName: '', email: '', bio: '', bannerUrl: '', avatarPreview: '' })
const accountSecurityDraft = reactive({ email: '', currentPassword: '', newPassword: '', confirmPassword: '' })
const portalConnectionRegistry = ref([])
const alertPreferenceDraft = reactive({})
const privacyWardDraft = reactive({})
const dangerZoneModalState = reactive({ isOpen: false, actionKey: '', title: '', copy: '', confirmLabel: '', requiresPassword: false, currentPassword: '' })

const codProfileSearchDraft = ref('')
const codProfileSearchResults = ref([])
const linkedCodProfileState = ref(null)
const linkedEpicProfileState = ref(null)
const epicProfileDraft = ref('')

const usernameCheckState = ref('idle')
const usernameCheckMessage = ref('Brukernavn må være 3-30 tegn og kan kun bruke bokstaver, tall og underscore.')

const isSavingProfile = ref(false)
const isSavingAccountSecurity = ref(false)
const isSyncingConnections = ref(false)
const isSearchingCodProfiles = ref(false)
const isSavingAlertPreferences = ref(false)
const isSavingPrivacyWard = ref(false)
const isExecutingDangerAction = ref(false)
const isCheckingUsername = ref(false)
const isUploadingAvatarAsset = ref(false)
const isUploadingBannerAsset = ref(false)

const profileStatusMessage = ref('')
const profileStatusTone = ref('settings-status-muted')
const accountStatusMessage = ref('')
const accountStatusTone = ref('settings-status-muted')
const connectionStatusMessage = ref('')
const connectionStatusTone = ref('settings-status-muted')
const codSearchStatusMessage = ref('')
const codSearchStatusTone = ref('settings-status-muted')
const alertStatusMessage = ref('')
const alertStatusTone = ref('settings-status-muted')
const privacyStatusMessage = ref('')
const privacyStatusTone = ref('settings-status-muted')
const dangerZoneStatusMessage = ref('')
const dangerZoneStatusTone = ref('settings-status-muted')

const avatarUploadInput = ref(null)
const bannerUploadInput = ref(null)

const activeSettingsMeta = computed(() => settingsTabs.find(tab => tab.id === activeSettingsTab.value) || settingsTabs[0])
const profileInitials = computed(() => getProfileInitial(patientProfileDraft.displayName || patientProfileDraft.username || patientProfileDraft.email || 'P'))
const bannerPreviewStyle = computed(() => patientProfileDraft.bannerUrl ? ({ backgroundImage: `linear-gradient(135deg, rgba(4,12,22,0.82), rgba(6,16,28,0.55)), url(${patientProfileDraft.bannerUrl})` }) : undefined)
const accountPasswordMismatch = computed(() => Boolean(accountSecurityDraft.newPassword || accountSecurityDraft.confirmPassword) && accountSecurityDraft.newPassword !== accountSecurityDraft.confirmPassword)
const usernameCheckStateClass = computed(() => ({ 'settings-status-success': usernameCheckState.value === 'available', 'settings-status-error': usernameCheckState.value === 'taken' || usernameCheckState.value === 'invalid', 'settings-status-muted': ['idle', 'unchanged'].includes(usernameCheckState.value) }))
const oauthConnectionCards = computed(() => portalConnectionRegistry.value.filter(connection => ['steam', 'xbox', 'battlenet', 'discord'].includes(connection.provider)).map(connection => ({ ...connection, label: connection.name || providerLabelMap[connection.provider] || connection.provider, subtitle: connection.connected ? [connection.displayName, connection.subtitle].filter(Boolean).join(' · ') : (connection.subtitle || 'Ikke koblet til') })))
const connectedPortalCount = computed(() => portalConnectionRegistry.value.filter(connection => connection.connected).length)
const dangerZoneModalTitle = computed(() => dangerZoneModalState.title)
const dangerZoneModalCopy = computed(() => dangerZoneModalState.copy)

function getProfileInitial(value) { return String(value || 'P').trim().charAt(0).toUpperCase() || 'P' }
function getConnectionGlyph(provider) {
  return {
    steam: '🎮',
    xbox: '🎮',
    battlenet: '⚔️',
    discord: '💬',
    cod: '🎯',
    epic: '🏗️',
  }[provider] || '•'
}
function setStatus(targetRef, toneRef, message, tone = 'settings-status-muted') { targetRef.value = message; toneRef.value = tone }
function applyPortalUserToDrafts(portalUser) {
  patientProfileDraft.username = portalUser?.username || ''
  patientProfileDraft.displayName = portalUser?.display_name || portalUser?.displayName || portalUser?.username || ''
  patientProfileDraft.email = portalUser?.email || ''
  patientProfileDraft.bio = portalUser?.bio || ''
  patientProfileDraft.bannerUrl = portalUser?.banner || portalUser?.banner_url || ''
  patientProfileDraft.avatarPreview = portalUser?.avatar || ''
  accountSecurityDraft.email = portalUser?.email || ''
}
function normalizeConnectionPayload(connection) {
  return {
    provider: connection.provider,
    name: providerLabelMap[connection.provider] || connection.provider,
    connected: Boolean(connection.connected),
    canDisconnect: Boolean(connection.canDisconnect),
    displayName: connection.displayName || connection.display_name || '',
    avatarUrl: connection.avatarUrl || connection.avatar_url || '',
    subtitle: connection.subtitle || '',
    providerAccountId: connection.providerAccountId || connection.provider_account_id || '',
  }
}
async function hydratePortalUser() {
  const portalUser = await auth.hydrateFromToken(auth.token)
  if (portalUser) applyPortalUserToDrafts(portalUser)
}
async function hydratePortalConnectionRegistry() {
  try {
    isSyncingConnections.value = true
    const { data } = await axios.get('/connections')
    const normalized = Array.isArray(data?.connections) ? data.connections.map(normalizeConnectionPayload) : []
    portalConnectionRegistry.value = normalized
    linkedCodProfileState.value = normalized.find(item => item.provider === 'cod' && item.connected) || null
    linkedEpicProfileState.value = normalized.find(item => item.provider === 'epic' && item.connected) || null
    epicProfileDraft.value = linkedEpicProfileState.value?.displayName || ''
  } catch (error) {
    console.error('Failed to hydrate portal connections:', error)
    setStatus(connectionStatusMessage, connectionStatusTone, 'Kunne ikke hente tilkoblede kontoer akkurat nå.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function hydrateAlertPreferences() {
  try {
    const { data } = await axios.get('/settings/notifications')
    const serverPreferences = data?.alert_preferences || {}
    for (const item of alertPreferenceBlueprint) alertPreferenceDraft[item.key] = Boolean(serverPreferences[item.key])
  } catch (error) {
    console.error('Failed to hydrate alert preferences:', error)
    for (const item of alertPreferenceBlueprint) if (typeof alertPreferenceDraft[item.key] === 'undefined') alertPreferenceDraft[item.key] = false
  }
}
async function hydratePrivacyWard() {
  try {
    const { data } = await axios.get('/settings/privacy')
    const serverPreferences = data?.privacy_preferences || {}
    for (const item of privacyWardBlueprint) privacyWardDraft[item.key] = Boolean(serverPreferences[item.key])
  } catch (error) {
    console.error('Failed to hydrate privacy preferences:', error)
    for (const item of privacyWardBlueprint) if (typeof privacyWardDraft[item.key] === 'undefined') privacyWardDraft[item.key] = false
  }
}
async function runUsernameAvailabilityCheck() {
  const username = patientProfileDraft.username.trim()
  if (!username) {
    usernameCheckState.value = 'idle'
    usernameCheckMessage.value = 'Brukernavn må være 3-30 tegn og kan kun bruke bokstaver, tall og underscore.'
    return
  }
  if (username === (auth.user?.username || '')) {
    usernameCheckState.value = 'unchanged'
    usernameCheckMessage.value = 'Dette er allerede brukernavnet ditt.'
    return
  }
  try {
    isCheckingUsername.value = true
    const { data } = await axios.get('/settings/username-availability', { params: { username } })
    usernameCheckState.value = data?.state || 'idle'
    usernameCheckMessage.value = data?.message || 'Ingen tilbakemelding fra server.'
  } catch (error) {
    console.error('Failed username availability check:', error)
    usernameCheckState.value = 'invalid'
    usernameCheckMessage.value = error.response?.data?.msg || 'Kunne ikke sjekke brukernavn akkurat nå.'
  } finally {
    isCheckingUsername.value = false
  }
}
async function savePatientProfile() {
  try {
    isSavingProfile.value = true
    const profile_update_payload = {
      username: patientProfileDraft.username.trim(),
      bio: patientProfileDraft.bio,
      display_name: patientProfileDraft.displayName.trim(),
      banner_url: patientProfileDraft.bannerUrl.trim(),
    }
    const { data } = await axios.post('/update-profile', profile_update_payload)
    if (data?.user) {
      auth.setAuth(data.user, auth.token)
      applyPortalUserToDrafts(data.user)
    } else {
      await hydratePortalUser()
    }
    setStatus(profileStatusMessage, profileStatusTone, 'Profilen ble oppdatert.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to save patient profile:', error)
    setStatus(profileStatusMessage, profileStatusTone, error.response?.data?.msg || 'Kunne ikke lagre profil akkurat nå.', 'settings-status-error')
  } finally {
    isSavingProfile.value = false
  }
}
function resetPatientProfile() {
  applyPortalUserToDrafts(auth.user)
  setStatus(profileStatusMessage, profileStatusTone, '', 'settings-status-muted')
}
async function saveAccountSecurity() {
  if (accountPasswordMismatch.value) {
    setStatus(accountStatusMessage, accountStatusTone, 'Nytt passord og bekreftelse må være like.', 'settings-status-error')
    return
  }
  const hasEmailChange = accountSecurityDraft.email.trim() !== (auth.user?.email || '')
  const hasPasswordChange = Boolean(accountSecurityDraft.newPassword)
  if (!hasEmailChange && !hasPasswordChange) {
    setStatus(accountStatusMessage, accountStatusTone, 'Ingen kontoendringer å lagre.', 'settings-status-muted')
    return
  }
  try {
    isSavingAccountSecurity.value = true
    const { data } = await axios.post('/settings/account', {
      email: accountSecurityDraft.email.trim(),
      current_password: accountSecurityDraft.currentPassword,
      new_password: accountSecurityDraft.newPassword,
    })
    if (data?.user) {
      auth.setAuth(data.user, auth.token)
      applyPortalUserToDrafts(data.user)
    } else {
      await hydratePortalUser()
    }
    accountSecurityDraft.currentPassword = ''
    accountSecurityDraft.newPassword = ''
    accountSecurityDraft.confirmPassword = ''
    setStatus(accountStatusMessage, accountStatusTone, data?.msg || 'Kontoinnstillinger lagret.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to save account security:', error)
    setStatus(accountStatusMessage, accountStatusTone, error.response?.data?.msg || 'Kunne ikke lagre kontoinnstillinger.', 'settings-status-error')
  } finally {
    isSavingAccountSecurity.value = false
  }
}
function resetAccountSecurity() {
  accountSecurityDraft.email = auth.user?.email || ''
  accountSecurityDraft.currentPassword = ''
  accountSecurityDraft.newPassword = ''
  accountSecurityDraft.confirmPassword = ''
  setStatus(accountStatusMessage, accountStatusTone, '', 'settings-status-muted')
}
function triggerAvatarUpload() { avatarUploadInput.value?.click() }
function triggerBannerUpload() { bannerUploadInput.value?.click() }
async function handleAvatarFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const localPreviewUrl = URL.createObjectURL(file)
  patientProfileDraft.avatarPreview = localPreviewUrl
  try {
    isUploadingAvatarAsset.value = true
    const formData = new FormData()
    formData.append('avatar', file)
    const { data } = await axios.post('/upload-avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (data?.url) {
      patientProfileDraft.avatarPreview = data.url
      auth.setAuth({ ...auth.user, avatar: data.url }, auth.token)
    }
    setStatus(profileStatusMessage, profileStatusTone, 'Avatar oppdatert.', 'settings-status-success')
  } catch (error) {
    console.error('Failed avatar upload:', error)
    setStatus(profileStatusMessage, profileStatusTone, error.response?.data?.msg || 'Kunne ikke laste opp avatar.', 'settings-status-error')
  } finally {
    isUploadingAvatarAsset.value = false
    event.target.value = ''
  }
}
async function handleBannerFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  try {
    isUploadingBannerAsset.value = true
    const formData = new FormData()
    formData.append('banner', file)
    const { data } = await axios.post('/upload-banner', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (data?.url) {
      patientProfileDraft.bannerUrl = data.url
      auth.setAuth({ ...auth.user, banner: data.url }, auth.token)
    }
    setStatus(profileStatusMessage, profileStatusTone, 'Banner oppdatert.', 'settings-status-success')
  } catch (error) {
    console.error('Failed banner upload:', error)
    setStatus(profileStatusMessage, profileStatusTone, error.response?.data?.msg || 'Kunne ikke laste opp banner.', 'settings-status-error')
  } finally {
    isUploadingBannerAsset.value = false
    event.target.value = ''
  }
}
async function startPortalConnection(provider) {
  setStatus(connectionStatusMessage, connectionStatusTone, '', 'settings-status-muted')
  if (provider === 'steam') {
    if (!auth.token) {
      setStatus(connectionStatusMessage, connectionStatusTone, 'Du må være logget inn for å starte Steam-kobling.', 'settings-status-error')
      return
    }
    window.location.href = `${portalApiRoot}/connections/steam/start?access_token=${encodeURIComponent(auth.token)}`
    return
  }
  if (provider === 'discord') {
    window.location.href = `${portalApiRoot}/login/discord`
    return
  }
  if (provider === 'xbox') {
    setStatus(connectionStatusMessage, connectionStatusTone, 'Xbox-kobling er deaktivert til ekte verifisering er på plass.', 'settings-status-muted')
    return
  }
  if (provider === 'battlenet') setStatus(connectionStatusMessage, connectionStatusTone, 'Battle.net-kobling er ikke aktivert ennå.', 'settings-status-muted')
}
async function disconnectPortalConnection(provider) {
  try {
    isSyncingConnections.value = true
    await axios.delete(`/connections/${provider}`)
    await hydratePortalConnectionRegistry()
    setStatus(connectionStatusMessage, connectionStatusTone, `${providerLabelMap[provider] || provider} ble koblet fra.`, 'settings-status-success')
  } catch (error) {
    console.error('Failed to disconnect provider:', error)
    setStatus(connectionStatusMessage, connectionStatusTone, error.response?.data?.error || 'Kunne ikke koble fra kontoen.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function searchCodProfiles() {
  const query = codProfileSearchDraft.value.trim()
  if (!query) {
    codProfileSearchResults.value = []
    setStatus(codSearchStatusMessage, codSearchStatusTone, 'Skriv inn et spillernavn før du søker.', 'settings-status-muted')
    return
  }
  try {
    isSearchingCodProfiles.value = true
    const { data } = await axios.get('/settings/connections/cod/search', { params: { q: query } })
    const results = Array.isArray(data?.results) ? data.results : []
    codProfileSearchResults.value = results.map(result => ({
      providerAccountId: result.provider_account_id || result.providerAccountId,
      displayName: result.display_name || result.displayName,
      realName: result.real_name || result.realName,
      avatarUrl: result.avatar_url || result.avatarUrl,
      subtitle: result.subtitle || '',
    }))
    if (codProfileSearchResults.value.length) {
      setStatus(codSearchStatusMessage, codSearchStatusTone, `Fant ${codProfileSearchResults.value.length} mulige CoD-profiler.`, 'settings-status-success')
    } else {
      setStatus(codSearchStatusMessage, codSearchStatusTone, 'Fant ingen treff på det spillernavnet.', 'settings-status-muted')
    }
  } catch (error) {
    console.error('Failed CoD profile search:', error)
    codProfileSearchResults.value = []
    setStatus(codSearchStatusMessage, codSearchStatusTone, error.response?.data?.msg || 'Kunne ikke søke i CoD-profiler akkurat nå.', 'settings-status-error')
  } finally {
    isSearchingCodProfiles.value = false
  }
}
async function linkCodProfile(result) {
  try {
    isSyncingConnections.value = true
    await axios.post('/settings/connections/cod', {
      provider_account_id: result.providerAccountId,
      display_name: result.displayName,
      avatar_url: result.avatarUrl,
      subtitle: result.subtitle,
    })
    await hydratePortalConnectionRegistry()
    codProfileSearchResults.value = []
    codProfileSearchDraft.value = ''
    setStatus(connectionStatusMessage, connectionStatusTone, 'CoD-profil koblet til.', 'settings-status-success')
    setStatus(codSearchStatusMessage, codSearchStatusTone, 'CoD-profil lagret på brukeren din.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to link CoD profile:', error)
    setStatus(codSearchStatusMessage, codSearchStatusTone, error.response?.data?.msg || 'Kunne ikke koble CoD-profilen.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function disconnectCodProfile() {
  try {
    isSyncingConnections.value = true
    await axios.delete('/settings/connections/cod')
    await hydratePortalConnectionRegistry()
    setStatus(connectionStatusMessage, connectionStatusTone, 'CoD-profil koblet fra.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to disconnect CoD profile:', error)
    setStatus(connectionStatusMessage, connectionStatusTone, error.response?.data?.msg || 'Kunne ikke koble fra CoD-profil.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function saveEpicProfile() {
  const epicUsername = epicProfileDraft.value.trim()
  if (!epicUsername) {
    setStatus(connectionStatusMessage, connectionStatusTone, 'Skriv inn et Epic-brukernavn først.', 'settings-status-muted')
    return
  }
  try {
    isSyncingConnections.value = true
    await axios.post('/settings/connections/epic', { provider_account_id: epicUsername, display_name: epicUsername })
    await hydratePortalConnectionRegistry()
    setStatus(connectionStatusMessage, connectionStatusTone, 'Epic-bruker lagret.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to save Epic profile:', error)
    setStatus(connectionStatusMessage, connectionStatusTone, error.response?.data?.msg || 'Kunne ikke lagre Epic-bruker.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function disconnectEpicProfile() {
  try {
    isSyncingConnections.value = true
    await axios.delete('/settings/connections/epic')
    await hydratePortalConnectionRegistry()
    setStatus(connectionStatusMessage, connectionStatusTone, 'Epic-bruker koblet fra.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to disconnect Epic profile:', error)
    setStatus(connectionStatusMessage, connectionStatusTone, error.response?.data?.msg || 'Kunne ikke koble fra Epic-bruker.', 'settings-status-error')
  } finally {
    isSyncingConnections.value = false
  }
}
async function saveAlertPreferences() {
  try {
    isSavingAlertPreferences.value = true
    const alert_preferences = Object.fromEntries(alertPreferenceBlueprint.map(item => [item.key, Boolean(alertPreferenceDraft[item.key])]))
    const { data } = await axios.post('/settings/notifications', { alert_preferences })
    if (data?.alert_preferences) Object.assign(alertPreferenceDraft, data.alert_preferences)
    setStatus(alertStatusMessage, alertStatusTone, 'Varslene ble oppdatert.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to save alert preferences:', error)
    setStatus(alertStatusMessage, alertStatusTone, error.response?.data?.msg || 'Kunne ikke lagre varselvalg.', 'settings-status-error')
  } finally {
    isSavingAlertPreferences.value = false
  }
}
async function savePrivacyWard() {
  try {
    isSavingPrivacyWard.value = true
    const privacy_preferences = Object.fromEntries(privacyWardBlueprint.map(item => [item.key, Boolean(privacyWardDraft[item.key])]))
    const { data } = await axios.post('/settings/privacy', { privacy_preferences })
    if (data?.privacy_preferences) Object.assign(privacyWardDraft, data.privacy_preferences)
    setStatus(privacyStatusMessage, privacyStatusTone, 'Personverninnstillingene ble oppdatert.', 'settings-status-success')
  } catch (error) {
    console.error('Failed to save privacy preferences:', error)
    setStatus(privacyStatusMessage, privacyStatusTone, error.response?.data?.msg || 'Kunne ikke lagre personvernvalg.', 'settings-status-error')
  } finally {
    isSavingPrivacyWard.value = false
  }
}
function openDangerZoneModal(actionKey) {
  if (actionKey === 'revoke_all') {
    Object.assign(dangerZoneModalState, { isOpen: true, actionKey, title: 'Logg ut alle aktive sesjoner', copy: 'Dette krever ny innlogging på alle enheter som bruker kontoen din.', confirmLabel: 'Logg ut alle', requiresPassword: false, currentPassword: '' })
    return
  }
  Object.assign(dangerZoneModalState, { isOpen: true, actionKey, title: 'Slett kontoen permanent', copy: 'Dette rydder opp i brukerdata og kan ikke angres.', confirmLabel: 'Slett konto', requiresPassword: true, currentPassword: '' })
}
function closeDangerZoneModal() {
  Object.assign(dangerZoneModalState, { isOpen: false, actionKey: '', title: '', copy: '', confirmLabel: '', requiresPassword: false, currentPassword: '' })
}
async function executeDangerZoneAction() {
  try {
    isExecutingDangerAction.value = true
    if (dangerZoneModalState.actionKey === 'revoke_all') {
      await axios.post('/settings/sessions/revoke-all')
      auth.logout()
      closeDangerZoneModal()
      router.push('/login')
      return
    }
    await axios.delete('/settings/account', { data: { current_password: dangerZoneModalState.currentPassword } })
    auth.logout()
    closeDangerZoneModal()
    router.push('/')
  } catch (error) {
    console.error('Failed danger zone action:', error)
    setStatus(dangerZoneStatusMessage, dangerZoneStatusTone, error.response?.data?.msg || 'Kunne ikke fullføre faresone-handlingen.', 'settings-status-error')
  } finally {
    isExecutingDangerAction.value = false
  }
}
watch(() => auth.user, (portalUser) => {
  if (portalUser) applyPortalUserToDrafts(portalUser)
}, { immediate: true })
onMounted(async () => {
  await hydratePortalUser()
  await Promise.all([hydratePortalConnectionRegistry(), hydrateAlertPreferences(), hydratePrivacyWard()])
})
</script>

<style scoped>
.settings-shell {
  min-height: calc(100vh - 64px);
  background: var(--bg, #080c12);
  color: var(--text, #b8ccd8);
  padding: 32px 0 80px;
}

.settings-frame {
  width: min(calc(100% - 2.5rem), 1100px);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.settings-sidebar {
  position: sticky;
  top: 84px;
}

.settings-sidebar-head {
  margin-bottom: 10px;
  padding: 0 10px;
}

.settings-sidebar-head h1,
.settings-page-header h2,
.danger-modal-card h3 {
  margin: 0;
  color: var(--bright, #eaf2ff);
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
  font-weight: 900;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.settings-sidebar-head h1 {
  font-size: 29px;
  line-height: 1;
}

.settings-sidebar-head p,
.settings-page-header p,
.settings-field small,
.settings-toggle-copy span,
.settings-connection-copy span,
.settings-connection-copy small,
.settings-danger-copy span,
.danger-modal-copy {
  margin: 0;
  color: var(--muted, #3d5668);
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-kicker {
  margin: 0 0 6px;
  color: var(--cyan, #00b8d0);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
}

.settings-kicker-muted {
  color: var(--muted, #3d5668);
}

.settings-nav-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.settings-nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--muted, #3d5668);
  text-align: left;
  cursor: pointer;
  transition: 0.15s ease;
}

.settings-nav-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text, #b8ccd8);
}

.settings-nav-btn.active {
  background: rgba(0, 184, 208, 0.08);
  color: var(--cyan, #00b8d0);
}

.settings-nav-btn.danger {
  margin-top: 12px;
}

.settings-nav-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.settings-nav-label {
  color: inherit;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-nav-hint {
  color: var(--muted, #3d5668);
  font-size: 12px;
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-nav-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.55;
  flex-shrink: 0;
}

.settings-nav-btn.active .settings-nav-dot {
  opacity: 1;
  box-shadow: 0 0 5px currentColor;
}

.settings-nav-btn.danger .settings-nav-dot {
  background: var(--red2, #e8304a);
  opacity: 1;
}

.settings-nav-badge {
  margin-left: auto;
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(200, 16, 46, 0.12);
  border: 1px solid rgba(200, 16, 46, 0.2);
  color: var(--red2, #e8304a);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
}

.settings-main {
  min-width: 0;
}

.settings-page-header {
  margin-bottom: 20px;
}

.settings-page-header h2 {
  font-size: 28px;
  line-height: 1;
  margin-bottom: 5px;
}

.settings-page-header em {
  color: var(--cyan, #00b8d0);
  font-style: normal;
}

.settings-page-header p {
  font-size: 13px;
}

.settings-panel,
.danger-modal-card {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border2, rgba(255, 255, 255, 0.11));
  border-radius: 12px;
  overflow: hidden;
}

.settings-panel-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  background: rgba(255, 255, 255, 0.02);
}

.settings-panel-head-danger {
  background: rgba(200, 16, 46, 0.04);
}

.settings-panel-title {
  flex: 1;
  color: var(--bright, #eaf2ff);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
}

.settings-panel-meta {
  color: var(--muted, #3d5668);
  font-size: 11px;
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-panel-body {
  padding: 20px;
}

.settings-profile-identity {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 22px;
}

.settings-profile-avatar,
.settings-profile-avatar-fallback,
.settings-linked-avatar,
.settings-linked-avatar-fallback {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.settings-profile-avatar,
.settings-profile-avatar-fallback {
  border: 3px solid rgba(200, 16, 46, 0.3);
}

.settings-profile-avatar-fallback,
.settings-linked-avatar-fallback {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--red, #c8102e), #7a0e1e);
  color: white;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
  font-size: 24px;
  font-weight: 900;
}

.settings-profile-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.settings-profile-copy strong,
.settings-connection-copy strong,
.settings-toggle-copy strong,
.settings-danger-copy strong,
.settings-linked-copy strong,
.settings-cod-copy strong {
  color: var(--bright, #eaf2ff);
  font-family: var(--font-body, 'Barlow', sans-serif);
  font-size: 14px;
  font-weight: 600;
}

.settings-profile-actions {
  margin-top: 8px;
}

.settings-form-grid {
  display: grid;
  gap: 14px;
}

.settings-form-grid-two {
  grid-template-columns: 1fr 1fr;
}

.settings-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.settings-field-spaced {
  margin-top: 14px;
}

.settings-field span {
  color: var(--muted, #3d5668);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
}

.settings-field input,
.settings-field textarea,
.settings-inline-field input {
  width: 100%;
  border-radius: 7px;
  border: 1px solid var(--border2, rgba(255, 255, 255, 0.11));
  background: var(--s2, #131e28);
  color: var(--bright, #eaf2ff);
  padding: 10px 13px;
  outline: none;
  transition: 0.15s ease;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
}

.settings-field input:focus,
.settings-field textarea:focus,
.settings-inline-field input:focus {
  border-color: var(--cyan, #00b8d0);
  box-shadow: 0 0 0 3px rgba(0, 184, 208, 0.1);
  background: var(--s3, #1a2535);
}

.settings-field textarea {
  resize: vertical;
  min-height: 96px;
  line-height: 1.6;
}

.settings-inline-field {
  display: flex;
  gap: 8px;
  align-items: center;
}

.settings-inline-field-compact {
  margin-top: 7px;
}

.settings-button-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 18px;
}

.settings-button-row.top-gap {
  margin-top: 16px;
}

.settings-primary-btn,
.settings-secondary-btn,
.settings-danger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 9px 20px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body, 'Barlow', sans-serif);
  cursor: pointer;
  transition: 0.18s ease;
}

.settings-primary-btn:hover,
.settings-secondary-btn:hover,
.settings-danger-btn:hover {
  transform: translateY(-1px);
}

.settings-primary-btn {
  border: none;
  color: white;
  background: linear-gradient(145deg, var(--red, #c8102e), #8a0e1e);
  box-shadow: 0 4px 16px rgba(200, 16, 46, 0.28);
}

.settings-secondary-btn {
  border: 1px solid var(--border2, rgba(255, 255, 255, 0.11));
  color: var(--text, #b8ccd8);
  background: rgba(255, 255, 255, 0.04);
}

.settings-secondary-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.settings-danger-btn {
  border: 1px solid rgba(200, 16, 46, 0.2);
  background: rgba(200, 16, 46, 0.1);
  color: var(--red2, #e8304a);
}

.settings-danger-btn:hover {
  background: rgba(200, 16, 46, 0.18);
}

.settings-btn-sm {
  padding: 6px 14px;
  font-size: 12px;
}

.settings-primary-btn:disabled,
.settings-secondary-btn:disabled,
.settings-danger-btn:disabled {
  opacity: 0.6;
  cursor: wait;
  transform: none;
}

.settings-connection-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
}

.settings-connection-divider.spaced {
  margin-top: 12px;
}

.settings-connection-divider span {
  color: var(--muted, #3d5668);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  white-space: nowrap;
  font-family: var(--font-display, 'Barlow Condensed', sans-serif);
}

.settings-connection-divider div {
  flex: 1;
  height: 1px;
  background: var(--border, rgba(255, 255, 255, 0.07));
}

.settings-connection-list,
.settings-cod-results,
.settings-toggle-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.settings-connection-list {
  margin-top: 10px;
}

.settings-connection-card,
.settings-toggle-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 13px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  border-radius: 9px;
  transition: 0.15s ease;
}

.settings-connection-card.connected {
  border-color: rgba(40, 184, 96, 0.2);
  background: rgba(40, 184, 96, 0.03);
}

.settings-connection-icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.provider-steam .settings-connection-icon { background: rgba(27, 159, 212, 0.12); border: 1px solid rgba(27, 159, 212, 0.22); }
.provider-xbox .settings-connection-icon { background: rgba(16, 124, 16, 0.12); border: 1px solid rgba(16, 124, 16, 0.22); }
.provider-battlenet .settings-connection-icon { background: rgba(20, 142, 255, 0.12); border: 1px solid rgba(20, 142, 255, 0.22); }
.provider-discord .settings-connection-icon { background: rgba(88, 101, 242, 0.12); border: 1px solid rgba(88, 101, 242, 0.22); }
.provider-cod .settings-connection-icon { background: rgba(200, 16, 46, 0.12); border: 1px solid rgba(200, 16, 46, 0.22); }
.provider-epic .settings-connection-icon { background: rgba(216, 152, 32, 0.1); border: 1px solid rgba(216, 152, 32, 0.2); }

.settings-connection-copy {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-connection-copy.grow {
  flex: 1;
}

.settings-connection-copy .is-on {
  color: var(--green, #28b860);
}

.settings-connection-copy .is-off {
  color: var(--muted, #3d5668);
}

.settings-connection-actions {
  flex-shrink: 0;
}

.manual-card {
  margin-top: 10px;
}

.settings-manual-linked {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.settings-linked-copy,
.settings-cod-copy {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-cod-result {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  border: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.02);
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.settings-cod-action {
  color: var(--cyan, #00b8d0);
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-toggle-list {
  gap: 0;
}

.settings-toggle-row {
  justify-content: space-between;
  padding: 12px 0;
  border: 0;
  border-bottom: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  border-radius: 0;
  background: transparent;
}

.settings-toggle-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.settings-toggle-row:first-child {
  padding-top: 0;
}

.settings-toggle-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.settings-toggle-switch {
  position: relative;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
  margin-left: 16px;
}

.settings-toggle-switch input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.settings-toggle-track {
  position: absolute;
  inset: 0;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border2, rgba(255, 255, 255, 0.11));
  transition: 0.2s ease;
}

.settings-toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--muted, #3d5668);
  transition: 0.2s ease;
}

.settings-toggle-switch input:checked + .settings-toggle-track {
  background: rgba(0, 184, 208, 0.25);
  border-color: rgba(0, 184, 208, 0.45);
}

.settings-toggle-switch input:checked + .settings-toggle-track + .settings-toggle-thumb {
  left: 21px;
  background: var(--cyan, #00b8d0);
  box-shadow: 0 0 6px rgba(0, 184, 208, 0.5);
}

.settings-panel-danger {
  border-color: rgba(200, 16, 46, 0.2);
}

.settings-danger-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-danger-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.settings-danger-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.settings-danger-divider {
  height: 1px;
  background: rgba(200, 16, 46, 0.1);
}

.settings-status {
  margin-top: 12px;
  font-size: 12px;
  font-family: var(--font-body, 'Barlow', sans-serif);
}

.settings-status.compact {
  margin-top: 8px;
}

.settings-status-success { color: var(--green, #28b860); }
.settings-status-error { color: var(--red2, #e8304a); }
.settings-status-muted { color: var(--muted, #3d5668); }

.danger-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(2, 6, 12, 0.72);
}

.danger-modal-card {
  width: min(520px, 100%);
  padding: 24px;
}

.danger-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}

@media (max-width: 900px) {
  .settings-frame {
    grid-template-columns: 1fr;
  }

  .settings-sidebar {
    position: static;
  }
}

@media (max-width: 760px) {
  .settings-shell {
    padding: 20px 0 48px;
  }

  .settings-frame {
    width: min(calc(100% - 1.5rem), 1100px);
    gap: 18px;
  }

  .settings-form-grid-two,
  .settings-inline-field,
  .settings-danger-row,
  .settings-profile-identity,
  .settings-cod-result,
  .settings-manual-linked,
  .settings-toggle-row,
  .danger-modal-actions,
  .settings-button-row {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .settings-toggle-switch {
    margin-left: 0;
  }
}
</style>

