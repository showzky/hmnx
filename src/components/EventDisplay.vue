<template>
    <div class="event-display">
      <!-- Use the processed event data instead of the raw eventData -->
      <component :is="templateComponent" v-bind="processedEventData"></component>
    </div>
  </template>
  
  <script>
  import Template1 from './Template1.vue'; 
  import Template2 from './Template2.vue';
  
  export default {
    name: 'EventDisplay',
    components: { Template1, Template2 },
    props: {
      eventData: {
        type: Object,
        required: true // Expect to receive event data as a prop from EventDetailPage
      }
    },
    computed: {
      // Convert snake_case keys from the backend to camelCase for the child components
      processedEventData() {
        return {
          eventTitle: this.eventData.event_name,
          eventDate: this.eventData.event_date,
          eventTime: this.eventData.event_time,
          eventDescription: this.eventData.event_description,
          eventImagePath: this.eventData.event_image_path,
          // Optionally add more fields if needed:
          eventLocation: this.eventData.event_location || '',
          eventPhoneNumber: this.eventData.event_phone_number || '',
          eventWarning: this.eventData.event_warning || '',
          eventContactEmail: this.eventData.event_contact_email || ''
        };
      },
      templateComponent() {
        // Choose which template to use based on the eventData.template_name value
        const templateName = this.eventData.template_name;
        if (templateName === 'template1') {
          return 'Template1';
        } else if (templateName === 'template2') {
          return 'Template2';
        } else {
          console.warn(`Unknown template name: ${templateName}. Using default Template1.`);
          return 'Template1';
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .event-display {
    margin-bottom: 20px;
  }
  </style>
  