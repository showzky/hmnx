import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/hmn-theme.css';          // HMN design system variables & utilities
import './assets/style.css/style.css';    // Legacy global styles
import './assets/badges.css'; // Import global badge styles
import 'swiper/swiper-bundle.css';
import '@fortawesome/fontawesome-free/css/all.css';
import { createPinia } from 'pinia';
import './components/admin/assets/admin.css';
import './assets/main.css'



// Log that Sortable is loaded
console.log('Sortable.js loaded successfully!');

// Create the Vue app instance
const app = createApp(App);

// Create the Pinia store instance and register it with the app
const pinia = createPinia();
app.use(pinia);

// Register the router with the app
app.use(router);

// Mount the app to the DOM element with id "app"
app.mount('#app');
