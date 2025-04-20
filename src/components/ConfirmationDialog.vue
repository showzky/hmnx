<template>
    <div v-if="visible" class="confirmation-dialog-overlay">
      <div class="confirmation-dialog">
        <div class="dialog-header">
          <slot name="header">Confirm Action</slot>
        </div>
        <div class="dialog-body">
          <p>{{ message }}</p>
        </div>
        <div class="dialog-footer">
          <button @click="$emit('cancel')" class="cancel-button">Cancel</button>
          <button @click="$emit('confirm')" class="confirm-button">Confirm</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ConfirmationDialog',
    props: {
      visible: {
        type: Boolean,
        required: true,
        default: false
      },
      message: {
        type: String,
        default: 'Are you sure you want to perform this action?'
      }
    },
    emits: ['confirm', 'cancel'] // Define custom events to emit
  };
  </script>
  
  <style scoped>
  .confirmation-dialog-overlay {
    position: fixed; /* Stay in place */
    z-index: 1050; /* Sit on top */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgba(0, 0, 0, 0.4); /* Black w/ opacity */
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .confirmation-dialog {
    background-color: #fefefe;
    margin: 15% auto; /* 15% from the top and centered */
    padding: 20px;
    border: 1px solid #888;
    width: 80%; /* Could be more or less, depending on screen size */
    max-width: 500px;
    border-radius: 0.5rem;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
  }
  
  .dialog-header, .dialog-footer {
    padding: 10px;
    text-align: center;
  }
  
  .dialog-header {
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .dialog-body {
    padding: 15px 20px;
    margin-bottom: 20px;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: center;
    gap: 15px;
    border-top: 1px solid #eee;
    padding-top: 20px;
  }
  
  .confirm-button, .cancel-button {
    padding: 10px 20px;
    border: none;
    border-radius: 0.3rem;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .confirm-button {
    background-color: #dc3545; /* Bootstrap danger color */
    color: white;
  }
  
  .confirm-button:hover {
    background-color: #c82333;
  }
  
  .cancel-button {
    background-color: #6c757d; /* Bootstrap secondary color */
    color: white;
  }
  
  .cancel-button:hover {
    background-color: #5a6268;
  }
  </style>