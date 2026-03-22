<template>
  <aside class="admin-sidebar">
    <template v-if="!isOnlyProducer">
      <!-- CORE -->
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('core')">
          Core <span class="chevron" :class="{ open: open.core }">▾</span>
        </div>
        <div v-show="open.core" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='dashboard' }" @click.prevent="$emit('set-active', 'dashboard')">
            <span class="s-dot"></span>Dashboard
          </a>
          <a class="s-item" :class="{ active: activeTab==='system' }" @click.prevent="$emit('set-active', 'system')">
            <span class="s-dot"></span>System
          </a>
        </div>
      </div>
      <!-- CONTENT -->
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('content')">
          Content <span class="chevron" :class="{ open: open.content }">▾</span>
        </div>
        <div v-show="open.content" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='content' }" @click.prevent="$emit('set-active', 'content')">
            <span class="s-dot"></span>Events
          </a>
          <a class="s-item" :class="{ active: activeTab==='bedriftsmeldinger' }" @click.prevent="$emit('set-active', 'bedriftsmeldinger')">
            <span class="s-dot"></span>Bedriftsmeldinger
          </a>
          <a class="s-item" v-if="isAdminOrDeveloper" :class="{ active: activeTab==='news' }" @click.prevent="$emit('set-active', 'news')">
            <span class="s-dot"></span>News
          </a>
          <a class="s-item" :class="{ active: activeTab==='changelog' }" @click.prevent="$emit('set-active', 'changelog')">
            <span class="s-dot"></span>Changelog
          </a>
          <a class="s-item" :class="{ active: activeTab==='achievements' }" @click.prevent="$emit('set-active', 'achievements')">
            <span class="s-dot"></span>Achievements
          </a>
          <a class="s-item" :class="{ active: activeTab==='shop' }" @click.prevent="$emit('set-active', 'shop')">
            <span class="s-dot"></span>Shop Items
          </a>
        </div>
      </div>
      <!-- USERS -->
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('users')">
          Users <span class="chevron" :class="{ open: open.users }">▾</span>
        </div>
        <div v-show="open.users" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='users' }" @click.prevent="$emit('set-active', 'users')">
            <span class="s-dot"></span>User List
          </a>
          <a class="s-item" :class="{ active: activeTab==='team' }" @click.prevent="$emit('set-active', 'team')">
            <span class="s-dot"></span>Team Manager
          </a>
        </div>
      </div>
      <!-- EXTRAS -->
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('extras')">
          Extras <span class="chevron" :class="{ open: open.extras }">▾</span>
        </div>
        <div v-show="open.extras" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='music' }" @click.prevent="$emit('set-active', 'music')">
            <span class="s-dot"></span>Music
          </a>
          <a class="s-item" :class="{ active: activeTab==='settings' }" @click.prevent="$emit('set-active', 'settings')">
            <span class="s-dot"></span>Settings
          </a>
        </div>
      </div>
    </template>
    <template v-else>
      <!-- Producer-only view -->
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('core')">
          Core <span class="chevron" :class="{ open: open.core }">▾</span>
        </div>
        <div v-show="open.core" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='dashboard' }" @click.prevent="$emit('set-active', 'dashboard')">
            <span class="s-dot"></span>Dashboard
          </a>
        </div>
      </div>
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('content')">
          Content <span class="chevron" :class="{ open: open.content }">▾</span>
        </div>
        <div v-show="open.content" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='content' }" @click.prevent="$emit('set-active', 'content')">
            <span class="s-dot"></span>Events
          </a>
          <a class="s-item" :class="{ active: activeTab==='bedriftsmeldinger' }" @click.prevent="$emit('set-active', 'bedriftsmeldinger')">
            <span class="s-dot"></span>Bedriftsmeldinger
          </a>
        </div>
      </div>
      <div class="sidebar-group">
        <div class="sidebar-group-header" @click="toggleGroup('extras')">
          Extras <span class="chevron" :class="{ open: open.extras }">▾</span>
        </div>
        <div v-show="open.extras" class="sidebar-items">
          <a class="s-item" :class="{ active: activeTab==='music' }" @click.prevent="$emit('set-active', 'music')">
            <span class="s-dot"></span>Music
          </a>
        </div>
      </div>
    </template>
  </aside>
</template>

<script>
export default {
  props: ['activeTab', 'isOnlyProducer', 'isAdminOrDeveloper', 'open'],
  emits: ['toggle-group', 'set-active'],
  methods: {
    toggleGroup(group) {
      this.$emit('toggle-group', group);
    }
  }
};
</script>
