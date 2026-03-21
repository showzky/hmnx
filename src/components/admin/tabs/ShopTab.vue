<template>
  <section class="shop-tab-wrap">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Shop <em>Items</em></div>
        <div class="sec-subtitle">Administrer varer og priser i butikken.</div>
      </div>
    </div>
    <ShopAdmin />
  </section>
</template>

<script>
import ShopAdmin from '../../../components/ShopAdmin.vue';

export default {
  components: {
    ShopAdmin
  }
}
</script>

<style scoped>
/* Add your styles here if needed */
</style>
