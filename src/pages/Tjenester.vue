<template>
    <div>
      <!-- Hero Section -->
      <div class="hero">
        <h1>Tjenester - HMN Mental Pasienter</h1>
      </div>
  
      <main class="services-container">
        <!-- EMERGENCY SERVICES -->
        <section class="service-card emergency-section">
          <h2>🆘 Nød-tjenester</h2>
          <div class="service-grid">
            <div class="service-item">
              <h3>Eksistensiell Krise First Aid</h3>
              <p>Symptomer: Gråt til Miley Cyrus, spise is direkte fra boksen</p>
              <button class="panic-btn" @click="generatePrescription">Generer nød-resept</button>
              <p id="prescriptionOutput" class="prescription-text">{{ prescription }}</p>
            </div>
  
            <div class="service-item">
              <h3>Odin's 5-STEGS PROTOKOLL</h3>
              <ol class="protocol-list">
                <li>Panikk</li>
                <li>Finn en syndebukk</li>
                <li>Spis kebab</li>
                <li>Nekt alt</li>
                <li>Gjenta</li>
              </ol>
            </div>
          </div>
        </section>
  
        <!-- SPECIALISTTJENESTER -->
        <section class="service-card">
          <h2>🤪 Spesialtjenester</h2>
          <div class="service-grid">
            <div class="service-item">
              <h3>Andre's Snack-terapi</h3>
              <p>Diagnose via chips-smak:</p>
              <ul class="chip-flavors">
                <li>🌶️ Sour Cream & Onion = Lett stress</li>
                <li>🔥 Hot Chili = Full kollaps</li>
              </ul>
            </div>
  
            <div class="service-item">
              <h3>WiFi-sjel</h3>
              <p>"Kurert av Håkon":</p>
              <div class="wifi-status">
                <span>{{ wifiBars }}</span>
                <button @click="fixWifi">Fiks WiFi-traume</button>
              </div>
            </div>
          </div>
        </section>
  
        <!-- LIVE PANIC FEED -->
        <section class="service-card">
          <h2>🎪 Live Panikk-feed</h2>
          <div class="panic-feed">
            <p v-for="message in panicFeed" :key="message">{{ message }}</p>
          </div>
          <button class="panic-btn" @click="addPanicMessage">Simuler ny krise</button>
        </section>
      </main>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        prescription: '',
        wifiBars: '📶📶📶📶',
        panicFeed: [
          '03:14 - Oliver: HVORFOR ER HIMMELEN BLÅ?!',
          '04:20 - Pasient #7: Hvem stjæler alltid sokker mine??'
        ]
      };
    },
    methods: {
      generatePrescription() {
        const prescriptions = [
          'Ta en lang dusj',
          'Lytt til favorittlåten din',
          'Gå en tur i frisk luft',
          'Koble fra sosiale medier'
        ];
        this.prescription = prescriptions[Math.floor(Math.random() * prescriptions.length)];
      },
      fixWifi() {
        this.wifiBars = '📶📶📶📶📶'; // Fully restored
      },
      addPanicMessage() {
        const newMessage = `04:${Math.floor(Math.random() * 59).toString().padStart(2, '0')} - Random User: PANIKK!`;
        this.panicFeed.push(newMessage);
      }
    }
  };
  </script>
  
  <style scoped>
  /* Reuse global CSS styles if possible, but add scoped tweaks as needed */
  </style>
  