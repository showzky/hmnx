import { createRouter, createWebHistory } from 'vue-router';
import axios from '../axios'; // adjust if needed

// Import your pages
import Home from '@/pages/Home.vue';
import About from '@/pages/About.vue';
import Tjenester from '@/pages/Tjenester.vue';
import Bangerfabrikken from '@/pages/Bangerfabrikken.vue';
import Dashboard from '@/pages/Dashboard.vue';
import Login from '@/pages/Login.vue';
import Comments from '@/pages/Comments.vue';
import Forum from '@/pages/Forum.vue';
import Exclusive from '@/pages/exclusive.vue';
import NotFound from '@/pages/NotFound.vue';
import Management from '@/pages/Management.vue';
import EventDetailPage from '@/pages/EventDetailPage.vue';
import Settings from '@/components/Settings.vue';
import FriendsList from '@/views/FriendsList.vue'
//import UserProfile from '../pages/UserProfile.vue';
import PendingRequests from '../components/PendingRequests.vue';
import Shop from '@/pages/Shop.vue';
import Contact from '@/pages/Contact.vue'; 

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
  { path: '/tjenester', component: Tjenester },
  { path: '/bangerfabrikken', component: Bangerfabrikken },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/comments', name: 'Comments', component: Comments, meta: { requiresAuth: true } },
  { path: '/forum', name: 'Forum', component: Forum, meta: { requiresAuth: true } },
  { path: '/exclusive', name: 'Exclusive', component: Exclusive, meta: { requiresAuth: true } },
  { path: '/management', name: 'Management', component: Management, meta: { requiresAuth: true } },
  { path: '/pending-requests', name: 'PendingRequests', component: PendingRequests, meta: { requiresAuth: true } },
  { path: '/events/:eventId', name: 'EventDetail', component: EventDetailPage, props: true },
  { path: '/settings', component: Settings, meta: { requiresAuth: true } },
  { path: '/shop', name: 'Shop', component: Shop, meta: { requiresAuth: true } },
  {
    path: '/users/:userId',
    name: 'UserProfile',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
  {
    path: '/friends',
    name: 'Friends',
    component: FriendsList
  },
  {path: '/contact', name: 'Contact', component: Contact, meta: { requiresAuth: false } }, 
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from) => {
  // Handle Discord token via query param.
  if (to.query.token) {
    localStorage.setItem('access_token', to.query.token);
    return { path: to.path, query: {} };
  }

  const token = localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !token) {
    return { path: '/login' };
  }

  try {
    const res = await axios.get('/maintenance-status');
    const maintenanceOn = res.data.maintenance_mode === 'on';

    const userRaw = localStorage.getItem('user');
    const user = userRaw ? JSON.parse(userRaw) : null;
    const isAdmin = user && user.roles?.some(role =>
      ['admin', 'developer'].includes(role.name.toLowerCase())
    );

    if (maintenanceOn && !isAdmin && to.path !== '/maintenance') {
      // Full page redirect: do not try to use a named route here.
      window.location.href = '/maintenance';

      return false; // Cancel the navigation
    }

    // If maintenance is off but user tries to access /maintenance, redirect home.
    if (!maintenanceOn && to.path === '/maintenance') {
      return { path: '/' };
    }
  } catch (error) {
    console.error('Failed to check maintenance mode:', error);
    // Allow navigation if the maintenance check fails.
  }

  return true; // Proceed normally
});

export default router;
