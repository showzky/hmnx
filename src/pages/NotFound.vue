<template>
    <div class="not-found-page">
      <div class="container">
        <div class="floating-pill" style="left: 10%; top: 20%">💊</div>
        <div class="floating-pill" style="right: 15%; top: 60%">🧪</div>
        
        <h1 class="error-code">404</h1>
        
        <div class="prescription">
          <h2>PRESCRIPTION NOT FOUND</h2>
          <p>
            This page is currently undergoing clinical trials.<br>
            Possible side effects may include confusion or temporary disorientation.
          </p>
          <button class="home-button" @click="goHome">Return to Lab</button>
          <p class="warning">* If symptoms persist, consult your web developer</p>
        </div>
        
        <div class="injection">💉</div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "NotFound",
    methods: {
      goHome() {
        this.$router.push('/');
      }
    }
  };
  </script>
  
  <style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Anton&family=Roboto:wght@300;700&display=swap');
  
  .not-found-page {
    --primary-color: #0066cc;
    --secondary-color: #e00000;
    --bg-color: #f0f7ff;
  
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-color);
    font-family: 'Roboto', sans-serif;
    overflow: hidden;
  }
  
  .container {
    text-align: center;
    position: relative;
    padding: 2rem;
  }
  
  .error-code {
    font-family: 'Anton', sans-serif;
    font-size: 20vw;
    color: var(--primary-color);
    margin: 0;
    text-shadow: 3px 3px 0 rgba(0,0,0,0.1);
    position: relative;
    animation: heartbeat 2s infinite;
  }
  
  .error-code::after {
    content: '🚑';
    position: absolute;
    right: -0.2em;
    bottom: -0.2em;
    font-size: 0.4em;
    transform: rotate(20deg);
    animation: siren 1s infinite alternate;
  }
  
  .prescription {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    display: inline-block;
    margin: 2rem 0;
    position: relative;
    transform: rotate(-2deg);
    border: 3px dashed var(--secondary-color);
  }
  
  .prescription h2 {
    color: var(--secondary-color);
    margin: 0 0 1rem;
    font-size: 2.5em;
  }
  
  .prescription::before {
    content: '✖';
    position: absolute;
    top: -30px;
    left: -30px;
    font-size: 4em;
    opacity: 0.1;
    animation: floating 3s ease-in-out infinite;
  }
  
  .injection {
    width: 100px;
    height: 100px;
    position: absolute;
    right: 5%;
    bottom: 10%;
    animation: inject 2s ease-in-out infinite;
  }
  
  @keyframes heartbeat {
    0% { transform: scale(1); }
    15% { transform: scale(1.3); }
    30% { transform: scale(1); }
    45% { transform: scale(1.15); }
    60% { transform: scale(1); }
    100% { transform: scale(1); }
  }
  
  @keyframes siren {
    from { filter: hue-rotate(0deg); }
    to { filter: hue-rotate(360deg); }
  }
  
  @keyframes inject {
    0% { transform: translateY(0) rotate(45deg); }
    50% { transform: translateY(-20px) rotate(45deg); }
    100% { transform: translateY(0) rotate(45deg); }
  }
  
  .home-button {
    background: var(--primary-color) !important; /* Force override */
    color: white !important;
    padding: 1rem 2rem;
    border: none;
    border-radius: 50px;
    font-size: 1.2em;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  }
  
  .home-button:hover {
    transform: scale(1.1);
    background: var(--secondary-color) !important;
  }
  
  .warning {
    color: var(--secondary-color);
    font-size: 0.9em;
    margin-top: 2rem;
    font-style: italic;
  }
  
  .floating-pill {
    position: absolute;
    animation: floating 3s ease-in-out infinite;
    opacity: 0.2;
  }
  
  @keyframes floating {
    0% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
    100% { transform: translateY(0); }
  }
  </style>