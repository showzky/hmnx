// src/stores/authStore.js
import { defineStore } from 'pinia';
import axios from '@/axios';

export const useAuthStore = defineStore('auth', {
  // State: authentication status, user info, and token
  state: () => ({
    isAuthenticated: !!localStorage.getItem('access_token'),
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
    token: localStorage.getItem('access_token') || null,
    fittePoints: 0,
  }),
  actions: {
    async fetchFittePoints() {
      try {
        // Hit your existing endpoint
        const res = await axios.get('/get-fitte-points', {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        // Update the store
        this.fittePoints = res.data.points;

      } catch (err) {
        console.error('Could not load Fitte Points:', err);
      }
    },
    async updateFittePoints(points) {
      try {
        const res = await axios.post('/update-fitte-points', { points }, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        this.fittePoints = res.data.points;  // Keep the store updated
      } catch (err) {
        console.error('Error updating Fitte Points:', err);
      }
    },
    
    // Call this after a successful login API call
    login(user, token) {
      this.user = user;
      this.token = token;
      this.isAuthenticated = true;
      localStorage.setItem('access_token', token);
      localStorage.setItem('user', JSON.stringify(user));
    },
    // Log out the user and clear stored authentication data
    logout() {
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    },
    // (Optional) Initialize from localStorage on page refresh
    initialize() {
      const token = localStorage.getItem('access_token');
      const user = localStorage.getItem('user');
      if (token && user) {
        this.token = token;
        this.user = JSON.parse(user);
        this.isAuthenticated = true;
      }
    },
  },
});
