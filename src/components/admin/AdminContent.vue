<template>
  <main class="admin-content">
    <div class="content-area">

      <!-- CHANGED THIS - Tabs accessible to both admin/developer AND producer -->
      <DashboardTab
        v-if="activeTab === 'dashboard'"
        :displayName="displayName"
        :totalUsers="usersList.length"
        :upcomingEventsData="upcomingEventsData"
        :widgets="widgets"
      />

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

      <BedriftsmeldingTab v-if="activeTab === 'bedriftsmeldinger'" />

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

      <!-- Admin/Developer-only tabs -->
      <template v-if="!isOnlyProducer">

        <SystemTab v-if="activeTab === 'system'" />

        <ShopTab v-if="activeTab === 'shop'" />

        <NewsTab v-if="activeTab === 'news'" />

        <UsersTab
          v-if="activeTab === 'users'"
          :userRoles="userRoles"
          :userPermissions="userPermissions"
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
    userPermissions: { type: Array, default: () => [] },
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
