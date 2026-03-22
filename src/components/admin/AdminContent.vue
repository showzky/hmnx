<template>
  <main class="admin-content">
    <div class="content-area">
      <section v-if="isOnlyProducer && activeTab === 'content'">
        <div class="sec-head mb24">
          <div>
            <div class="sec-title">Hendelser / <em>Oversikt</em></div>
            <div class="sec-subtitle">Opprett og administrer kommende hendelser.</div>
          </div>
        </div>
        <div class="panel mb16">
          <div class="panel-head">
            <span class="panel-title">Eksisterende hendelser</span>
            <input
              type="text"
              :value="searchQuery"
              @input="$emit('update:searchQuery', $event.target.value)"
              placeholder="Sok hendelser..."
              class="search-input"
              style="max-width:220px;"
            />
          </div>
          <div class="panel-body" style="padding:0;">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:30px;"></th>
                  <th>Navn</th>
                  <th>Dato</th>
                  <th>Tid</th>
                  <th style="width:90px;">Handlinger</th>
                </tr>
              </thead>
              <tbody v-if="upcomingEventsData && upcomingEventsData.length">
                <tr v-for="element in upcomingEventsData" :key="element.id">
                  <td class="drag-handle">|||</td>
                  <td>{{ element.event_name }}</td>
                  <td>{{ formatDate(element.event_date) }}</td>
                  <td>{{ formatTime(element.event_time) }}</td>
                  <td>
                    <button class="btn btn-danger btn-sm" @click="$emit('deleteEvent', element.id)">
                      Slett
                    </button>
                  </td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr><td colspan="5" style="color:var(--muted);font-style:italic;">Ingen hendelser funnet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head"><span class="panel-title">Opprett ny hendelse</span></div>
          <div class="panel-body">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Navn</label>
                <input
                  class="form-input"
                  type="text"
                  :value="newEvent.event_name"
                  @input="updateNewEventField('event_name', $event.target.value)"
                  placeholder="Hendelsesnavn"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Dato</label>
                <input
                  class="form-input"
                  type="date"
                  :value="newEvent.event_date"
                  @input="updateNewEventField('event_date', $event.target.value)"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Tid</label>
                <input
                  class="form-input"
                  type="time"
                  :value="newEvent.event_time"
                  @input="updateNewEventField('event_time', $event.target.value)"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Mal</label>
                <select
                  class="form-select"
                  :value="newEvent.template_name"
                  @input="updateNewEventField('template_name', $event.target.value)"
                  required
                >
                  <option value="" disabled>Velg mal</option>
                  <option value="template1">Template 1 (Bilde-fokus)</option>
                  <option value="template2">Template 2 (Tekst-fokus)</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Beskrivelse (valgfritt)</label>
              <textarea
                class="form-textarea"
                :value="newEvent.event_description"
                @input="updateNewEventField('event_description', $event.target.value)"
                placeholder="Kort hendelsesinfo..."
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label class="file-upload-label">
                <span>Velg bilde</span>
                <input
                  type="file"
                  @change="$emit('handleImageUpload', $event)"
                  accept="image/*"
                  class="hidden-file-input"
                />
              </label>
            </div>
            <div class="form-group">
              <label class="custom-checkbox">
                <input
                  type="checkbox"
                  :checked="newEvent.notify_users"
                  @change="updateNewEventField('notify_users', $event.target.checked)"
                />
                <span style="color:var(--muted);font-size:13px;margin-left:6px;">Varsle alle brukere</span>
              </label>
            </div>
            <button class="btn btn-red" @click="$emit('createEvent')">Opprett</button>
            <div
              v-if="createEventMessage"
              class="form-message"
              :class="{ success: createEventSuccess, error: !createEventSuccess }"
              style="margin-top:10px;"
            >
              {{ createEventMessage }}
            </div>
          </div>
        </div>
      </section>

      <MusicTab
        v-if="activeTab === 'music'"
        :tracks="musicTracks"
        :message="musicMessage"
        :messageSuccess="musicSuccess"
        @addTrack="$emit('addTrack', $event)"
        @deleteTrack="$emit('deleteTrack', $event)"
        @setFeatured="$emit('setFeatured', $event)"
        @reorderTracks="$emit('reorderTracks', $event)"
      />

      <template v-if="!isOnlyProducer">
        <DashboardTab
          v-if="activeTab === 'dashboard'"
          :displayName="displayName"
          :totalUsers="usersList.length"
          :upcomingEventsData="upcomingEventsData"
          :widgets="widgets"
        />

        <SystemTab v-if="activeTab === 'system'" />

        <EventsTab
          v-if="activeTab === 'content'"
          :searchQuery="searchQuery"
          :upcomingEventsData="upcomingEventsData"
          :newEvent="newEvent"
          :createEventMessage="createEventMessage"
          :createEventSuccess="createEventSuccess"
          @deleteEvent="$emit('deleteEvent', $event)"
          @handleImageUpload="$emit('handleImageUpload', $event)"
          @createEvent="$emit('createEvent')"
          @update:searchQuery="$emit('update:searchQuery', $event)"
          @update:newEvent="$emit('update:newEvent', $event)"
        />

        <ShopTab v-if="activeTab === 'shop'" />

        <BedriftsmeldingTab v-if="activeTab === 'bedriftsmeldinger'" />

        <NewsTab v-if="activeTab === 'news'" />

        <UsersTab
          v-if="activeTab === 'users'"
          :userRoles="userRoles"
          :usersList="usersList"
          :userRoleUpdate="userRoleUpdate"
          :availableRoles="availableRoles"
          :updateUserMessage="updateUserMessage"
          :updateUserSuccess="updateUserSuccess"
          :selectedUserRoles="selectedUserRoles"
          :userRoleRemove="userRoleRemove"
          :selectedUserRolesToRemove="selectedUserRolesToRemove"
          :rolesToRemove="rolesToRemove"
          :removeRoleMessage="removeRoleMessage"
          :removeRoleSuccess="removeRoleSuccess"
          :newRole="newRole"
          :createRoleMessage="createRoleMessage"
          :createRoleSuccess="createRoleSuccess"
          @updateUserRole="$emit('updateUserRole')"
          @fetchUserRolesToRemove="$emit('fetchUserRolesToRemove')"
          @removeSelectedRoles="$emit('removeSelectedRoles')"
          @createRole="$emit('createRole')"
          @deleteRole="$emit('deleteRole', $event)"
          @update:userRoleUpdate="$emit('update:userRoleUpdate', $event)"
          @update:userRoleRemove="$emit('update:userRoleRemove', $event)"
          @update:rolesToRemove="$emit('update:rolesToRemove', $event)"
          @update:newRole="$emit('update:newRole', $event)"
        />

        <TeamTab
          v-if="activeTab === 'team'"
          :teamMembers="teamMembers"
          :defaultAvatar="defaultAvatar"
          :teamMessage="teamMessage"
          :teamSuccess="teamSuccess"
          @saveTeamMember="$emit('saveTeamMember', $event)"
          @deleteTeamMember="$emit('deleteTeamMember', $event)"
          @addNewTeamMember="$emit('addNewTeamMember')"
          @triggerAvatarUpload="$emit('triggerAvatarUpload', $event)"
          @update:teamMembers="$emit('update:teamMembers', $event)"
        />

        <SettingsTab
          v-if="activeTab === 'settings'"
          :maintenanceMode="maintenanceMode"
          :noticeMaintenanceMode="noticeMaintenanceMode"
          :maintenanceBannerMessage="maintenanceBannerMessage"
          :maintenanceMessage="maintenanceMessage"
          :maintenanceSuccess="maintenanceSuccess"
          :noticeMaintenanceMessage="noticeMaintenanceMessage"
          :noticeMaintenanceSuccess="noticeMaintenanceSuccess"
          @onToggleMaintenance="$emit('onToggleMaintenance')"
          @onToggleNoticeMaintenance="$emit('onToggleNoticeMaintenance')"
          @update:maintenanceMode="$emit('update:maintenanceMode', $event)"
          @update:noticeMaintenanceMode="$emit('update:noticeMaintenanceMode', $event)"
          @update:maintenanceBannerMessage="$emit('update:maintenanceBannerMessage', $event)"
        />

        <ChangeLogTab
          v-if="activeTab === 'changelog'"
          :newChangelog="newChangelog"
          :changelogEntries="changelogEntries"
          :changelogMessage="changelogMessage"
          :changelogSuccess="changelogSuccess"
          @submitChangelogEntry="$emit('submitChangelogEntry')"
          @deleteChangelogEntry="$emit('deleteChangelogEntry', $event)"
          @update:newChangelog="$emit('update:newChangelog', $event)"
        />

        <AchievementTab v-if="activeTab === 'achievements'" :achievements="achievements" />
      </template>
    </div>
  </main>
</template>

<script>
import AchievementTab from './tabs/AchievementTab.vue';
import BedriftsmeldingTab from './tabs/BedriftsmeldingTab.vue';
import ChangeLogTab from './tabs/ChangeLogTab.vue';
import DashboardTab from './tabs/DashboardTab.vue';
import EventsTab from './tabs/EventsTab.vue';
import MusicTab from './tabs/MusicTab.vue';
import NewsTab from './tabs/NewsTab.vue';
import SettingsTab from './tabs/SettingsTab.vue';
import ShopTab from './tabs/ShopTab.vue';
import SystemTab from './tabs/SystemTab.vue';
import TeamTab from './tabs/TeamTab.vue';
import UsersTab from './tabs/UsersTab.vue';

export default {
  components: {
    AchievementTab,
    BedriftsmeldingTab,
    ChangeLogTab,
    DashboardTab,
    EventsTab,
    MusicTab,
    NewsTab,
    SettingsTab,
    ShopTab,
    SystemTab,
    TeamTab,
    UsersTab,
  },
  props: {
    displayName: { type: String, default: '' },
    isOnlyProducer: { type: Boolean, default: false },
    activeTab: { type: String, default: 'dashboard' },
    searchQuery: { type: String, default: '' },
    upcomingEventsData: { type: Array, default: () => [] },
    newEvent: {
      type: Object,
      default: () => ({
        event_name: '',
        event_date: '',
        event_time: '',
        event_description: '',
        template_name: '',
        event_image: null,
        notify_users: false,
      }),
    },
    musicTracks: { type: Array, default: () => [] },
    musicMessage: { type: String, default: '' },
    musicSuccess: { type: Boolean, default: false },
    createEventMessage: { type: String, default: '' },
    createEventSuccess: { type: Boolean, default: false },
    userRoles: { type: Array, default: () => [] },
    usersList: { type: Array, default: () => [] },
    userRoleUpdate: { type: Object, default: () => ({ selectedUser: '', newRole: '' }) },
    availableRoles: { type: Array, default: () => [] },
    updateUserMessage: { type: String, default: '' },
    updateUserSuccess: { type: Boolean, default: false },
    selectedUserRoles: { type: Array, default: () => [] },
    userRoleRemove: { type: Object, default: () => ({ selectedUser: '' }) },
    selectedUserRolesToRemove: { type: Array, default: () => [] },
    rolesToRemove: { type: Array, default: () => [] },
    removeRoleMessage: { type: String, default: '' },
    removeRoleSuccess: { type: Boolean, default: false },
    newRole: { type: Object, default: () => ({ name: '', badge_icon: '', badge_color: '' }) },
    createRoleMessage: { type: String, default: '' },
    createRoleSuccess: { type: Boolean, default: false },
    teamMembers: { type: Array, default: () => [] },
    defaultAvatar: { type: String, default: '' },
    teamMessage: { type: String, default: '' },
    teamSuccess: { type: Boolean, default: false },
    maintenanceMode: { type: Boolean, default: false },
    noticeMaintenanceMode: { type: Boolean, default: false },
    maintenanceBannerMessage: { type: String, default: '' },
    maintenanceMessage: { type: String, default: '' },
    maintenanceSuccess: { type: Boolean, default: false },
    noticeMaintenanceMessage: { type: String, default: '' },
    noticeMaintenanceSuccess: { type: Boolean, default: false },
    newChangelog: { type: Object, default: () => ({ version: '', date: '', added: '', changed: '' }) },
    changelogEntries: { type: Array, default: () => [] },
    changelogMessage: { type: String, default: '' },
    changelogSuccess: { type: Boolean, default: false },
    widgets: { type: Array, default: () => [] },
    achievements: { type: Array, default: () => [] },
  },
  emits: [
    'addNewTeamMember',
    'addTrack',
    'createEvent',
    'createRole',
    'deleteChangelogEntry',
    'deleteEvent',
    'deleteRole',
    'deleteTeamMember',
    'deleteTrack',
    'fetchUserRolesToRemove',
    'handleImageUpload',
    'onToggleMaintenance',
    'onToggleNoticeMaintenance',
    'removeSelectedRoles',
    'reorderTracks',
    'saveTeamMember',
    'setFeatured',
    'submitChangelogEntry',
    'triggerAvatarUpload',
    'update:maintenanceBannerMessage',
    'update:maintenanceMode',
    'update:newChangelog',
    'update:newEvent',
    'update:newRole',
    'update:noticeMaintenanceMode',
    'update:rolesToRemove',
    'update:searchQuery',
    'update:teamMembers',
    'update:userRoleRemove',
    'update:userRoleUpdate',
    'updateUserRole',
  ],
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString();
    },
    formatTime(timeString) {
      return timeString;
    },
    updateNewEventField(field, value) {
      const updatedEvent = { ...this.newEvent, [field]: value };
      this.$emit('update:newEvent', updatedEvent);
    },
  },
};
</script>
