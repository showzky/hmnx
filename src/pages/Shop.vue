<template>
  <div class="shop-container">
    <header class="shop-header">
      <h1 class="shop-title">Fitte Points Shop</h1>
      <div class="points-balance">
        <span class="balance-label">Your Balance:</span>
        <span class="balance-amount">{{ fittePoints }} Fitte Points</span>
      </div>
    </header>

    <!-- Tabs for Badges & Themes -->
    <div class="shop-tabs">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'badge' }"
        @click="activeTab = 'badge'"
      >
        Badges
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'theme' }"
        @click="activeTab = 'theme'"
      >
        Themes
      </button>
    </div>

    <div class="shop-items">
      <div
        class="shop-item"
        v-for="item in filteredItems"
        :key="item.id"
      >
        <div class="item-icon-wrapper">
          <span class="item-icon">{{ item.icon }}</span>
        </div>
        <div class="item-content">
          <h3 class="item-name">{{ item.name }}</h3>
          <p class="item-description">{{ item.description }}</p>
          <div class="item-footer">
            <span class="item-price">{{ item.price }} FP</span>
            <button
              class="purchase-btn"
              :disabled="fittePoints < item.price"
              @click="purchaseItem(item)"
            >
              Buy
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios';

export default {
  name: 'Shop',
  setup() {
    const auth = useAuthStore();
    const fittePoints = ref(0);
    const activeTab = ref('badge');
    
    // Example items; fetch real data via API
    const items = ref([
      { id: 1, name: 'Golden Badge', description: 'Exclusive golden badge', price: 50, icon: '🥇', type: 'badge' },
      { id: 2, name: 'Silver Badge', description: 'Shiny silver badge', price: 30, icon: '🥈', type: 'badge' },
      { id: 3, name: 'Dark Theme', description: 'Sleek dark mode theme', price: 80, icon: '🌙', type: 'theme' },
      { id: 4, name: 'Neon Theme', description: 'Vibrant neon theme', price: 100, icon: '✨', type: 'theme' }
    ]);

    const filteredItems = computed(() =>
      items.value.filter(item => item.type === activeTab.value)
    );

    const loadBalance = async () => {
      try {
        // fetch from backend
        const res = await axios.get('/user/points');
        fittePoints.value = res.data.points;
      } catch {
        // fallback
        fittePoints.value = auth.user?.fittePoints || 0;
      }
    };

    const purchaseItem = async (item) => {
      // TODO: call API to purchase
      console.log('Purchasing:', item);
    };

    onMounted(loadBalance);

    return {
      fittePoints,
      activeTab,
      filteredItems,
      purchaseItem
    };
  }
};
</script>

<style scoped>
.shop-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.shop-title {
  font-size: 2rem;
  color: var(--text);
}
.points-balance {
  background: var(--card-bg);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.balance-label { color: var(--text); opacity: 0.8; }
.balance-amount { color: var(--primary); font-weight: 600; }

.shop-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: var(--card-bg);
  color: var(--text);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: background 0.3s;
}
.tab-btn.active {
  background: var(--primary);
  color: #fff;
}
.tab-btn:hover:not(.active) {
  background: rgba(255,255,255,0.05);
}

.shop-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}
.shop-item {
  background: var(--card-bg);
  border-radius: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}
.shop-item:hover {
  transform: translateY(-4px);
}

.item-icon-wrapper {
  background: rgba(255,255,255,0.05);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
}
.item-icon { font-size: 2.5rem; }

.item-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.item-name { font-size: 1.2rem; color: var(--text); }
.item-description { font-size: 0.9rem; opacity: 0.8; flex: 1; }

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}
.item-price { color: var(--primary); font-weight: 600; }
.purchase-btn {
  padding: 0.5rem 1rem;
  background: var(--secondary);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.3s;
}
.purchase-btn:hover:not(:disabled) {
  background: var(--accent);
}
.purchase-btn:disabled {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.5);
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .shop-header { flex-direction: column; gap: 1rem; }
  .shop-tabs { flex-direction: column; }
}
</style>
