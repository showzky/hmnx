<template>
    <div>
      <!-- Hero Section -->
      <div class="hero">
        <h1>HMN Mental Pasienter</h1>
        <p class="slogan">Profesjonelle uansvarlige siden 2024</p>
      </div>
  
      <div class="hero">
       
       
  
        <!-- Timeline Section -->
        <div class="timeline-meme">
          <div class="timeline-item">
            <div class="timeline-emoji">🎉</div>
            <div class="timeline-text">
              <h3>Født i kaos</h3>
              <p>"vi liker kake med sjokkolade alle sammen face to face" - Thomas, probably</p>
            </div>
          </div>
  
          <div class="timeline-item discord-highlight">
            <div class="timeline-emoji">🎮</div>
            <div class="timeline-text">
              <h3>TimeCraft Discord</h3>
              <p>
                Hovedkvarter for:
                <br />
                <span class="discord-activities">
                  Vi for sjå ka æ ska skriv hær🗿
                  <br />
                  Noen ord hær å vett🍕
                </span>
              </p>
              <button class="discord-btn" @click="openDiscord">
                Bli med i koret av kaos
              </button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Meeting Section -->
      <section class="meeting-section">
        <h2>🏔️ Historisk Øyeblikk</h2>
        <div class="meeting-card">
          <p class="meeting-date">August 2024</p>
          <h3>Den store Sunndalsøra-konspirasjonen</h3>
          <p>Hva skjedde egentlig der oppe? Verden vil aldri vite...</p>
          <div class="classified">
            🔒 KLASSIFISERT
            <span class="tooltip">(Spør Kim-Andre om passord)</span>
          </div>
        </div>
      </section>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Home',
    methods: {
      openDiscord() {
        window.open('YOUR_DISCORD_INVITE_LINK', '_blank');
      }
    }
  };
  </script>
  
  <style scoped>
  /* Optional - Keep global styles in your main `style.css` file */
  /* Add any section-specific tweaks here if necessary */
  </style>
  