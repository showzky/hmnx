<template>
  <section class="achievement-tab-wrap">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Achieve<em>ments</em></div>
        <div class="sec-subtitle">Opprett achievements, sett betingelser og gi dem til brukere.</div>
      </div>
    </div>
    <AchievementAdmin />
  </section>
</template>

<script>
import AchievementAdmin from '@/components/AchievementAdmin.vue';

export default {
  name: 'AchievementTab',
  components: { AchievementAdmin }
};
</script>

<style scoped></style> 