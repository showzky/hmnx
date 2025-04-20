<template>
    <section class="contact-section">
      <!-- decorative “pills” -->
      <div class="pill pill--red"></div>
      <div class="pill pill--teal"></div>
      <div class="pill pill--circle"></div>
  
      <div class="contact-card">
        <header class="contact-header">
          <h1>🩺 Medical Contact</h1>
          <p class="subtitle">“Got symptoms of a bug? Drop us a line!”</p>
        </header>
  
        <form @submit.prevent="handleSubmit" class="contact-form">
          <div class="field">
            <label for="name">👤 Full Name</label>
            <input
              id="name"
              type="text"
              v-model="form.name"
              placeholder="Your Name"
              required
            />
          </div>
  
          <div class="field">
            <label for="email">📧 Email</label>
            <input
              id="email"
              type="email"
              v-model="form.email"
              placeholder="you@hospital.com"
              required
            />
          </div>
  
          <div class="field">
            <label for="message">💬 Describe Your “Symptoms”</label>
            <textarea
              id="message"
              v-model="form.message"
              rows="4"
              placeholder="What’s ailing you?"
              required
            ></textarea>
          </div>
  
          <button type="submit" class="btn-submit">💉 Send to the Lab</button>
  
          <p v-if="submitted" class="confirmation">
            ✅ Specimen received—our team will be in touch!
          </p>
        </form>
      </div>
    </section>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from '@/axios' // ⬅️ Make sure this works or adjust if needed
  
  const form = ref({ name: '', email: '', message: '' })
  const submitted = ref(false)
  
  async function handleSubmit() {
    try {
      console.log('Form data:', form.value)
      await axios.post('/send-message', form.value)
      submitted.value = true
  
      setTimeout(() => {
        form.value = { name: '', email: '', message: '' }
        submitted.value = false
      }, 3000)
    } catch (error) {
      console.error('Failed to send message:', error)
      alert('❌ Failed to send message. Please try again later.')
    }
  }
  </script>
  
  
  <style scoped>
  /* Container & background */
  .contact-section {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    overflow: hidden;
    background: linear-gradient(
      to bottom right,
      #e0f7f9 0%,
      #ffffff 50%,
      #fde2e2 100%
    );
  }
  
  /* Decorative “pills” */
  .pill {
    position: absolute;
    border-radius: 999px;
    opacity: 0.4;
    animation: pulse 4s ease-in-out infinite;
  }
  .pill--red {
    top: 10%;
    left: 5%;
    width: 200px;
    height: 70px;
    background: #f88379;
    transform: rotate(45deg);
  }
  .pill--teal {
    bottom: 20%;
    right: 10%;
    width: 150px;
    height: 50px;
    background: #88ddff;
    transform: rotate(-12deg);
  }
  .pill--circle {
    top: 50%;
    right: 30%;
    width: 100px;
    height: 100px;
    background: rgba(255, 255, 255, 0.3);
    border: 2px solid #ff7070;
    border-radius: 50%;
    transform: translateY(-50%);
    animation: none;
    opacity: 0.3;
  }
  
  /* Card */
  .contact-card {
    position: relative;
    width: 100%;
    max-width: 600px;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.6s ease-out both;
    z-index: 1;
  }
  
  /* Header */
  .contact-header h1 {
    margin: 0;
    font-size: 2.5rem;
    text-align: center;
    color: #333;
  }
  .contact-header .subtitle {
    margin-top: 0.5rem;
    text-align: center;
    color: #666;
    font-style: italic;
  }
  
  /* Form */
  .contact-form {
    margin-top: 1.5rem;
  }
  .field {
    margin-bottom: 1.25rem;
  }
  .field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #444;
  }
  .field input,
  .field textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #ccc;
    border-radius: 1rem;
    background: rgba(255, 255, 255, 0.6);
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
    transition: border-color 0.3s;
    font-size: 1rem;
    color: #333;
  }
  .field input:focus,
  .field textarea:focus {
    outline: none;
    border-color: #f56a6a;
  }
  
  /* Button */
  .btn-submit {
    display: block;
    width: 100%;
    padding: 0.75rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(90deg, #e53e3e, #319795);
    border: none;
    border-radius: 1rem;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
  
  /* Confirmation text */
  .confirmation {
    margin-top: 1rem;
    text-align: center;
    color: #2f855a;
    font-weight: 500;
  }
  
  /* Animations */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  @keyframes pulse {
    0%,
    100% {
      opacity: 0.3;
    }
    50% {
      opacity: 0.6;
    }
  }
  </style>
  