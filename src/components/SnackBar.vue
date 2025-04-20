<template>
    <!-- === SNACKBAR TEMPLATE ===
         - Displays the notification message.
         - Uses dynamic classes based on the 'type' prop.
         - Includes a close button to hide the snackbar.
    -->
    <div :class="['snackbar', type]" v-if="visible">
      <span>{{ message }}</span>
      <button @click="hideSnackBar">X</button>
    </div>
  </template>
  
  <script>
export default {
  name: "SnackBar",
  props: {
    // === COMPONENT PROPERTIES ===
    // - 'message': The text to display.
    // - 'duration': How long the snack bar is visible (default: 3000ms).
    // - 'type': Determines the visual style (e.g., 'info', 'success', 'error').
    message: {
      type: String,
      required: true,
    },
    duration: {
      type: Number,
      default: 3000,
    },
    type: {
      type: String,
      default: 'info', // Default type styling
    },
  },
  data() {
    return {
      // === COMPONENT STATE ===
      // - 'visible': Controls the display of the snack bar.
      visible: false,
    };
  },
  methods: {
    showSnackBar() {
      // === SHOW SNACKBAR ===
      // - Set visible to true to display the snack bar.
      // - Automatically hide after the specified duration.
      this.visible = true;
      setTimeout(() => {
        this.hideSnackBar();
      }, this.duration);
    },
    hideSnackBar() {
      // === HIDE SNACKBAR ===
      // - Set visible to false to hide the snack bar.
      this.visible = false;
    },
  },
  mounted() {
    // === COMPONENT MOUNTED ===
    // - Automatically trigger the snack bar when the component mounts.
    //   (For more control, you can remove this and call showSnackBar() from the parent.)
    this.showSnackBar();
  },
};
</script>

<style scoped>

.snackbar {
  /* === BASE SNACKBAR STYLING ===
       - Positioned fixed at the bottom center.
       - Sets common background, padding, and rounded corners.
  */
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  padding: 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

/* === TYPE-SPECIFIC STYLING ===
     - 'info': Default look.
     - 'success': Green background for success messages.
     - 'error': Red background for error messages.
*/
.snackbar.info {
  background-color: #323232;
}
.snackbar.success {
  background-color: #4caf50;
}
.snackbar.error {
  background-color: #f44336;
}

/* === CLOSE BUTTON STYLING === */
.snackbar button {
  background: none;
  border: none;
  color: #fff;
  margin-left: 16px;
  cursor: pointer;
}
</style>
