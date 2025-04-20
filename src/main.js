import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/style.css/style.css';  // Import global styles
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import '@fortawesome/fontawesome-free/css/all.css';
import { createPinia } from 'pinia';

// Create the Vue app instance
const app = createApp(App);

// Create the Pinia store instance and register it with the app
const pinia = createPinia();
app.use(pinia);

// Register the router with the app
app.use(router);

// Mount the app to the DOM element with id "app"
app.mount('#app');
