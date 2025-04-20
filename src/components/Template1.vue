<template>
  <div class="event-hero" :style="{ backgroundImage: `url(${eventImagePath})` }">
    <!-- Dark overlay for contrast -->
    <div class="overlay"></div>

    <!-- Main content container -->
    <div class="content-wrapper">
      <div class="text-content">
        <!-- Large Event Title -->
        <h1 class="event-title">{{ eventTitle }}</h1>

        <!-- Event Description Paragraph -->
        <p class="event-description">
          {{ eventDescription }}
        </p>

        <!-- Additional Event Details (Date, Location, Time, Warning) -->
        <div class="event-details">
          <div class="date-box">
            <!-- Example: Break your date into day & month if you prefer that style -->
            <div class="date-day">{{ formattedDay }}</div>
            <div class="date-month">{{ formattedMonth }}</div>
          </div>
          <div class="event-location-time">
            <p v-if="eventLocation" class="location">{{ eventLocation }}</p>
            <p v-if="eventTime" class="time">{{ eventTime }}</p>
            <p v-if="eventWarning" class="warning">Warning! {{ eventWarning }}</p>
          </div>
        </div>

        <!-- Horizontal Email Form & Button -->
        <div class="email-form">
          <input
            type="email"
            v-model="signupEmail"
            placeholder="Enter your email"
            class="email-input"
            required
          />
          <button @click="signUpForEvent" class="follow-button">
            Follow
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventTemplateImageBased',
  props: {
    eventTitle: {
      type: String,
      required: true
    },
    eventDate: {
      type: String, // or Date object
      default: ''
    },
    eventTime: {
      type: String,
      default: ''
    },
    eventDescription: {
      type: String,
      default: ''
    },
    eventImagePath: {
      type: String,
      default: ''
    },
    eventLocation: {
      type: String,
      default: ''
    },
    eventWarning: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      signupEmail: ''
    };
  },
  computed: {
    // If your event_date is a string like "2025-11-28", parse it for day/month display
    formattedDay() {
      if (!this.eventDate) return '';
      const dateObj = new Date(this.eventDate);
      return dateObj.getDate() || ''; // e.g., 28
    },
    formattedMonth() {
      if (!this.eventDate) return '';
      const dateObj = new Date(this.eventDate);
      // You can format the month name however you like, e.g., short or long
      return dateObj.toLocaleString('default', { month: 'long' }) || ''; // e.g., "November"
    }
  },
  methods: {
    signUpForEvent() {
      console.log('User signed up with email:', this.signupEmail);
      alert('Signup is a placeholder. In production, you would send this to the backend.');
      this.signupEmail = '';
    }
  }
};
</script>

<style scoped>
/* ------------------------------
   Root Variables (Adjust to match your brand)
------------------------------ */
:root {
  --primary-text: #ffffff;
  --secondary-text: #e0e0e0;
  --highlight-color: #ff6b6b; /* Example highlight/accent color */
  --overlay-color: rgba(0, 0, 0, 0.7);
  --card-bg: rgba(255, 255, 255, 0.1);
  --transition: 0.3s ease;
  --font-family: "Helvetica Neue", Arial, sans-serif;
}

.event-hero {
  position: relative;
  width: 100%;
  min-height: 100vh; /* Fill the viewport */
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center; /* Vertically center content */
  justify-content: flex-start; /* Align text to the left (optional) */
  font-family: var(--font-family);
  color: var(--primary-text);
  padding: 2rem; /* Adjust for side spacing */
  box-sizing: border-box;
}

/* Dark overlay on top of the background image */
.overlay {
  position: absolute;
  inset: 0;
  background-color: var(--overlay-color);
  z-index: 1;
}

/* Main wrapper for the text content */
.content-wrapper {
  position: relative;
  z-index: 2; /* Above overlay */
  max-width: 1200px;
  width: 100%;
  margin: 0 auto; /* Center horizontally */
}

/* Container for all textual and form elements */
.text-content {
  max-width: 700px; /* Limit width for readability */
}

/* ------------------------------
   Title & Description
------------------------------ */
.event-title {
  font-size: 3rem;
  line-height: 1.2;
  margin-bottom: 1rem;
  font-weight: 700;
  color: var(--primary-text);
}

.event-description {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  color: var(--secondary-text);
}

/* ------------------------------
   Event Details
------------------------------ */
.event-details {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* Date box to mimic the small calendar style in the reference */
.date-box {
  background: var(--card-bg);
  backdrop-filter: blur(5px);
  padding: 1rem;
  border-radius: 0.5rem;
  text-align: center;
  min-width: 80px;
}

.date-day {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
  color: var(--primary-text);
}

.date-month {
  font-size: 1rem;
  text-transform: uppercase;
  color: var(--secondary-text);
}

.event-location-time {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.location,
.time,
.warning {
  font-size: 1rem;
  color: var(--secondary-text);
}

.warning {
  color: #ffb300; /* Example warning color (amber) */
  font-weight: 600;
}

/* ------------------------------
   Email Form
------------------------------ */
.email-form {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 500px;
  margin-bottom: 2rem;
}

.email-input {
  flex: 1; /* Take remaining space */
  padding: 0.8rem;
  border: none;
  border-radius: 0.3rem;
  font-size: 1rem;
  outline: none;
}

.email-input:focus {
  box-shadow: 0 0 0 2px var(--highlight-color);
}

.follow-button {
  padding: 0.8rem 1.5rem;
  background-color: var(--highlight-color);
  color: #fff;
  border: none;
  border-radius: 0.3rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition);
  text-transform: uppercase;
}

.follow-button:hover {
  background-color: #ff5a5a; /* Slightly darker shade on hover */
}

/* ------------------------------
   Responsive Adjustments
------------------------------ */
@media (max-width: 768px) {
  .event-title {
    font-size: 2.2rem;
  }
  .event-description {
    font-size: 1.1rem;
  }
  .event-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .event-title {
    font-size: 1.8rem;
  }
  .date-box {
    min-width: 60px;
  }
  .email-form {
    flex-direction: column;
    align-items: stretch;
  }
  .follow-button {
    width: 100%;
    text-align: center;
  }
}
</style>
