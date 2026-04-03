<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import HmnDriftsmelding from './components/HmnDriftsmelding.vue';
import HmnNav from './components/HmnNav.vue';
import HmnFooter from './components/HmnFooter.vue';
import HmnLoginModal from './components/HmnLoginModal.vue';
import HmnRegisterModal from './components/HmnRegisterModal.vue';
import HmnToast from './components/HmnToast.vue';

const showLogin    = ref(false);
const showRegister = ref(false);
const toast        = ref(null);

function toggleLoginModal() {
  showLogin.value = !showLogin.value;
  if (showLogin.value) showRegister.value = false;
}

function switchToRegister() {
  showLogin.value = false;
  showRegister.value = true;
}

function switchToLogin() {
  showRegister.value = false;
  showLogin.value = true;
}

const route = useRoute()
const hideLayoutRoutes = ['/tos', '/management']
const showLayout = computed(() => !hideLayoutRoutes.includes(route.path))
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
</script>

<template>
  <div id="app">
    <HmnDriftsmelding v-if="showLayout" />
    <HmnNav v-if="showLayout" @toggle-login="toggleLoginModal" @toggle-register="() => { showRegister = true; showLogin = false; }" />

    <router-view />

    <HmnFooter v-if="showLayout" />

    <HmnLoginModal
      :show="showLogin && !isAuthPage"
      @close="showLogin = false"
      @switch-register="switchToRegister"
    />
    <HmnRegisterModal
      :show="showRegister && !isAuthPage"
      @close="showRegister = false"
      @switch-login="switchToLogin"
    />
    <HmnToast ref="toast" />
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

footer {
  margin-top: auto;
}
</style>
