<template>
  <div class="shop-container">
    <!-- Best Practice: Use semantic HTML for accessibility -->
    <header class="shop-header">
      <h1 class="shop-title">Fitte Points Shop</h1>
      <div class="points-balance" aria-live="polite">
        <span class="balance-label">Your Balance:</span>
        <span class="balance-amount">{{ fittePoints }} FP</span>
      </div>
    </header>

    <!-- Tabs for Badges & Themes -->
    <nav class="shop-tabs" role="tablist">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'badge' }"
        @click="activeTab = 'badge'"
        role="tab"
        :aria-selected="activeTab === 'badge'"
      >
        Badges
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'theme' }"
        @click="activeTab = 'theme'"
        role="tab"
        :aria-selected="activeTab === 'theme'"
      >
        Themes
      </button>
    </nav>

    <section class="shop-items" aria-label="Shop Items">
      <article
        class="shop-item"
        v-for="item in filteredItems"
        :key="item.id"
      >
        <div class="item-icon-wrapper">
          <span class="item-icon" :aria-label="item.name + ' icon'" role="img">{{ item.icon }}</span>
        </div>
        <div class="item-content">
          <h2 class="item-name">{{ item.name }}</h2>
          <p class="item-description">{{ item.description }}</p>
          <!-- Best Practice: Separate concerns with clear action handlers -->
          <div class="item-footer">
            <span class="item-price">{{ item.price }} FP</span>
            <button
              class="purchase-btn"
              :disabled="fittePoints < item.price"
              @click="purchaseItem(item)"
              :aria-disabled="fittePoints < item.price"
            >
              Buy
            </button>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'Shop',
  setup() {
    const auth = useAuthStore();
    const activeTab = ref('badge');

    const items = ref([
      // Dummy items for shop display
      { id: 1, name: 'Golden Badge', description: 'Exclusive golden badge', price: 50, icon: '🥇', type: 'badge' },
      { id: 2, name: 'Silver Badge', description: 'Shiny silver badge', price: 30, icon: '🥈', type: 'badge' },
      { id: 3, name: 'Bronze Badge', description: 'Classic bronze badge', price: 20, icon: '🥉', type: 'badge' },
      { id: 4, name: 'Dark Theme', description: 'Sleek dark mode theme', price: 80, icon: '🌙', type: 'theme' },
      { id: 5, name: 'Neon Theme', description: 'Vibrant neon theme', price: 100, icon: '✨', type: 'theme' }
    ]);

    const filteredItems = computed(() =>
      items.value.filter(item => item.type === activeTab.value)
    );

    const fittePoints = ref(0);

    onMounted(async () => {
      try {
        const { data } = await axios.get('/get-fitte-points')
        fittePoints.value = data.points
      } catch (e) {
        console.error(e)
      }
    });

    const purchaseItem = async (item) => {
      try {
        console.log('Purchasing:', item);
        // TODO: Integrate purchase API and update store
        // await auth.fetchFittePoints();
      } catch (error) {
        console.error('Purchase failed', error);
      }
    };

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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Roboto:wght@400;700&display=swap');

.shop-container {
  --primary: #ff4081;
  --secondary: #536dfe;
  --accent: #ff9100;
  --bg-color: #1e1e2f;
  --card-bg: #29293d;
  --text: #f5f5f5;
  font-family: 'Press Start 2P', sans-serif;
  background: var(--bg-color);
  color: var(--text);
  max-width: 1000px;
  margin: 2rem auto;
  padding: 1rem;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--secondary);
}

.shop-title {
  font-size: 2.5rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--primary);
}

.points-balance {
  background: var(--card-bg);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Roboto', sans-serif;
}

.balance-label {
  opacity: 0.8;
  font-size: 0.9rem;
}

.balance-amount {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--accent);
}

.shop-tabs {
  display: flex;
  gap: 1rem;
  margin: 1.5rem 0;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  background: var(--card-bg);
  border: 2px solid transparent;
  border-radius: 0.75rem;
  cursor: pointer;
  font-family: 'Roboto', sans-serif;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: var(--primary);
  border-color: var(--accent);
  color: #fff;
}

.tab-btn:hover:not(.active) {
  background: rgba(255,255,255,0.1);
}

.shop-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.shop-item {
  background: var(--card-bg);
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.shop-item:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

.item-icon-wrapper {
  background: rgba(255,255,255,0.05);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
}

.item-icon {
  font-size: 3rem;
}

.item-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-family: 'Roboto', sans-serif;
}

.item-name {
  font-size: 1.2rem;
  color: var(--text);
}

.item-description {
  font-size: 0.9rem;
  opacity: 0.8;
  flex: 1;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.item-price {
  font-weight: 600;
  font-family: 'Press Start 2P', sans-serif;
  color: var(--accent);
}

.purchase-btn {
  padding: 0.5rem 1rem;
  background: var(--secondary);
  border: none;
  border-radius: 0.5rem;
  font-family: 'Roboto', sans-serif;
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
  .shop-header {
    flex-direction: column;
    gap: 1rem;
  }
  .shop-tabs {
    flex-direction: column;
  }
}
</style>
