<template>
    <div class="event-template-text-based">
      <header class="event-header">
        <h2 class="event-title">{{ eventTitle }}</h2>
        <p class="event-datetime">
          {{ eventDate }} | {{ eventTime }}
        </p>
        <p class="event-location" v-if="eventLocation">Location: {{ eventLocation }}</p>
        <p class="event-phone" v-if="eventPhoneNumber">Phone: {{ eventPhoneNumber }}</p>
      </header>
  
      <section class="event-description">
        <h3>About this Event</h3>
        <p>{{ eventDescription }}</p>
      </section>
  
      <section class="event-signup">
        <h3>Register Now!</h3>
        <p>Don't miss out - secure your spot today.</p>
        <form @submit.prevent="signUpForEvent">
          <div class="form-group">
            <label for="email">Your Email:</label>
            <input type="email" id="email" v-model="signupEmail" placeholder="your@email.com" required>
          </div>
          <button type="submit" class="signup-button">Sign Up</button>
        </form>
      </section>
  
      <p class="event-warning" v-if="eventWarning">Important: {{ eventWarning }}</p>
      <p class="contact-info" v-if="eventContactEmail">Contact us at: <a :href="`mailto:${eventContactEmail}`">{{ eventContactEmail }}</a></p>
  
    </div>
  </template>
  
  <script>
  export default {
    name: 'Template2',
    props: {
      eventTitle: {
        type: String,
        required: true
      },
      eventDate: {
        type: String, // Or Date object
        required: true
      },
      eventTime: {
        type: String,
        required: true
      },
      eventDescription: {
        type: String,
        default: ''
      },
      eventLocation: {
        type: String,
        default: ''
      },
      eventPhoneNumber: {
        type: String,
        default: ''
      },
      eventWarning: {
        type: String,
        default: ''
      },
      eventContactEmail: {
        type: String,
        default: ''
      }
    },
    data() {
      return {
        signupEmail: ''
      };
    },
    methods: {
      signUpForEvent() {
        // Placeholder signup functionality
        console.log('User signed up with email:', this.signupEmail);
        alert('Signup functionality is a placeholder in this template. In a real app, we would send this email to the backend.');
        this.signupEmail = ''; // Reset email input
      }
    }
  };
  </script>
  
  <style scoped>
  .event-template-text-based {
    font-family: 'Verdana', sans-serif; /* Different font for text focus */
    color: #333; /* Darker default text color */
    padding: 2rem;
    max-width: 800px; /* Limit width for readability */
    margin: 20px auto; /* Center on page */
    background-color: #f8f9fa; /* Light background for contrast */
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    text-align: left; /* Left-align text for text-focused template */
  }
  
  .event-header {
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #007bff; /* Blue underline for header */
    padding-bottom: 0.5rem;
  }
  
  .event-title {
    font-size: 2rem;
    margin-bottom: 0.3rem;
    color: #0056b3; /* Darker blue title */
  }
  
  .event-datetime, .event-location, .event-phone {
    font-size: 1rem;
    color: #555; /* Medium gray for metadata */
    margin-bottom: 0.3rem;
  }
  
  .event-description {
    margin-bottom: 2rem;
    line-height: 1.7;
    font-size: 1.1rem;
  }
  
  .event-description h3 {
    font-size: 1.3rem;
    margin-bottom: 0.8rem;
    color: #007bff; /* Blue heading within description */
  }
  
  .event-signup {
    background-color: #e9ecef; /* Light gray signup section */
    padding: 1.5rem;
    border-radius: 0.3rem;
    margin-bottom: 1.5rem;
  }
  
  .event-signup h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.4rem;
    color: #343a40; /* Dark gray signup heading */
  }
  
  .event-signup p {
    margin-bottom: 1rem;
    color: #666; /* Slightly lighter text in signup section */
  }
  
  .event-signup .form-group {
    margin-bottom: 1rem;
  }
  
  .event-signup label {
    display: block;
    margin-bottom: 0.3rem;
    font-weight: bold;
    color: #495057;
  }
  
  .event-signup input[type="email"] {
    width: 100%;
    padding: 0.6rem;
    border: 1px solid #ced4da;
    border-radius: 0.2rem;
    font-size: 1rem;
  }
  
  .event-signup .signup-button {
    background-color: #28a745; /* Green signup button */
    color: white;
    border: none;
    padding: 0.7rem 1.3rem;
    border-radius: 0.2rem;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.2s ease;
  }
  
  .event-signup .signup-button:hover {
    background-color: #218838;
  }
  
  .event-warning {
    color: #d35400; /* Orange warning text */
    font-style: italic;
    margin-bottom: 0.5rem;
  }
  
  .contact-info a {
    color: #007bff; /* Blue contact link */
    text-decoration: underline;
  }
  
  </style>