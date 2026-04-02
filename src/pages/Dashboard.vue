<template>
  <div class="dashboard-page">
    <div class="profile-banner" :style="bannerStyle">
      <div class="banner-grid"></div>
      <button class="banner-edit" @click="triggerBannerUpload" :disabled="isUploadingBanner">
        {{ isUploadingBanner ? 'Laster opp...' : 'Endre banner' }}
      </button>
      <input
        ref="bannerInput"
        type="file"
        accept="image/*"
        @change="handleBannerImageChange"
        hidden
      />
    </div>

    <div class="profile-header-wrap">
      <div class="hmn-container">
        <div v-if="user" class="profile-header">
          <div class="profile-top">
            <div class="profile-left">
              <div class="avatar-wrap">
                <label for="dashboard-avatar-upload" class="avatar avatar-button">
                  <img v-if="user.avatar" :src="user.avatar" class="avatar-img" alt="avatar" />
                  <span v-else>{{ initials }}</span>
                  <span class="avatar-overlay">✎</span>
                </label>
                <input
                  id="dashboard-avatar-upload"
                  type="file"
                  accept="image/*"
                  @change="handleProfilePicChange"
                  hidden
                />
                <div class="avatar-online"></div>
              </div>

              <div class="profile-info">
                <div class="profile-name-row">
                  <span class="profile-name">{{ displayName }}</span>
                  <div class="pbadges">
                    <span
                      v-for="role in normalizedRoles"
                      :key="role.id || role.name"
                      class="pbadge"
                      :class="badgeClass(role.name)"
                    >
                      {{ role.name }}
                    </span>
                  </div>
                </div>
                <div class="profile-sub">
                  <span class="profile-joined">Pasient siden januar 2024</span>
                  <span class="profile-online"><span class="profile-online-dot"></span>Online nå</span>
                </div>
              </div>
            </div>

            <div class="profile-actions">
              <button class="btn btn-ghost btn-sm" @click="toggleBioEdit">
                {{ isEditingBio ? 'Avbryt' : 'Rediger profil' }}
              </button>
              <button class="btn btn-ghost btn-sm" @click="goToSettings">Innstillinger</button>
            </div>
          </div>

          <div class="profile-tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              class="ptab"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-body">
      <div class="hmn-container">
        <div v-if="!user" class="loading-state">Laster dashboard...</div>

        <div v-else>
          <div v-show="activeTab === 'oversikt'" class="pg">
            <div class="col">
              <RankCard
                v-if="primaryRole"
                :variant="primaryRole.name.toLowerCase()"
                :name="primaryRole.name"
                since="januar 2024"
              />

              <div class="scard">
                <div class="sh">
                  <span class="sh-t">Om meg</span>
                  <button class="sh-a" @click="toggleBioEdit">{{ isEditingBio ? 'Avbryt' : 'Rediger' }}</button>
                </div>
                <div class="sb">
                  <div v-if="isEditingBio" class="bio-editor">
                    <textarea v-model="newBio" class="bio-input" maxlength="300"></textarea>
                    <div class="bio-editor-footer">
                      <span class="bio-count" :class="{ danger: remainingChars < 0 }">{{ remainingChars }} tegn igjen</span>
                      <div class="bio-actions">
                        <button class="btn btn-ghost btn-sm" @click="cancelEditBio">Avbryt</button>
                        <button class="btn btn-red btn-sm" @click="updateBio" :disabled="remainingChars < 0 || isSavingBio">
                          {{ isSavingBio ? 'Lagrer...' : 'Lagre' }}
                        </button>
                      </div>
                    </div>
                  </div>
                  <p v-else class="bio-text">"{{ bioDisplay }}"</p>
                </div>
              </div>

              <div class="scard">
                <div class="sh"><span class="sh-t">Pasientstatus</span></div>
                <div class="stat-rows">
                  <div class="sr"><span class="sr-label">Krenkethetsnivå</span><span class="sr-val c-red">{{ krenketDisplay }}</span></div>
                  <div class="sr"><span class="sr-label">Achievements</span><span class="sr-val c-cyan">{{ achievementCount }}</span></div>
                  <div class="sr"><span class="sr-label">Hendelser deltatt</span><span class="sr-val c-gold">{{ attendedEvents }}</span></div>
                  <div class="sr"><span class="sr-label">Uforklarte hendelser</span><span class="sr-val c-green">{{ blameScore }}</span></div>
                </div>
              </div>

              <div class="scard">
                <div class="sh"><span class="sh-t">Tilkoblede kontoer</span><span class="sh-a">Administrer</span></div>
                <div class="sb">
                  <div class="conn-list">
                    <div v-for="connection in resolvedConnections" :key="connection.provider" class="conn">
                      <div class="conn-icon" :class="connection.iconClass">{{ connection.abbr }}</div>
                      <div class="conn-info">
                        <div class="conn-name">{{ connection.name }}</div>
                        <div class="conn-user">{{ connection.userText }}</div>
                      </div>
                      <div class="conn-dot" :class="connection.connected ? 'cd-on' : 'cd-off'"></div>
                      <button
                        class="conn-btn"
                        :class="connection.connected ? 'cb-on' : 'cb-off'"
                        :disabled="!connection.actionable || connectionActionProvider === connection.provider || connectionsLoading"
                        @click="handleConnectionAction(connection)"
                      >
                        {{
                          connectionActionProvider === connection.provider
                            ? 'Jobber...'
                            : connection.connected
                              ? (connection.actionable ? 'Koble fra' : 'Tilkoblet')
                              : 'Koble til'
                        }}
                      </button>
                    </div>
                  </div>
                  <div v-if="connectionStatus" class="conn-status" :class="connectionStatusType">{{ connectionStatus }}</div>
                </div>
              </div>
            </div>

            <div class="col">
              <div class="mc">
                <div class="np-strip">
                  <div class="np-dot"></div>
                  <span class="np-live">Spiller nå</span>
                  <span class="np-game">Satisfactory · {{ activityLabel }}</span>
                  <span class="np-via">Steam</span>
                  <div v-if="gamingSummary?.current_game" class="np-overlay">
                    <span class="np-game">{{ nowPlayingTitle }}</span>
                    <span class="np-via">{{ nowPlayingProvider }}</span>
                  </div>
                </div>
                <div class="mc-head"><span class="mc-title">Siste spilte</span><span class="mc-meta">siste 2 uker</span></div>
                <div class="game-grid">
                  <div v-for="game in recentGames" :key="game.id" class="gc">
                    <div class="gc-art" :class="game.artClass" :style="game.artStyle">
                      <img v-if="game.imageUrl" :src="game.imageUrl" :alt="game.title" class="gc-art-img" />
                      <span v-else>{{ game.code }}</span>
                      <div class="gc-pip" :class="game.platformClass">{{ game.platform }}</div>
                    </div>
                    <div class="gc-body">
                      <div class="gc-title">{{ game.title }}</div>
                      <div class="gc-stats"><span>{{ game.leftStat }}</span><span>{{ game.rightStat }}</span></div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mc">
                <div class="mc-head"><span class="mc-title">Siste achievements</span><span class="mc-meta">nylig låst opp</span></div>
                <div v-if="recentAchievementsDisclaimer" class="mc-note">{{ recentAchievementsDisclaimer }}</div>
                <div v-if="showRecentAchievementsEmptyState" class="ach-empty">
                  <div class="ach-empty-orbit"></div>
                  <div class="ach-empty-medallion">
                    <div class="ach-empty-core">🏆</div>
                  </div>
                  <div class="ach-empty-copy">
                    <div class="ach-empty-title">Ingen achievements enda</div>
                    <div class="ach-empty-text">Denne seksjonen fylles automatisk når du låser opp achievements i HMN Portalen, Steam eller Xbox.</div>
                    <div class="ach-empty-subtle">Første unlock får hedersplassen her. Inntil videre er tavla mistenkelig ren.</div>
                  </div>
                </div>
                <div v-else class="ach-grid">
                  <div v-for="achievement in recentAchievements" :key="achievement.id" class="ai">
                    <div class="ai-icon" :class="achievement.iconClass">
                      <img v-if="achievement.isImg" :src="achievement.icon" class="ai-icon-img" />
                      <span v-else>{{ achievement.icon }}</span>
                    </div>
                    <div class="ai-info">
                      <div class="ai-name">{{ achievement.title }}</div>
                      <div class="ai-game">{{ achievement.game }}</div>
                    </div>
                    <span class="ai-plat" :class="achievement.platformClass">{{ achievement.platform }}</span>
                  </div>
                </div>
              </div>

              <div class="mc">
                <div class="mc-head"><span class="mc-title">Helsejournal</span><span class="mc-meta">§ 4.4 kontinuerlig oppdatert</span></div>
                <div class="krenket">
                  <div class="kr-row"><span class="kr-label">Krenkethetsnivå</span><span class="kr-val">{{ krenketDisplay }} · {{ krenketLabel }}</span></div>
                  <div class="kr-track"><div class="kr-fill" :style="{ width: krenketPercent }"></div></div>
                  <div class="kr-sub">{{ krenketSubline }}</div>
                </div>
                <div class="kr-stats">
                  <div class="krs"><div class="krs-val c-gold">3</div><div class="krs-label">Kaffe i dag</div></div>
                  <div class="krs"><div class="krs-val c-cyan">{{ lastSeenOutside }}</div><div class="krs-label">Sist sett ute</div></div>
                  <div class="krs"><div class="krs-val c-green">Stabil</div><div class="krs-label">Diagnose</div></div>
                </div>
              </div>

              <div class="mc">
                <div class="mc-head"><span class="mc-title">Nylig aktivitet</span></div>
                <div class="act-list">
                  <div v-for="item in recentActivity" :key="item.id" class="act">
                    <div class="act-dot" :class="item.dotClass"></div>
                    <span class="act-text">{{ item.text }}</span>
                    <span class="act-time">{{ item.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'gaming'" class="pg">
            <div class="col">
              <div class="scard">
                <div class="sh"><span class="sh-t">Plattformer</span></div>
                <div class="sb platform-list">
                  <div v-for="platform in dynamicGamingPlatforms" :key="platform.id" class="platform-item" :class="platform.panelClass">
                    <div class="conn-icon" :class="platform.iconClass">{{ platform.abbr }}</div>
                    <div>
                      <div class="platform-name">{{ platform.name }}</div>
                      <div class="platform-sub">{{ platform.meta }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="scard">
                <div class="sh"><span class="sh-t">Totalt</span></div>
                <div class="stat-rows">
                  <div class="sr"><span class="sr-label">Total spilltid</span><span class="sr-val c-cyan">{{ gamingTotalHours }}</span></div>
                  <div class="sr"><span class="sr-label">Gamerscore</span><span class="sr-val c-gold">—</span></div>
                  <div class="sr"><span class="sr-label">Spill eiet</span><span class="sr-val c-green">{{ gamingOwnedGames }}</span></div>
                  <div class="sr"><span class="sr-label">Achievements</span><span class="sr-val c-red">—</span></div>
                </div>
              </div>
            </div>

            <div class="col">
              <div class="mc">
                <div class="np-strip">
                  <div class="np-dot"></div>
                  <span class="np-live">Spiller nå</span>
                  <span class="np-game">Satisfactory · 2t 14m</span>
                  <span class="np-via">Steam</span>
                  <div v-if="gamingSummary?.current_game" class="np-overlay">
                    <span class="np-game">{{ nowPlayingTitle }}</span>
                    <span class="np-via">{{ nowPlayingProvider }}</span>
                  </div>
                </div>
                <div class="mc-head"><span class="mc-title">Alle spill</span><span class="mc-meta">{{ gamingOwnedGames }} totalt</span></div>
                <div class="game-grid all-games-grid">
                  <div v-for="game in allGames" :key="game.id" class="gc">
                    <div class="gc-art" :class="game.artClass" :style="game.artStyle">
                      <img v-if="game.imageUrl" :src="game.imageUrl" :alt="game.title" class="gc-art-img" />
                      <span v-else>{{ game.code }}</span>
                      <div class="gc-pip" :class="game.platformClass">{{ game.platform }}</div>
                    </div>
                    <div class="gc-body">
                      <div class="gc-title">{{ game.title }}</div>
                      <div class="gc-stats"><span>{{ game.leftStat }}</span><span>{{ game.rightStat }}</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'achievements'" class="tab-single">
            <div class="mc">
              <div class="mc-head"><span class="mc-title">Alle achievements</span><span class="mc-meta">{{ achievementCount }} totalt</span></div>
              <div class="achievement-panel-wrap">
                <AchievementPanel />
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'aktivitet'" class="tab-single">
            <div class="mc">
              <div class="mc-head"><span class="mc-title">All aktivitet</span></div>
              <div class="act-list">
                <div v-for="item in fullActivity" :key="item.id" class="act">
                  <div class="act-dot" :class="item.dotClass"></div>
                  <span class="act-text">{{ item.text }}</span>
                  <span class="act-time">{{ item.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/axios'
import { useAuthStore } from '@/stores/authStore'
import {
  disconnectConnection,
  fetchConnections,
} from '@/services/connectionService'
import RankCard from '@/components/RankCard.vue'
import AchievementPanel from '@/components/AchievementPanel.vue'

const tabs = [
  { id: 'oversikt', label: 'Oversikt' },
  { id: 'gaming', label: 'Gaming' },
  { id: 'achievements', label: 'Achievements' },
  { id: 'aktivitet', label: 'Aktivitet' },
]

const rolePriority = ['admin', 'superadmin', 'developer', 'staff', 'moderator', 'producer', 'overlege', 'junior', 'member']
const badgeClasses = {
  admin: 'pb-red',
  superadmin: 'pb-red',
  developer: 'pb-cyan',
  staff: 'pb-cyan',
  moderator: 'pb-gold',
  producer: 'pb-green',
  overlege: 'pb-gold',
  junior: 'pb-gold',
  member: 'pb-muted',
}

const fallbackGames = [
  { id: 1, code: 'SF', title: 'Satisfactory', leftStat: '847t', rightStat: '42/58 ach', platform: 'Steam', artClass: 'ga1', platformClass: 'gp-s' },
  { id: 2, code: 'CS2', title: 'Counter-Strike 2', leftStat: '312t', rightStat: '18/167 ach', platform: 'Steam', artClass: 'ga2', platformClass: 'gp-s' },
  { id: 3, code: 'HW2', title: 'Halo Wars 2', leftStat: '1,800G', rightStat: '60/90 ach', platform: 'Xbox', artClass: 'ga3', platformClass: 'gp-x' },
]

const fallbackAllGames = [
  ...fallbackGames,
  { id: 4, code: 'RDR2', title: 'Red Dead Redemption 2', leftStat: '98t', rightStat: '51/51', platform: 'Steam', artClass: 'ga4', platformClass: 'gp-s' },
  { id: 5, code: 'OW2', title: 'Overwatch 2', leftStat: 'Gold', rightStat: '58% win', platform: 'Bnet', artClass: 'ga5', platformClass: 'gp-b' },
  { id: 6, code: 'D4', title: 'Diablo IV', leftStat: '220t', rightStat: 'S8', platform: 'Bnet', artClass: 'ga6', platformClass: 'gp-b' },
]

const fallbackActivity = [
  { id: 1, text: 'Låste opp Fully Automated i Satisfactory', time: '12m', dotClass: 'ad-g' },
  { id: 2, text: 'Bekreftet oppmøte til Olivers Party', time: '2t', dotClass: 'ad-c' },
  { id: 3, text: 'Rang oppdatert - nå Overlege', time: 'i går', dotClass: 'ad-o' },
  { id: 4, text: 'Fikk skylda for deployment-feilen - § 2.1', time: 'i går', dotClass: 'ad-r' },
  { id: 5, text: 'Koblet til Steam-konto', time: '3d', dotClass: 'ad-m' },
]

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('oversikt')
const bannerInput = ref(null)
const isUploadingBanner = ref(false)
const isUploadingAvatar = ref(false)
const isEditingBio = ref(false)
const isSavingBio = ref(false)
const newBio = ref('')
const labActivity = ref(0)
const krenkeLevel = ref(0)
const achievements = ref([])
const recentActivityApi = ref([])
const connectionsData = ref([])
const connectionsLoading = ref(false)
const connectionActionProvider = ref('')
const connectionStatus = ref('')
const connectionStatusType = ref('status-muted')
const gamingSummary = ref(null)
const recentAchievementsSummary = ref(null)

const user = computed(() => auth.user)
const displayName = computed(() => user.value?.username || user.value?.email || 'Bruker')
const initials = computed(() => (displayName.value[0] || 'B').toUpperCase())
const normalizedRoles = computed(() => (user.value?.roles || []).map(role => ({ ...role, name: role.name || 'member' })))

const primaryRole = computed(() => {
  if (!normalizedRoles.value.length) return null
  return [...normalizedRoles.value].sort((left, right) => {
    const leftIndex = rolePriority.indexOf(left.name.toLowerCase())
    const rightIndex = rolePriority.indexOf(right.name.toLowerCase())
    return (leftIndex === -1 ? 99 : leftIndex) - (rightIndex === -1 ? 99 : rightIndex)
  })[0]
})

const bannerToShow = computed(() => user.value?.banner || '')
const bannerStyle = computed(() => (
  bannerToShow.value
    ? { backgroundImage: `linear-gradient(rgba(8,12,18,0.45), rgba(8,12,18,0.15)), url(${bannerToShow.value})` }
    : {}
))

const remainingChars = computed(() => 300 - newBio.value.length)
const bioDisplay = computed(() => user.value?.bio || 'Developersssssass. Ansvarlig for alt som går galt. Og bra. Men mest galt.')
const krenketValue = computed(() => Math.min(100, Math.max(0, Number(krenkeLevel.value) || 0)))
const krenketDisplay = computed(() => `${Math.round(krenketValue.value)}%`)
const krenketPercent = computed(() => `${krenketValue.value}%`)
const krenketLabel = computed(() => {
  if (krenketValue.value < 20) return 'Lav'
  if (krenketValue.value < 50) return 'Moderat'
  if (krenketValue.value < 75) return 'Forhøyet'
  return 'Kritisk'
})
const krenketSubline = computed(() => {
  if (krenketValue.value < 20) return 'Overraskende stabil. Mistanke om at noe er galt.'
  if (krenketValue.value < 50) return 'Under kontroll, men fortsatt mottakelig for småprovokasjon.'
  if (krenketValue.value < 75) return 'Stigende etter torsdagsmøtet. Behandles med kebab.'
  return 'Kritisk nivå. Krever umiddelbar pause og energidrikk.'
})

const achievementCount = computed(() => achievements.value.length || 0)
const attendedEvents = computed(() => Math.max(7, Math.min(99, recentActivity.value.length + 2)))
const blameScore = computed(() => '∞')
const lastSeenOutside = computed(() => (labActivity.value >= 1 ? '2d' : '5d'))
const activityLabel = computed(() => `${labActivity.value}t denne uken`)

const connections = computed(() => [
  { id: 1, name: 'Steam', abbr: 'S', iconClass: 'ci-s', connected: true, userText: `${displayName.value} · 1,240t` },
  { id: 2, name: 'Xbox', abbr: 'X', iconClass: 'ci-x', connected: true, userText: `${displayName.value} · 48,350G` },
  { id: 3, name: 'Battle.net', abbr: 'B', iconClass: 'ci-b', connected: false, userText: 'Ikke tilkoblet' },
  { id: 4, name: 'Discord', abbr: 'D', iconClass: 'ci-d', connected: true, userText: `${displayName.value}#0001` },
])

const recentGames = computed(() => recentGamesDynamic.value)
const allGames = computed(() => allGamesDynamic.value)
const unlockedAchievements = computed(() => achievements.value.filter(item => item.achieved !== false))
const recentAchievements = computed(() => {
  const items = Array.isArray(recentAchievementsSummary.value?.items) ? recentAchievementsSummary.value.items : []
  if (items.length) {
    return items.map(item => ({
      id: item.id,
      title: item.title,
      game: item.game,
      icon: item.icon,
      isImg: Boolean(item.is_img),
      iconClass: item.icon_class || 'air',
      platform: item.platform,
      platformClass: item.platform_class || 'aph',
    }))
  }
  return unlockedAchievements.value
    .slice(0, 4)
    .map((item, index) => {
      const rawIcon = item.icon || item.svg || ''
      const isImg = typeof rawIcon === 'string' && (rawIcon.startsWith('http') || rawIcon.startsWith('data:'))
      return {
        id: item.id,
        title: item.title,
        game: item.category || 'HMN Portalen',
        icon: rawIcon || ['🏆', '🎯', '⚔️', '🔥'][index % 4],
        isImg,
        iconClass: ['aig', 'aic', 'aigg', 'air'][index % 4],
        platform: item.category === 'clicker' ? 'Clicker' : 'HMN',
        platformClass: item.category === 'clicker' ? 'apx' : 'aph',
      }
    })
})
const showRecentAchievementsEmptyState = computed(() => unlockedAchievements.value.length === 0)
const recentAchievementsDisclaimer = computed(() => {
  if (showRecentAchievementsEmptyState.value) return ''
  return recentAchievementsSummary.value?.disclaimer || ''
})

const recentActivity = computed(() => recentActivityApi.value.length ? recentActivityApi.value.slice(0, 5) : fallbackActivity)
const fullActivity = computed(() => recentActivityApi.value.length ? [...recentActivityApi.value, ...fallbackActivity].slice(0, 8) : fallbackActivity)
const gamingPlatforms = computed(() => [
  { id: 1, name: 'Steam', abbr: 'S', meta: '1,240t total spilltid', iconClass: 'ci-s', panelClass: 'platform-steam' },
  { id: 2, name: 'Xbox', abbr: 'X', meta: '48,350 Gamerscore', iconClass: 'ci-x', panelClass: 'platform-xbox' },
  { id: 3, name: 'Battle.net', abbr: 'B', meta: 'Ikke tilkoblet', iconClass: 'ci-b', panelClass: 'platform-bnet' },
])

const connectionMeta = {
  steam: { name: 'Steam', abbr: 'S', iconClass: 'ci-s', actionable: true },
  xbox: { name: 'Xbox', abbr: 'X', iconClass: 'ci-x', actionable: true },
  battlenet: { name: 'Battle.net', abbr: 'B', iconClass: 'ci-b', actionable: false },
  discord: { name: 'Discord', abbr: 'D', iconClass: 'ci-d', actionable: false },
}

const resolvedConnections = computed(() => {
  if (!connectionsData.value.length) {
    return [
      { provider: 'steam', connected: false, subtitle: 'Ikke tilkoblet', ...connectionMeta.steam, userText: 'Ikke tilkoblet', actionable: true },
      { provider: 'xbox', connected: false, subtitle: 'Ikke tilkoblet', ...connectionMeta.xbox, userText: 'Ikke tilkoblet', actionable: true },
      { provider: 'battlenet', connected: false, subtitle: 'Kommer senere', ...connectionMeta.battlenet, userText: 'Kommer senere', actionable: false },
      {
        provider: 'discord',
        connected: Boolean(user.value?.discord_id),
        subtitle: user.value?.discord_id ? `Discord · ${String(user.value.discord_id).slice(-4)}` : 'Primær innlogging mangler',
        ...connectionMeta.discord,
        userText: user.value?.discord_id
          ? `${displayName.value} · Discord · ${String(user.value.discord_id).slice(-4)}`
          : 'Primær innlogging mangler',
        actionable: false
      },
    ]
  }

  return connectionsData.value.map(connection => {
    const meta = connectionMeta[connection.provider] || { name: connection.provider, abbr: '?', iconClass: 'ci-d', actionable: false }
    return {
      ...connection,
      ...meta,
      userText: connection.connected
        ? [connection.displayName, connection.subtitle].filter(Boolean).join(' · ')
        : (connection.subtitle || 'Ikke tilkoblet'),
      actionable: connection.connected
        ? ['steam', 'xbox'].includes(connection.provider)
        : ['steam', 'xbox'].includes(connection.provider) && meta.actionable,
    }
  })
})

const dynamicGamingPlatforms = computed(() => [
  {
    id: 1,
    name: 'Steam',
    abbr: 'S',
    meta: gamingSummary.value?.connected
      ? `${gamingTotalHours.value} total spilltid`
      : (resolvedConnections.value.find(item => item.provider === 'steam')?.userText || 'Ikke tilkoblet'),
    iconClass: 'ci-s',
    panelClass: 'platform-steam'
  },
  {
    id: 2,
    name: 'Xbox',
    abbr: 'X',
    meta: resolvedConnections.value.find(item => item.provider === 'xbox')?.userText || 'Ikke tilkoblet',
    iconClass: 'ci-x',
    panelClass: 'platform-xbox'
  },
  {
    id: 3,
    name: 'Battle.net',
    abbr: 'B',
    meta: 'Kommer senere',
    iconClass: 'ci-b',
    panelClass: 'platform-bnet'
  },
])

function buildGameVisualSeed(game) {
  const seed = Number(game?.id || 0) % 6
  const palettes = [
    'linear-gradient(135deg,#0a1628,#1a3a6a)',
    'linear-gradient(135deg,#280a0a,#6a1a1a)',
    'linear-gradient(135deg,#0a1a0a,#1a5a1a)',
    'linear-gradient(135deg,#241019,#6b2549)',
    'linear-gradient(135deg,#12122a,#323282)',
    'linear-gradient(135deg,#1b1809,#6c4b13)',
  ]
  return palettes[seed]
}

function normalizeSteamGame(game) {
  return {
    ...game,
    leftStat: game.leftStat || game.left_stat,
    rightStat: game.rightStat || game.right_stat,
    platformClass: game.platformClass || game.platform_class || 'gp-s',
    imageUrl: game.imageUrl || game.image_url || game.logo_url || null,
    artStyle: { background: buildGameVisualSeed(game) },
    artClass: '',
  }
}

const recentGamesDynamic = computed(() => {
  const games = Array.isArray(gamingSummary.value?.recent_games) ? gamingSummary.value.recent_games : []
  if (gamingSummary.value) {
    if (games.length) return games.map(normalizeSteamGame)
    if (gamingSummary.value.message) {
      return [{
        id: 'steam-message',
        code: 'ST',
        title: gamingSummary.value.message,
        leftStat: gamingSummary.value.connected ? 'Steam koblet til' : 'Ikke koblet til',
        rightStat: gamingSummary.value.configured ? 'Ingen nylige spill' : 'Mangler API-nøkkel',
        platform: 'Steam',
        platformClass: 'gp-s',
        artClass: 'ga1',
      }]
    }
    return []
  }
  return fallbackGames
})

const allGamesDynamic = computed(() => {
  const games = Array.isArray(gamingSummary.value?.all_games) ? gamingSummary.value.all_games : []
  if (gamingSummary.value) {
    if (games.length) return games.map(normalizeSteamGame)
    if (gamingSummary.value.message) {
      return [{
        id: 'steam-message-all',
        code: 'ST',
        title: gamingSummary.value.message,
        leftStat: gamingSummary.value.connected ? 'Steam koblet til' : 'Ikke koblet til',
        rightStat: gamingSummary.value.configured ? 'Ingen data enda' : 'Mangler API-nøkkel',
        platform: 'Steam',
        platformClass: 'gp-s',
        artClass: 'ga1',
      }]
    }
    return []
  }
  return fallbackAllGames
})

const nowPlayingTitle = computed(() => {
  if (gamingSummary.value?.current_game?.title) {
    return `${gamingSummary.value.current_game.title} · ${gamingSummary.value.current_game.subtitle}`
  }
  return `Ingen aktiv Steam-data · ${activityLabel.value}`
})

const nowPlayingProvider = computed(() => gamingSummary.value?.current_game?.provider || 'Steam')
const gamingTotalHours = computed(() => `${gamingSummary.value?.totals?.total_hours ?? 0}t`)
const gamingOwnedGames = computed(() => gamingSummary.value?.totals?.owned_games ?? 0)
const gamingSummaryMessage = computed(() => gamingSummary.value?.message || '')

let activityInterval = null
let secondsActive = 0
let isTabActive = true

function badgeClass(name) {
  return badgeClasses[(name || '').toLowerCase()] || 'pb-muted'
}

function toggleBioEdit() {
  if (isEditingBio.value) {
    cancelEditBio()
    return
  }
  newBio.value = user.value?.bio || ''
  isEditingBio.value = true
}

function cancelEditBio() {
  isEditingBio.value = false
  newBio.value = user.value?.bio || ''
}

async function updateBio() {
  if (remainingChars.value < 0 || isSavingBio.value) return
  try {
    isSavingBio.value = true
    const { data } = await axios.post('/update-profile', { bio: newBio.value })
    auth.$patch({ user: { ...auth.user, bio: data.user.bio } })
    localStorage.setItem('user', JSON.stringify(auth.user))
    isEditingBio.value = false
  } catch (error) {
    console.error('Error updating bio:', error)
  } finally {
    isSavingBio.value = false
  }
}

function triggerBannerUpload() {
  bannerInput.value?.click()
}

async function handleBannerImageChange(event) {
  const file = event.target.files?.[0]
  if (!file || !file.type.startsWith('image/')) return

  const formData = new FormData()
  formData.append('banner', file)

  try {
    isUploadingBanner.value = true
    const { data } = await axios.post('/upload-banner', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    auth.$patch({ user: { ...auth.user, banner: data.url } })
    localStorage.setItem('user', JSON.stringify(auth.user))
  } catch (error) {
    console.error('Banner upload failed:', error)
  } finally {
    isUploadingBanner.value = false
    event.target.value = ''
  }
}

async function handleProfilePicChange(event) {
  const file = event.target.files?.[0]
  if (!file || !file.type.startsWith('image/')) return

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    isUploadingAvatar.value = true
    const { data } = await axios.post('/upload-avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    auth.$patch({ user: { ...auth.user, avatar: data.url } })
    localStorage.setItem('user', JSON.stringify(auth.user))
  } catch (error) {
    console.error('Avatar upload failed:', error)
  } finally {
    isUploadingAvatar.value = false
    event.target.value = ''
  }
}

async function fetchWeeklyActivity() {
  try {
    const { data } = await axios.get('/get-weekly-activity')
    labActivity.value = data.weekly_hours ?? 0
  } catch (error) {
    console.error('Error fetching weekly activity:', error)
  }
}

async function fetchKrenkeLevel() {
  try {
    const { data } = await axios.get('/get-krenke-level')
    krenkeLevel.value = data.level ?? 0
  } catch (error) {
    console.error('Error fetching krenke level:', error)
  }
}

async function fetchAchievements() {
  try {
    const { data } = await axios.get('/user/achievements')
    achievements.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error fetching achievements:', error)
    achievements.value = []
  }
}

async function fetchRecentAchievementsSummary() {
  try {
    const { data } = await axios.get('/dashboard/recent-achievements')
    recentAchievementsSummary.value = data
  } catch (error) {
    console.error('Error fetching recent achievements summary:', error)
    recentAchievementsSummary.value = null
  }
}

function mapActivityDot(text) {
  const lower = text.toLowerCase()
  if (lower.includes('joined') || lower.includes('velkommen')) return 'ad-g'
  if (lower.includes('event') || lower.includes('oppmøte')) return 'ad-c'
  if (lower.includes('role') || lower.includes('rang')) return 'ad-o'
  if (lower.includes('error') || lower.includes('feil')) return 'ad-r'
  return 'ad-m'
}

async function fetchRecentActivity() {
  try {
    const { data } = await axios.get('/dashboard/latest-activity')
    const items = Array.isArray(data.latest_activity) ? data.latest_activity : []
    recentActivityApi.value = items.map((item, index) => ({
      id: `api-${index}`,
      text: item.text,
      time: item.timestamp || 'nå',
      dotClass: mapActivityDot(item.text || ''),
    }))
  } catch (error) {
    console.error('Error fetching latest activity:', error)
    recentActivityApi.value = []
  }
}

async function fetchConnectionData() {
  try {
    connectionsLoading.value = true
    const { data } = await fetchConnections()
    connectionsData.value = Array.isArray(data.connections) ? data.connections : []
  } catch (error) {
    console.error('Error fetching connections:', error)
    connectionsData.value = []
  } finally {
    connectionsLoading.value = false
  }
}

async function fetchGamingSummary() {
  try {
    const { data } = await axios.get('/dashboard/gaming-summary')
    gamingSummary.value = data
  } catch (error) {
    console.error('Error fetching gaming summary:', error)
    gamingSummary.value = {
      connected: false,
      configured: false,
      message: 'Kunne ikke hente Steam-data akkurat nå.',
      current_game: null,
      recent_games: [],
      all_games: [],
      totals: { total_hours: 0, owned_games: 0, recent_games: 0 },
    }
  }
}

async function handleConnectionAction(connection) {
  if (!connection?.actionable || connectionActionProvider.value) return

  try {
    connectionActionProvider.value = connection.provider

    if (connection.connected) {
      await disconnectConnection(connection.provider)
      connectionStatusType.value = 'status-success'
      connectionStatus.value = `${connection.name} ble koblet fra.`
      await fetchConnectionData()
      await fetchGamingSummary()
      return
    }

    const accessToken = localStorage.getItem('access_token')
    const apiBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

    if (!accessToken || !apiBase) {
      connectionStatusType.value = 'status-error'
      connectionStatus.value = `Mangler innloggingsdata for å starte ${connection.name}-koblingen.`
      return
    }

    if (connection.provider === 'steam') {
      window.location.href = `${apiBase}/connections/steam/start?access_token=${encodeURIComponent(accessToken)}`
      return
    }

    if (connection.provider === 'xbox') {
      window.location.href = `${apiBase}/connections/xbox/start?access_token=${encodeURIComponent(accessToken)}`
      return
    }

    connectionStatusType.value = 'status-error'
    connectionStatus.value = `Kunne ikke starte ${connection.name}-koblingen.`
  } catch (error) {
    console.error('Connection action failed:', error)
    connectionStatusType.value = 'status-error'
    connectionStatus.value = error.response?.data?.error || 'Noe gikk galt under kontokoblingen.'
  } finally {
    connectionActionProvider.value = ''
  }
}

async function sendActivityUpdate(seconds) {
  if (!seconds) return
  try {
    await axios.post('/track-dashboard-visit', { seconds })
  } catch (error) {
    console.error('Error sending activity update:', error)
  }
}

function startActivityTimer() {
  if (activityInterval) return
  activityInterval = window.setInterval(() => {
    if (!isTabActive) return
    secondsActive += 1
    if (secondsActive % 60 === 0) {
      sendActivityUpdate(60)
      secondsActive = 0
    }
  }, 1000)
}

function stopActivityTimer() {
  if (!activityInterval) return
  clearInterval(activityInterval)
  activityInterval = null
}

function handleVisibilityChange() {
  isTabActive = !document.hidden
  if (isTabActive) {
    startActivityTimer()
    return
  }
  sendActivityUpdate(secondsActive)
  secondsActive = 0
  stopActivityTimer()
}

function goToSettings() {
  router.push('/settings')
}

watch(user, currentUser => {
  newBio.value = currentUser?.bio || ''
}, { immediate: true })

onMounted(async () => {
  if (!auth.user && typeof auth.initialize === 'function') auth.initialize()
  let shouldClearConnectionQuery = false
  if (route.query.linked === 'steam') {
    connectionStatusType.value = 'status-success'
    connectionStatus.value = 'Steam-konto koblet til.'
    shouldClearConnectionQuery = true
  } else if (route.query.linked === 'xbox') {
    connectionStatusType.value = 'status-success'
    connectionStatus.value = 'Xbox-konto koblet til.'
    shouldClearConnectionQuery = true
  } else if (route.query.connection_error) {
    connectionStatusType.value = 'status-error'
    connectionStatus.value = route.query.connection_error.toString().startsWith('xbox_')
      ? 'Xbox-koblingen feilet. Prøv igjen.'
      : 'Steam-koblingen feilet. Prøv igjen.'
    shouldClearConnectionQuery = true
  }
  if (shouldClearConnectionQuery) {
    router.replace({ path: route.path, query: {} })
  }
  await Promise.all([
    auth.fetchFittePoints(),
    fetchWeeklyActivity(),
    fetchKrenkeLevel(),
    fetchAchievements(),
    fetchRecentAchievementsSummary(),
    fetchRecentActivity(),
    fetchConnectionData(),
    fetchGamingSummary(),
  ])
  startActivityTimer()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  sendActivityUpdate(secondsActive)
  stopActivityTimer()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

.profile-banner {
  height: 220px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0a1628 0%, #1a3a6a 40%, #0d1f40 70%, #1a0a28 100%);
  background-size: cover;
  background-position: center;
}

.profile-banner::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 80% at 80% 50%, rgba(0, 184, 208, 0.08), transparent 60%), radial-gradient(ellipse 40% 60% at 10% 80%, rgba(200, 16, 46, 0.07), transparent 50%);
}

.banner-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(0, 184, 208, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 184, 208, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

.banner-edit {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 1;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.7);
  font-size: 11px;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--font-body);
  backdrop-filter: blur(8px);
}

.banner-edit:disabled {
  opacity: 0.7;
  cursor: progress;
}

.banner-edit:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.6);
  color: white;
}

.profile-header-wrap {
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
}

.profile-header {
  padding: 0;
}

.profile-top {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 16px;
}

.profile-left {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.avatar-wrap {
  position: relative;
  margin-top: -52px;
  flex-shrink: 0;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--red), #7a0e1e);
  border: 4px solid var(--bg2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 900;
  color: white;
  box-shadow: 0 0 24px rgba(200, 16, 46, 0.3);
  position: relative;
  overflow: hidden;
}

.avatar-button {
  cursor: pointer;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.18s;
  font-size: 18px;
}

.avatar-button:hover .avatar-overlay {
  opacity: 1;
}

.avatar-online {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  background: var(--green);
  border-radius: 50%;
  border: 2px solid var(--bg2);
  box-shadow: 0 0 8px var(--green);
}

.profile-info {
  flex: 1;
  padding-top: 12px;
}

.profile-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.profile-name {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 900;
  color: var(--bright);
  letter-spacing: 0.02em;
  line-height: 1;
}

.pbadges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pbadge {
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.07em;
  font-family: var(--font-display);
  text-transform: uppercase;
}

.pb-red {
  background: rgba(200, 16, 46, 0.15);
  color: var(--red2);
  border: 1px solid rgba(200, 16, 46, 0.25);
}

.pb-cyan {
  background: rgba(0, 184, 208, 0.1);
  color: var(--cyan);
  border: 1px solid rgba(0, 184, 208, 0.2);
}

.pb-gold {
  background: rgba(216, 152, 32, 0.12);
  color: var(--gold);
  border: 1px solid rgba(216, 152, 32, 0.22);
}

.pb-green {
  background: rgba(40, 184, 96, 0.1);
  color: var(--green);
  border: 1px solid rgba(40, 184, 96, 0.2);
}

.pb-muted {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
  border: 1px solid var(--border);
}

.profile-sub {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.profile-joined {
  font-size: 12px;
  color: var(--muted);
}

.profile-online {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--green);
}

.profile-online-dot {
  width: 6px;
  height: 6px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--green);
}

.profile-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  flex-shrink: 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  border: none;
  transition: all 0.18s;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-red {
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  color: white;
  box-shadow: 0 4px 16px rgba(200, 16, 46, 0.28);
}

.btn-red:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border2);
  color: var(--text);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.08);
}

.btn-sm {
  padding: 6px 14px;
  font-size: 12px;
}

.profile-tabs {
  display: flex;
  border-top: 1px solid var(--border);
  margin-top: 8px;
  overflow-x: auto;
}

.ptab {
  padding: 12px 20px;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  cursor: pointer;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  transition: all 0.18s;
}

.ptab:hover {
  color: var(--text);
}

.ptab.active {
  color: var(--cyan);
  border-bottom-color: var(--cyan);
}

.profile-body {
  padding: 28px 0 72px;
}

.loading-state {
  padding: 48px 0;
  color: var(--muted);
  font-size: 14px;
}

.pg {
  display: grid;
  grid-template-columns: 290px 1fr;
  gap: 18px;
  align-items: start;
}

.col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tab-single {
  max-width: 100%;
}

.scard {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.sh {
  padding: 11px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sh-t {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 800;
  color: var(--bright);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.sh-a {
  font-size: 11px;
  color: var(--cyan);
  cursor: pointer;
  font-family: var(--font-body);
  background: transparent;
  border: none;
}

.sh-a:hover {
  text-decoration: underline;
}

.sb {
  padding: 14px 16px;
}

.bio-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.38);
  line-height: 1.75;
  font-family: var(--font-body);
  font-style: italic;
}

.bio-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bio-input {
  min-height: 110px;
  resize: vertical;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 12px;
  font: inherit;
}

.bio-editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.bio-count {
  font-size: 11px;
  color: var(--muted);
}

.bio-count.danger {
  color: var(--red2);
}

.bio-actions {
  display: flex;
  gap: 8px;
}

.stat-rows {
  padding: 0 16px;
}

.sr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid var(--border);
}

.sr:last-child {
  border-bottom: none;
}

.sr-label {
  font-size: 12px;
  color: var(--muted);
}

.sr-val {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 800;
}

.c-red {
  color: var(--red2);
}

.c-cyan {
  color: var(--cyan);
}

.c-gold {
  color: var(--gold);
}

.c-green {
  color: var(--green);
}

.conn-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.conn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
  transition: all 0.15s;
}

.conn:hover {
  background: rgba(255, 255, 255, 0.04);
}

.conn-icon {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 900;
  font-family: var(--font-display);
}

.ci-s {
  background: rgba(27, 159, 212, 0.15);
  color: #4ab8e8;
  border: 1px solid rgba(27, 159, 212, 0.25);
}

.ci-x {
  background: rgba(16, 124, 16, 0.15);
  color: #4ec84e;
  border: 1px solid rgba(16, 124, 16, 0.25);
}

.ci-b {
  background: rgba(20, 142, 255, 0.15);
  color: #60aeff;
  border: 1px solid rgba(20, 142, 255, 0.25);
}

.ci-d {
  background: rgba(88, 101, 242, 0.15);
  color: #8891f8;
  border: 1px solid rgba(88, 101, 242, 0.25);
}

.conn-info {
  flex: 1;
  min-width: 0;
}

.conn-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 1px;
}

.conn-user {
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conn-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cd-on {
  background: var(--green);
  box-shadow: 0 0 5px var(--green);
}

.cd-off {
  background: var(--muted);
}

.conn-btn {
  font-size: 10px;
  padding: 3px 9px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.06em;
  font-family: var(--font-display);
  text-transform: uppercase;
  cursor: pointer;
  border: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.15s;
}

.conn-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.cb-on {
  background: rgba(255, 255, 255, 0.04);
  color: var(--muted);
  border: 1px solid var(--border2);
}

.cb-off {
  background: rgba(0, 184, 208, 0.1);
  color: var(--cyan);
  border: 1px solid rgba(0, 184, 208, 0.2);
}

.conn-status {
  margin-top: 10px;
  padding: 9px 11px;
  border-radius: 7px;
  font-size: 11px;
  font-family: var(--font-body);
  border: 1px solid var(--border2);
}

.status-success {
  color: #7fe3a3;
  background: rgba(40, 184, 96, 0.08);
  border-color: rgba(40, 184, 96, 0.2);
}

.status-error {
  color: #ff7387;
  background: rgba(200, 16, 46, 0.08);
  border-color: rgba(200, 16, 46, 0.2);
}

.status-muted {
  color: var(--text);
  background: rgba(255, 255, 255, 0.03);
}

.mc {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border2);
  border-radius: 10px;
  overflow: hidden;
}

.mc-head {
  padding: 12px 18px;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mc-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 800;
  color: var(--bright);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.mc-meta {
  font-size: 11px;
  color: var(--muted);
}

.mc-note {
  padding: 10px 18px 0;
  font-size: 11px;
  color: var(--muted);
  line-height: 1.5;
}

.np-strip {
  padding: 9px 18px;
  background: rgba(40, 184, 96, 0.04);
  border-bottom: 1px solid rgba(40, 184, 96, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.np-dot {
  width: 8px;
  height: 8px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--green);
  flex-shrink: 0;
}

.np-live {
  font-size: 10px;
  color: var(--green);
  letter-spacing: 0.1em;
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
  flex-shrink: 0;
}

.np-game {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

.np-via {
  font-size: 11px;
  color: var(--muted);
  margin-left: auto;
}

.np-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 18px 9px 74px;
  background: rgba(15, 23, 32, 0.96);
}

.np-overlay .np-via {
  margin-left: auto;
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 14px 18px;
}

.all-games-grid {
  grid-template-columns: repeat(3, 1fr);
}

.gc {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.18s;
}

.gc:hover {
  border-color: var(--border2);
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4);
}

.gc-art {
  width: 100%;
  aspect-ratio: 16 / 9;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 900;
  font-size: 14px;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.1);
}

.gc-art > span {
  position: relative;
  z-index: 1;
}

.gc-art-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(1.05) contrast(1.02);
}

.ga1 { background: linear-gradient(135deg, #0a1628, #1a3a6a); }
.ga2 { background: linear-gradient(135deg, #280a0a, #6a1a1a); }
.ga3 { background: linear-gradient(135deg, #0a1a0a, #1a5a1a); }
.ga4 { background: linear-gradient(135deg, #1a0a28, #3a1a6a); }
.ga5 { background: linear-gradient(135deg, #281a0a, #6a4a1a); }
.ga6 { background: linear-gradient(135deg, #0a1a28, #1a3a5a); }

.gc-pip {
  position: absolute;
  top: 5px;
  right: 5px;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
  z-index: 1;
}

.gp-s { background: rgba(27, 159, 212, 0.25); color: #4ab8e8; }
.gp-x { background: rgba(16, 124, 16, 0.25); color: #4ec84e; }
.gp-b { background: rgba(20, 142, 255, 0.25); color: #60aeff; }

.gc-body {
  padding: 8px 10px;
}

.gc-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
  font-family: var(--font-body);
}

.gc-stats {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--muted);
}

.gc-stats span:first-child {
  color: var(--text);
  font-weight: 500;
}

.ach-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 14px 18px;
}

.ach-empty {
  position: relative;
  display: flex;
  align-items: center;
  gap: 18px;
  margin: 14px 18px 18px;
  padding: 20px 22px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background:
    radial-gradient(circle at top left, rgba(0, 184, 208, 0.12), transparent 34%),
    radial-gradient(circle at bottom right, rgba(200, 16, 46, 0.12), transparent 36%),
    linear-gradient(145deg, rgba(18, 26, 36, 0.96), rgba(13, 19, 27, 0.98));
  overflow: hidden;
}

.ach-empty::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(255,255,255,0.02), transparent 28%, transparent 72%, rgba(255,255,255,0.02));
  pointer-events: none;
}

.ach-empty-orbit {
  position: absolute;
  width: 180px;
  height: 180px;
  left: -42px;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: inset 0 0 0 16px rgba(255, 255, 255, 0.015);
  pointer-events: none;
}

.ach-empty-medallion {
  position: relative;
  z-index: 1;
  width: 74px;
  height: 74px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(216, 152, 32, 0.2), rgba(0, 184, 208, 0.12));
  border: 1px solid rgba(216, 152, 32, 0.24);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.28);
  flex-shrink: 0;
}

.ach-empty-core {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 16, 24, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 24px;
}

.ach-empty-copy {
  position: relative;
  z-index: 1;
  max-width: 520px;
}

.ach-empty-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: var(--bright);
  margin-bottom: 6px;
}

.ach-empty-text {
  font-size: 12px;
  line-height: 1.65;
  color: var(--text);
  max-width: 460px;
}

.ach-empty-subtle {
  margin-top: 8px;
  font-size: 10px;
  line-height: 1.6;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.ai {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 7px;
  background: var(--surface2);
  border: 1px solid var(--border);
}

.ai-icon {
  width: 34px;
  height: 34px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}
.ai-icon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.aig { background: rgba(216, 152, 32, 0.12); border: 1px solid rgba(216, 152, 32, 0.2); }
.aic { background: rgba(0, 184, 208, 0.1); border: 1px solid rgba(0, 184, 208, 0.18); }
.air { background: rgba(200, 16, 46, 0.1); border: 1px solid rgba(200, 16, 46, 0.18); }
.aigg { background: rgba(40, 184, 96, 0.1); border: 1px solid rgba(40, 184, 96, 0.18); }

.ai-info {
  flex: 1;
  min-width: 0;
}

.ai-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 2px;
  font-family: var(--font-body);
}

.ai-game {
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-plat {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
  flex-shrink: 0;
}

.aps { background: rgba(27, 159, 212, 0.12); color: #4ab8e8; }
.apx { background: rgba(16, 124, 16, 0.12); color: #4ec84e; }
.aph { background: rgba(200, 16, 46, 0.12); color: var(--red2); }

.krenket {
  padding: 14px 18px;
}

.kr-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kr-label {
  font-size: 12px;
  color: var(--muted);
}

.kr-val {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 800;
  color: var(--red2);
}

.kr-track {
  background: rgba(255, 255, 255, 0.06);
  height: 5px;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.kr-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--red), var(--red2));
  box-shadow: 0 0 8px rgba(200, 16, 46, 0.35);
}

.kr-sub {
  font-size: 11px;
  color: var(--muted);
  font-style: italic;
  font-family: var(--font-body);
}

.kr-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0;
  border-top: 1px solid var(--border);
}

.krs {
  padding: 11px 14px;
  text-align: center;
}

.krs:not(:last-child) {
  border-right: 1px solid var(--border);
}

.krs-val {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 800;
  line-height: 1;
}

.krs-label {
  font-size: 10px;
  color: var(--muted);
  margin-top: 3px;
}

.act-list {
  display: flex;
  flex-direction: column;
}

.act {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 18px;
  border-bottom: 1px solid var(--border);
}

.act:last-child {
  border-bottom: none;
}

.act:hover {
  background: rgba(255, 255, 255, 0.02);
}

.act-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ad-g { background: var(--green); box-shadow: 0 0 5px var(--green); }
.ad-c { background: var(--cyan); }
.ad-o { background: var(--gold); }
.ad-r { background: var(--red2); }
.ad-m { background: var(--muted); }

.act-text {
  flex: 1;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  font-family: var(--font-body);
}

.act-time {
  font-size: 11px;
  color: var(--muted);
  flex-shrink: 0;
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.platform-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 7px;
  border: 1px solid var(--border);
}

.platform-steam {
  background: rgba(27, 159, 212, 0.08);
  border-color: rgba(27, 159, 212, 0.2);
}

.platform-xbox {
  background: rgba(16, 124, 16, 0.08);
  border-color: rgba(16, 124, 16, 0.2);
}

.platform-bnet {
  background: rgba(255, 255, 255, 0.02);
  opacity: 0.55;
}

.platform-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  font-family: var(--font-body);
}

.platform-sub {
  font-size: 11px;
  color: var(--muted);
}

.achievement-panel-wrap {
  padding: 16px 18px;
}

@media (max-width: 980px) {
  .pg {
    grid-template-columns: 1fr;
  }

  .game-grid,
  .all-games-grid,
  .ach-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .profile-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-left {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-actions {
    padding-top: 0;
  }

  .profile-name {
    font-size: 22px;
  }

  .game-grid,
  .all-games-grid,
  .ach-grid,
  .kr-stats {
    grid-template-columns: 1fr;
  }

  .ach-empty {
    flex-direction: column;
    align-items: flex-start;
    padding: 18px;
  }

  .ach-empty-orbit {
    left: auto;
    right: -56px;
    top: -52px;
    transform: none;
  }

  .krs:not(:last-child) {
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .act {
    align-items: flex-start;
  }

  .act-time {
    margin-left: auto;
  }
}
</style>
