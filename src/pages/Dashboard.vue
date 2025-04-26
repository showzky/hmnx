<template>
  <div>
    <!-- Show dashboard once we have a userToShow (either you or a friend) -->
    <div v-if="userToShow" class="profile-container">
      
      <!-- HEADER / BANNER + AVATAR -->
      <header class="profile-header">
        <div class="banner" :style="{ backgroundImage: `url(${bannerToShow})` }">
          <!-- Only you can change your own banner -->
          <button
            v-if="isOwnProfile"
            class="change-banner-btn"
            @click="triggerBannerUpload"
          >
            Change Banner
          </button>
          <input
            v-if="isOwnProfile"
            type="file"
            ref="bannerInput"
            accept="image/*"
            @change="handleBannerImageChange"
            hidden
          />

          <div class="avatar-container">
            <!-- Only you can upload your own avatar -->
            <label
              v-if="isOwnProfile"
              for="avatar-upload"
              class="avatar-upload-label"
            >
              <div class="avatar">
                <img :src="avatarToShow" alt="Profile" />
                <div class="upload-overlay">
                  <i class="fas fa-camera"></i>
                  <span>Upload Picture</span>
                </div>
              </div>
            </label>
            <!-- If it's not your profile, show avatar without upload -->
            <div v-else class="avatar">
              <img :src="avatarToShow" alt="Profile" />
            </div>
            <input
              v-if="isOwnProfile"
              id="avatar-upload"
              type="file"
              accept="image/*"
              @change="handleProfilePicChange"
              hidden
            />
          </div>
        </div>

        <!-- PROFILE INFO (NAME, BADGES, BIO) -->
        <div class="profile-info">
          <div class="user-meta">
            <h1 class="username">{{ displayName }}</h1>
            <div class="badges-container">
              <div
                v-for="role in userToShow.roles"
                :key="role.id"
                class="role-badge"
                :class="role.name.toLowerCase()"
                :style="{ backgroundColor: role.badge_color || '#444' }"
              >
                <i v-if="role.badge_icon" :class="role.badge_icon"></i>
                <i
                  v-if="role.name.toLowerCase() === 'admin'"
                  class="icon-shield"
                ></i>
                <span>{{ role.name }}</span>
              </div>
            </div>
          </div>

          <!-- BIO SECTION -->
          <div class="bio-section">
            <div v-if="isOwnProfile && isEditingBio" class="edit-bio-group">
              <textarea
                v-model="newBio"
                placeholder="Write your bio..."
                maxlength="300"
              ></textarea>
              <p
                class="char-count"
                :class="{
                  'count-orange': remainingChars < 20 && remainingChars >= 0,
                  'count-red': remainingChars < 0,
                }"
              >
                {{ remainingChars }} characters left
              </p>
              <div class="button-group">
                <button
                  class="action-btn"
                  @click="updateBio"
                  :disabled="remainingChars < 0"
                >
                  Save
                </button>
                <button class="action-btn" @click="cancelEditBio">
                  Cancel
                </button>
              </div>
            </div>

            <div v-else class="bio-display-group">
              <p>{{ userToShow.bio || 'No bio set' }}</p>
              <button
                v-if="isOwnProfile"
                class="action-btn"
                @click="startEditBio"
              >
                Edit Bio
              </button>
            </div>
          </div>

          <!-- STATS GRID -->
          <div class="stats-grid">
            <!-- KRENKE THERMOMETER -->
            <div class="stat-card">
              <h3>Husket å føle deg krenket?</h3>
              <div class="thermometer-container">
                <div class="thermometer">
                  <div
                    class="mercury"
                    :style="{ height: krenkeLevel + '%' }"
                  ></div>
                  <div class="bulb"></div>
                  <div class="graduations">
                    <div class="graduation" data-temp="100" style="top: 0%;"></div>
                    <div class="graduation" data-temp="0" style="top: 100%;"></div>
                  </div>
                </div>
              </div>
              <div class="stat">{{ krenkeLevel }}% • krenket</div>
            </div>

            <!-- FITTE POINTS -->
            <div class="stat-card fitte-points">
              <h3>Fitte Points</h3>
              <div class="stat">
                <span class="fitte-number">{{ fittePoints }}</span>
                <svg class="fitte-icon" width="70" height="50" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="20" cy="20" r="20" fill="#ff61c2"/>
                  <path d="M10 20C10 25 15 30 20 30C25 30 30 25 30 20C30 15 25 10 20 10C15 10 10 15 10 20Z" fill="#ff61c2"/>
                  <path d="M15 20C15 22 17 24 20 24C23 24 25 22 25 20C25 18 23 16 20 16C17 16 15 18 15 20Z" fill="#fff"/>
                </svg>
              </div>
            </div>

            <!-- LAB ACTIVITY -->
            <div class="stat-card">
              <h3>Lab Activity</h3>
              <div class="stat">{{ labActivity }}h This Week</div>
            </div>
          </div>
        </div>
      </header>

      <!-- NAV BAR -->
      <nav class="profile-nav">
        <div
          class="nav-item"
          :class="{ active: activeNav === 'experiments' }"
          @click="activeNav = 'experiments'"
        >
          Experiments
        </div>
        <div
          class="nav-item"
          :class="{ active: $route.path === '/friends' }"
          @click="$router.push({ name: 'Friends' })"
        >
          Venner
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'achievements' }"
          @click="activeNav = 'achievements'"
        >
          Achievements
        </div>
        <div
          class="nav-item"
          :class="{ active: $route.path === '/shop' }"
          @click="$router.push({ name: 'Shop' })"
        >
          🛒 Shop
        </div>
      </nav>

      <!-- MAIN CONTENT -->
      <div class="content-grid">
        <!-- ACTIVITY FEED -->
        <div class="activity-feed">
          <h2>Recent Madness</h2>
          <FriendsList v-if="activeNav === 'friends'" ref="friendsList" />
          <div v-if="activeNav === 'shop'" class="shop-section">
            <h2>Shop</h2>
            <div class="shop-items">
              <div class="shop-item">
                <div class="item-icon">🎮</div>
                <div class="item-details">
                  <h3>Gaming Session</h3>
                  <p>2 hours of uninterrupted gaming</p>
                  <div class="item-price">50 Fitte Points</div>
                </div>
              </div>
              <div class="shop-item">
                <div class="item-icon">🎵</div>
                <div class="item-details">
                  <h3>Music Request</h3>
                  <p>Request your favorite song</p>
                  <div class="item-price">30 Fitte Points</div>
                </div>
              </div>
              <div class="shop-item">
                <div class="item-icon">🎨</div>
                <div class="item-details">
                  <h3>Custom Avatar</h3>
                  <p>Get a custom avatar made</p>
                  <div class="item-price">100 Fitte Points</div>
                </div>
              </div>
            </div>
          </div>
          <div
            class="activity-item"
            v-for="(activity, idx) in activityFeed"
            :key="idx"
          >
            <i :class="activity.icon"></i>
            <div>
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
              <small>{{ activity.time }}</small>
            </div>
          </div>
        </div>

        <!-- QUICK ACTIONS (only on your own profile) -->
        <div v-if="isOwnProfile" class="quick-actions">
          <button class="action-btn krenke-knapp" @click="adjustKrenkeLevel">
            <i class="fas fa-hand-sparkles"></i>
            <span>Husket å føle deg krenket?</span>
          </button>
          <button class="action-btn" @click="goToSettings">
            <i class="fas fa-brain"></i>
            <span>Settings</span>
          </button>
          <button class="action-btn" @click="action('overdrive')">
            <i class="fas fa-radiation"></i>
            <span>Overdrive Mode</span>
          </button>
          <AdminButton />
        </div>
      </div>

      <!-- SNACKBAR -->
      <SnackBar
        ref="snackBar"
        :message="snackBarMessage"
        :type="snackBarType"
        :duration="3000"
      />
    </div>

    <!-- LOADING STATE -->
    <div v-else class="loading">
      <p>Loading dashboard…</p>
    </div>
  </div>
</template>




<script>
import FriendsList from '@/views/FriendsList.vue';
import { ref, computed, onBeforeUnmount, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useWebSocket } from '@/composables/useWebSocket';
import SnackBar from '@/components/SnackBar.vue';
import { fetchUsers } from '@/services/userService'
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios';
import AdminButton from '@/components/AdminButton.vue';

export default {
  name: 'NeuroLabProfile',
  components: {
    SnackBar,
    FriendsList,
    AdminButton
  },
  setup() {
    const auth = useAuthStore();
    const fittePoints = computed(() => auth.fittePoints);
    const { socket } = useWebSocket();
    const router = useRouter();
    const route = useRoute();

    const friendsList = ref(null);
    const profileUser = ref(null);

    const isOwnProfile = computed(() => {
      if (!route.params.userId) return true;
      return +route.params.userId === auth.user?.id;
    });
    
    const userToShow = computed(() => {
      return isOwnProfile.value ? auth.user : profileUser.value;
    });

    const displayName = computed(() =>
      userToShow.value?.username || userToShow.value?.email || 'Dr. Neuroflux'
    );

    const defaultAvatar = 'https://picsum.photos/400/400';
    const defaultBanner = 'https://picsum.photos/1200/280';

    const bannerImage = ref(auth.user?.banner);
    const bannerToShow = computed(() =>
      isOwnProfile.value
        ? bannerImage.value
        : userToShow.value?.banner || defaultBanner
    );

    const avatarToShow = computed(() =>
      userToShow.value?.avatar || defaultAvatar
    );

    onMounted(async () => {
  /* If you're viewing somebody else's profile … */
  if (!isOwnProfile.value) {
    try {
      /* 1️⃣ quick "list" request — has avatar & banner */
      const listRes = await fetchUsers()
      profileUser.value = listRes.data.users.find(
        u => u.id === +route.params.userId
      )

      /* 2️⃣ full "/users/:id" request — bio, roles, etc. */
      const fullRes = await axios.get(
        `${import.meta.env.VITE_API_URL}/users/${route.params.userId}`
      )

      /* merge: keep avatar/banner from step 1, add the rest from step 2 */
      profileUser.value = {
        ...profileUser.value,   // avatar & banner stay
        ...fullRes.data.user    // bio, roles, anything else
      }
    } catch (err) {
      console.warn('Failed to load full user profile:', err)
    }
  }
      if (socket.value) {
        socket.value.on('roleUpdate', (newRoleData) => {
          const receivedUserId = parseInt(newRoleData.userId, 10);
          if (auth.user?.id === receivedUserId) {
            auth.$patch({
              user: { ...auth.user, roles: [...newRoleData.roles] }
            });
          }
        });

        if (auth.user?.id) {
          socket.value.emit('setUserId', auth.user.id);
        }
      }

      // Daily reset of krenke state
      const today = new Date().toDateString();
      const lastReset = localStorage.getItem('krenkeResetDate');
      if (lastReset !== today) {
        krenkeFilled.value = false;
        localStorage.setItem('krenkeFilled', 'false');
        localStorage.setItem('krenkeResetDate', today);
      } else {
        krenkeFilled.value = localStorage.getItem('krenkeFilled') === 'true';
      }

      getKrenkeLevelFromBackend();
      await auth.fetchFittePoints();

      fetchWeeklyActivity();
      trackDashboardVisit();

      canvas = document.getElementById('fluid-canvas');
      if (canvas) {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        context = canvas.getContext('2d');
        updateFluidFill(krenkeLevel.value);
      }
    });

    const activeNav = ref('experiments');
    const userLevel = ref(42);
    const krenkeLevel = ref(2);
    




    const krenkeFilled = ref(false);
    const neuroConnections = ref('2.4K');
    const labActivity = ref(0);
    const rolesString = computed(() =>
      auth.user?.roles?.map(r => r.name).join(', ') || 'No roles'
    );

    const userRoles = computed(() => auth.user?.roles || []);
    const isRegular = computed(() =>
      userRoles.value.some(r => r.name.toLowerCase() === 'regular')
    );
    const isDeveloper = computed(() =>
      userRoles.value.some(r => r.name.toLowerCase() === 'developer')
    );
    const isProducer = computed(() =>
      userRoles.value.some(r => r.name.toLowerCase() === 'producer')
    );

    const drainInterval = setInterval(() => {
      if (krenkeLevel.value > 0){ 
        krenkeLevel.value = Math.max(0, krenkeLevel.value -15); // Change later ( only for testing)
        updateKrenkeLevelOnBackend();
      }
    }, 10000); // 30 seconds interval for draining krenke level 

    onBeforeUnmount(() => clearInterval(drainInterval));

    async function fetchWeeklyActivity() {
      try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/get-weekly-activity', {
          headers: { Authorization: `Bearer ${token}` },
        });
        labActivity.value = res.data.weekly_visits;
      } catch (err) {
        console.error('Error fetching activity:', err);
      }
    }

    async function trackDashboardVisit() {
      try {
        const token = localStorage.getItem('access_token');
        await axios.post(
          `${import.meta.env.VITE_API_URL}/track-dashboard-visit`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (err) {
        console.error('Tracking visit failed:', err);
      }
    }

    let canvas, context;

    function updateFluidFill(percentage) {
      if (!canvas || !context) return;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.save();
      context.beginPath();
      context.rect(0, 0, canvas.width, canvas.height);
      context.clip();

      const fluidHeight = canvas.height * (percentage / 100);
      const gradient = context.createLinearGradient(
        0, canvas.height - fluidHeight, 0, canvas.height
      );
      gradient.addColorStop(0, '#f17a65');
      gradient.addColorStop(1, '#3dcadf');
      context.fillStyle = gradient;
      context.fillRect(0, canvas.height - fluidHeight, canvas.width, fluidHeight);
      context.restore();
    }

    watch(krenkeLevel, updateFluidFill);

    async function adjustKrenkeLevel() {
      await getKrenkeLevelFromBackend();
      const current = krenkeLevel.value;
      if (current < 80 && !krenkeFilled.value) {
        krenkeLevel.value = 100;
        auth.fittePoints += 10;
        krenkeFilled.value = true;
        await updateKrenkeLevelOnBackend();
        await auth.updateFittePoints(auth.fittePoints);  // Optional chaining if needed
        showSnack('+10 Fitte Points! You have successfully krenket.', 'success');
      } else {
        showSnack('Krenke level too high or already filled — no points awarded!', 'info');
      }
    }

    async function getKrenkeLevelFromBackend() {
      try {
        const token = localStorage.getItem('access_token');
        const res = await axios.get('/get-krenke-level', {
          headers: { Authorization: `Bearer ${token}` }
        });
        krenkeLevel.value = res.data.level;
      } catch (err) {
        console.error('Could not fetch krenke level:', err);
      }
    }

    async function updateKrenkeLevelOnBackend() {
      try {
        const token = localStorage.getItem('access_token');
        await axios.post('/update-krenke-level', {
          level: krenkeLevel.value
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (err) {
        console.error('Could not update krenke level:', err);
      }
    }

    const bannerInput = ref(null);
    const isUploadingBanner = ref(false);
    const isUploadingAvatar = ref(false);

    function triggerBannerUpload() {
      bannerInput.value.click();
    }

    async function handleBannerImageChange(event) {
      const file = event.target.files[0];
      if (!file?.type.startsWith('image/')) {
        showSnack('Please select an image file', 'error');
        return;
      }

      const formData = new FormData();
      formData.append('banner', file);

      try {
        isUploadingBanner.value = true;
        const token = localStorage.getItem('access_token');
        const res = await axios.post('/upload-banner', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          }
        });
        const newUrl = res.data.url;
        bannerImage.value = newUrl;
        auth.$patch({ user: { ...auth.user, banner: newUrl } });
        localStorage.setItem('user', JSON.stringify(auth.user));
        showSnack('Banner updated successfully!', 'success');
      } catch (err) {
        console.error('Upload failed:', err);
        showSnack(err.response?.data?.msg || 'Failed to upload banner', 'error');
      } finally {
        isUploadingBanner.value = false;
      }
    }

    async function handleProfilePicChange(event) {
      const file = event.target.files[0];
      if (!file?.type.startsWith('image/')) return;

      const formData = new FormData();
      formData.append('avatar', file);

      try {
        isUploadingAvatar.value = true;
        const token = localStorage.getItem('access_token');
        const res = await axios.post('/upload-avatar', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          }
        });
        const url = res.data.url;
        auth.$patch({ user: { ...auth.user, avatar: url } });
        localStorage.setItem('user', JSON.stringify(auth.user));
      } catch (err) {
        console.error('Avatar upload failed:', err);
      } finally {
        isUploadingAvatar.value = false;
      }
    }

    const snackBar = ref(null);
    const snackBarMessage = ref('');
    const snackBarType = ref('success');

    function showSnack(msg, type = 'success') {
      snackBarMessage.value = msg;
      snackBarType.value = type;
      snackBar.value?.showSnackBar();
    }

    const isEditingBio = ref(false);
    const newBio = ref(auth.user?.bio || '');
    const remainingChars = computed(() => 300 - newBio.value.length);

    function startEditBio() {
      isEditingBio.value = true;
      newBio.value = auth.user?.bio || '';
    }

    async function updateBio() {
      if (remainingChars.value < 0) return;
      try {
        const token = localStorage.getItem('access_token');
        const res = await axios.post('/update-profile', { bio: newBio.value }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        auth.$patch({ user: { ...auth.user, bio: res.data.user.bio } });
        localStorage.setItem('user', JSON.stringify(auth.user));
        isEditingBio.value = false;
        showSnack('Bio updated successfully!');
      } catch (err) {
        showSnack(err.response?.data?.msg || 'Error updating bio', 'error');
      }
    }

    function cancelEditBio() {
      isEditingBio.value = false;
      newBio.value = auth.user?.bio || '';
    }

    function action(type) {
      console.log(`Action: ${type}`);
    }

    function goToSettings() {
      router.push('/settings');
    }

    return {
      auth,
      defaultAvatar,
      bannerImage,
      bannerInput,
      triggerBannerUpload,
      activeNav,
      userLevel,
      krenkeLevel,
      isOwnProfile,
      userToShow,
      neuroConnections,
      labActivity,
      activityFeed: ref([]),
      displayName,
      isDeveloper,
      isProducer,
      isRegular,
      isEditingBio,
      newBio,
      remainingChars,
      friendsList,
      startEditBio,
      updateBio,
      cancelEditBio,
      action,
      handleProfilePicChange,
      handleBannerImageChange,
      snackBar,
      snackBarMessage,
      snackBarType,
      showSnack,
      adjustKrenkeLevel,
      getKrenkeLevelFromBackend,
      updateKrenkeLevelOnBackend,
      fittePoints,
      isUploadingBanner,
      isUploadingAvatar,
      rolesString,
      goToSettings,
      bannerToShow,
      avatarToShow,
      AdminButton
    };
  }
};
</script>







<style scoped>
:root {
  --primary: #7b2cbf;
  --secondary: #3a86ff;
  --accent: #ff006e;
  --background: #0f0e17;
  --text: #fffffe;
  --card-bg: #16151d;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background: var(--background);
  color: var(--text);
  font-family: 'Inter', system-ui;
  line-height: 1.6;
}

.profile-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
  width: 100%;
}

/* Add responsive styles */
@media (max-width: 768px) {
  .profile-container {
    margin: 1rem auto;
    padding: 0 0.5rem;
  }

  .banner {
    height: 200px;
  }

  .avatar {
    width: 120px;
    height: 120px;
  }

  .avatar-container {
    bottom: -60px;
    left: 1rem;
  }

  .profile-info {
    padding: 4rem 1rem 1rem;
  }

  .username {
    font-size: 2rem;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .profile-nav {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .nav-item {
    padding: 0.5rem;
    font-size: 0.9rem;
  }

  .role-badge {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
  }

  .thermometer {
    width: 25px;
    height: 120px;
  }

  .fitte-points {
    padding: 1rem;
  }

  .fitte-points h3 {
    font-size: 1.2rem;
  }

  .fitte-points .stat {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .banner {
    height: 160px;
  }

  .avatar {
    width: 100px;
    height: 100px;
  }

  .avatar-container {
    bottom: -50px;
  }

  .username {
    font-size: 1.5rem;
  }

  .profile-info {
    padding: 3.5rem 0.5rem 0.5rem;
  }

  .stats-grid {
    gap: 1rem;
  }

  .stat-card {
    padding: 1rem;
  }

  .thermometer {
    width: 20px;
    height: 100px;
  }
}

/* Profile Header */
.profile-header {
  position: relative;
  border-radius: 1.5rem;
  overflow: hidden;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  margin-bottom: 2rem;
}

.banner {
  height: 280px;
  background: rgba(0, 0, 0, 0.4);
  position: relative;
  background-size: cover;
  background-position: center;
}
.badges-container {
  display: flex;
  gap: 0.5rem;      /* space between badges */
  flex-wrap: wrap;  /* wrap to next line if there's not enough room */
  margin-top: 0.5rem;
}

/* NEW single-badge style */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  /* No fallback background here if you want CSS to handle it when badge_color isn't set */
  color: #fff;
  font-weight: 500;
  transition: background-color 0.3s ease;
}
.fitte-points {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.fitte-points h3 {
  color: #ccc8cb;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.fitte-points .stat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 3.5rem;
  font-weight: bold;
  color: #ffffff;
  transition: transform 0.3s ease;
  line-height: 1;
}

.fitte-points .fitte-icon {
  width: 70px;
  height: 50px;
  animation: pulse 2s infinite;
}

/* Fitte Points " number"  styles*/
.fitte-points .fitte-number {
  font-size: 3.5rem;
  color: #ff61c2;
  font-weight: bold;
  line-height: 1;
}

/* Change Banner Button Styles */
.change-banner-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.5rem 1rem;
  background-color: var(--accent);
  color: var(--text);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  z-index: 20;
  transition: background-color 0.3s ease;
}
.change-banner-btn:hover {
  background-color: #ff3e80;
}

.avatar-container {
  position: absolute;
  bottom: -80px;
  left: 2rem;
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
}

.avatar-upload-label {
  cursor: pointer;
  display: block;
  position: relative;
  z-index: 10;
}

.avatar {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 4px solid var(--background);
  background: var(--card-bg);
  overflow: hidden;
  position: relative;
  transition: transform 0.3s ease;
}
.avatar:hover {
  transform: scale(1.05);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Profile Info */
.profile-info {
  padding: 6rem 2rem 2rem;
  backdrop-filter: blur(20px);
}
.user-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.username {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}
role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #444; /* Fallback background */
  color: #fff;
  font-weight: 500;
  font-size: 14px;
  cursor: default;
  transition: background-color 0.3s ease;
}

/* Developer-specific styling */
.role-badge.developer {
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 14px; /* Matching admin badge size */
  font-weight: 700;
  padding: 8px 12px;
  border-radius: 20px;
  background: linear-gradient(135deg, #2b6cb0, #4299e1);
  border: 2px solid rgba(255, 255, 255, 0.15);
  color: #ebf8ff;
  text-shadow: 0 1px 2px rgba(32, 78, 207, 0.4);
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3),
              0 4px 16px rgba(66, 153, 225, 0.2);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  line-height: 1;
  transition: transform 0.2s ease;
}

/* Icon using Font Awesome (make sure to include FA in your project) */
.role-badge.developer::before {
  content: "\f121";
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  font-size: 1em;
  display: inline-block;
}

/* Subtle animated background effect */
.role-badge.developer::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, 
    transparent 25%,
    rgba(255,255,255,0.1) 50%,
    transparent 75%);
  animation: shine 4s infinite;
}

/* ===================== FIXED FITTE POINTS STYLES ===================== */
.fitte-points {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.fitte-points h3 {
  color: #ccc8cb;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.fitte-points .stat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 3.5rem;
  font-weight: bold;
  color: #ffffff;
  transition: transform 0.3s ease;
  line-height: 1;
}

.fitte-points .fitte-icon {
  width: 70px;
  height: 50px;
  animation: pulse 2s infinite;
}

/* Fitte Points " number"  styles*/
.fitte-points .fitte-number {
  font-size: 3.5rem;
  color: #ff61c2;
  font-weight: bold;
  line-height: 1;
}

/* Admin-specific styling (using your glowing badge as a reference) */
.role-badge.admin {
  /* These values are taken from your glowing admin badge */
  font-family: 'Arial', sans-serif;
  font-size: 14px; 
  font-weight: bold;
  text-transform: uppercase;
  padding: 8px 12px; 
  border-radius: 20px; 
  background: linear-gradient(135deg, #d90429, #ff2e63);
  border: 2px solid rgba(255, 255, 255, 0.2);
  text-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.6), 0 0 40px rgba(255, 46, 99, 0.6);
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  gap: 6px; /* Reduced from 10px */
  line-height: 1; /* Ensures text doesn't create extra height */
}

/* Shield icon for admin badge using CSS mask */
.icon-shield {
  display: inline-block;
  width: 20px;
  height: 20px;
  background: white;
  -webkit-mask: url('https://img.icons8.com/ios-filled/50/ffffff/shield.png') no-repeat center;
  mask: url('https://img.icons8.com/ios-filled/50/ffffff/shield.png') no-repeat center;
  -webkit-mask-size: contain;
  mask-size: contain;
  opacity: 0.9;
}

/* Optional: Animated shine effect for the admin badge */
.role-badge.admin::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 200%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.2) 20%, transparent 80%);
  transform: skewX(-20deg);
  animation: shine 3s infinite linear;
}

@keyframes shine {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Member Badge */
.role-badge.member {
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, #4a5568, #718096);
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  color: #f7fafc;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin: 10px;
}

.role-badge.member::before {
  content: "\f007";
  font-family: "Font Awesome 5 Free";
  font-weight: 400;
  font-size: 0.9em;
}

/* Shared Styles */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  line-height: 1;
  position: relative;
  overflow: hidden;
}

/* Container for preview */
.badge-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #1a202c;
  flex-wrap: wrap;
}

/* Shine animation for developer badge */
@keyframes shine {
  0% { transform: translateX(-50%) rotate(45deg); }
  100% { transform: translateX(150%) rotate(45deg); }
}

/* Badges container (if you need some extra spacing) */
.badges-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
/* Bio Section */
.bio-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 1rem;
}
.bio-section p {
  font-size: 1rem;
  margin-bottom: 1rem;
}
.edit-bio-group textarea {
  width: 100%;
  padding: 0.8rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--background);
  color: var(--text);
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  margin-bottom: 0.5rem;
}
.char-count {
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.count-orange {
  color: orange;
}
.count-red {
  color: red;
}
.button-group {
  display: flex;
  gap: 1rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}
.stat-card {
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.stat-card h3 {
  color: var(--accent);
  margin-bottom: 0.5rem;
}
.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}
.stat {
  font-size: 0.9rem;
}

/* Navigation */
.profile-nav {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.nav-item {
  padding: 1rem;
  cursor: pointer;
  position: relative;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}
.nav-item.active {
  opacity: 1;
  font-weight: 500;
}
.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent);
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 2rem;
}
.activity-feed {
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: 1rem;
}
.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  margin-bottom: 1rem;
}
.quick-actions {
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: 1rem;
  height: fit-content;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 0.75rem;
  color: var(--text);
  cursor: pointer;
  transition: background 0.3s ease;
}
.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Optional: Style the hidden file input */
input[type="file"] {
  display: none;
}

.thermometer-container {
  display: flex;
  justify-content: center;
  margin: 15px 0;
}

.thermometer {
  position: relative;
  width: 30px;
  height: 150px;
  background: #f0f0f0;
  border-radius: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 25px;
}

.mercury {
  position: absolute;
  bottom: 0;
  left: 5px;
  width: 20px;
  height: 60%; /* This will be overridden by the :style binding */
  background: linear-gradient(to top, #ff0000, #ff3300);
  border-radius: 10px 10px 0 0;
  transition: height 0.5s ease;
}

.bulb {
  position: absolute;
  bottom: -15px;
  left: 0;
  width: 30px;
  height: 30px;
  background: #ff0000;
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}

.graduations {
  position: absolute;
  left: 35px;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.graduation {
  position: relative;
  height: 1px;
  width: 15px;
  background: #333;
}

.graduation::after {
  content: attr(data-temp);
  position: absolute;
  left: 20px;
  top: -8px;
  font-size: 12px;
  color: #333;
}

.stat-card .stat {
  text-align: center;
  font-size: 1rem;
  color: #ff3300;
  font-weight: bold;
}

.snackbar.success {
  background-color: #28a745;
}

.snackbar.info {
  background-color: #fd7e14;
}

.snackbar.error {
  background-color: #dc3545;
}

/* Shop Section Styles */
.shop-section {
  padding: 1.5rem;
  background: var(--card-bg);
  border-radius: 1rem;
  margin-top: 1rem;
}

.shop-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.shop-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.shop-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.item-icon {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.1);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  color: var(--text);
}

.item-details p {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 0.5rem;
}

.item-price {
  color: #00ff88;
  font-weight: 600;
  font-size: 1.1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .shop-items {
    grid-template-columns: 1fr;
  }
  
  .shop-item {
    padding: 1rem;
  }
  
  .item-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
}
</style>