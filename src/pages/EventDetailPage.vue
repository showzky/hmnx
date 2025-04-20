<template>
    <div v-if="isLoading">
      Loading event details...
    </div>
    <div v-else-if="event">
      <h1>Event Detail Page</h1>
      <EventDisplay :event-data="event" />
    </div>
    <div v-else-if="error">
      Error loading event details: {{ error }}
    </div>
    <div v-else>
      <p>Could not load event details.</p>
    </div>
  </template>
  
  <script>
  import EventDisplay from '@/components/EventDisplay.vue'; // Import EventDisplay component
  import axios from '@/axios'; // Import axios
  
  export default {
    name: 'EventDetailPage',
    components: {
      EventDisplay // Register EventDisplay component
    },
    props: {
      eventId: {
        type: String, // or Number, depending on your event ID type
        required: true
      }
    },
    data() {
      return {
        event: null,
        isLoading: true,
        error: null
      };
    },
    mounted() {
      this.fetchEventDetails();
    },
    methods: {
      fetchEventDetails() {
        this.isLoading = true;
        this.error = null;
        const eventId = this.eventId; // Access eventId from props
        axios.get(`/events/${eventId}`) // --- IMPORTANT:  Verify your Flask endpoint for fetching single event by ID ---
          .then(response => {
            console.log('Fetched event details:', response.data.event); // Log the fetched event data
            this.event = response.data.event; // Assuming your backend returns event data in response.data.event
            this.isLoading = false;
          })
          .catch(error => {
            console.error('Error fetching event details:', error);
            this.error = error.message || 'Failed to load event details.';
            this.isLoading = false;
          });
      }
    }
  };
  </script>
  
  <style scoped>
  /* You can add basic styling for EventDetailPage if needed, e.g., for loading/error messages */
  </style>