<template>
    <footer class="site-footer">
      <div class="footer-container">
        <!-- Left Section -->
        <div class="footer-brand">
          <div class="logo">Helse Midt-Norge MP</div>
          <p class="footer-slogan">Vi hjelper hjernen din - siden 2024</p>
        </div>
  
        <!-- Middle Section -->
        <div class="footer-links">
          <h4>Hurtiglenker</h4>
          <ul>
            <li><router-link to="/">Hjem</router-link></li>
            <li><router-link to="/about">Om oss</router-link></li>
            <li><router-link to="/tjenester">Tjenester</router-link></li>
            <li><router-link to="/kontakt">Kontakt</router-link></li> <!-- Placeholder -->
          </ul>
        </div>
  
        <!-- Right Section -->
        <div class="footer-social">
          <h4>Følg oss</h4>
          <div class="social-icons">
            <a href="#" class="social-link">📘</a> <!-- Facebook -->
            <a href="#" class="social-link">📸</a> <!-- Instagram -->
            <a href="#" class="social-link">🎵</a> <!-- TikTok -->
          </div>
        </div>
      </div>
  
      <!-- Copyright Notice -->
      <div class="footer-copyright">
        <p>© 2024 HMN Mental Pasienter. All drama beskyttet.</p>
      </div>
    </footer>
  </template>
  
  <script>
  export default {
    name: 'Footer'
  }
  </script>
  