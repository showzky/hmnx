<template>
  <main class="about-container">
    <!-- Mission Section -->
    <section class="about-section">
      <h2>Vår Historie og Mål</h2>
      <div class="mission-box">
        <p>
          Vi startet i 2024 med en enkel visjon: å gjøre fylleangst mer tilgjengelig i Midt-Norge.
          I dag er vi et team på 6 dedikerte fagfolk som forstår at noen ganger trengs det både alkohol
          og en god kopp kaffe.
        </p>

        <!-- Statistics Grid -->
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">1+</div>
            <div class="stat-label">Års erfaring</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10K+</div>
            <div class="stat-label">Mennesker hjulpet</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="team-section">
      <h2>Vårt Team</h2>
      <div class="team-grid">
        <div v-for="member in team" :key="member.id" class="team-member">
          <div
            class="member-image"
            :style="{
              backgroundImage: `url('${member.avatar || '/assets/placeholder-avatar.jpg'}')`
            }"
          ></div>
          <h3>{{ member.name }}</h3>
          <p>{{ member.title }}</p>
          <p class="member-bio" v-if="member.bio">{{ member.bio }}</p>
        </div>
      </div>
    </section>

    <!-- Values Section -->
    <section class="values-section">
      <h2>Våre Verdier</h2>
      <div class="values-grid">
        <div v-for="(value, index) in values" :key="index" class="value-card">
          <h3>{{ value.icon }} {{ value.title }}</h3>
          <p>{{ value.description }}</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from '@/axios';

export default {
  name: "About",
  data() {
    return {
      team: [],
      values: [
        { icon: "🤝", title: "Forståelse", description: "Vi lytter først, diagnostiserer senere" },
        { icon: "🔓", title: "Åpenhet", description: "Ingen skjulte agenda eller kostnader" },
        { icon: "💡", title: "Innovasjon", description: "Kombinerer tradisjonell og digital hjelp" }
      ]
    };
  },
  methods: {
    async fetchTeamMembers() {
      try {
        const response = await axios.get('/team-members');
        this.team = response.data.team_members;
      } catch (error) {
        console.error('Error fetching team members:', error);
      }
    }
  },
  mounted() {
    this.fetchTeamMembers();
  }
};
</script>

<style scoped>
/* Existing styles remain unchanged */

/* Add new styles for member bio */
.member-bio {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

/* Update team member card for bio */
.team-member {
  text-align: center;
  padding: 1.5rem;
  background: var(--card-bg);
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.team-member:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.member-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  margin: 0 auto 1rem;
  background-size: cover;
  background-position: center;
  border: 3px solid #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.team-member h3 {
  margin: 0.5rem 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.team-member p {
  color: var(--text-secondary);
  margin: 0.25rem 0;
}
</style>
