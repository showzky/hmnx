<script setup>
import { ref } from 'vue';
import Navbar from './components/NavBar.vue';
import Footer from './components/Footer.vue';
import LoginModal from './components/LoginModal.vue';
import MaintenanceBanner from './components/MaintenanceBanner.vue';

// Reactive flag to control the visibility of the login modal
const showLogin = ref(false);

// Function to toggle the login modal visibility
function toggleLoginModal() {
  showLogin.value = !showLogin.value;
}
</script>

<template>
  <div id="app">
    <!-- Navbar emits "toggle-login" event to toggle the modal -->
    <Navbar @toggle-login="toggleLoginModal" />
    <MaintenanceBanner />
    
    <!-- Main Content rendered by Vue Router -->
    <router-view />

    <!-- Footer -->
    <Footer />

    <!-- Conditionally render the LoginModal -->
    <LoginModal v-if="showLogin" @hide-login="toggleLoginModal" />
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

footer {
  margin-top: auto;
}
</style>
