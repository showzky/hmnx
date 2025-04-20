<template>
    <div class="thread-editor">
      <div ref="editorContainer"></div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue';
  import Quill from 'quill';
  import 'quill/dist/quill.snow.css'; // Importer Quill sitt standard tema
  
  export default {
    name: 'ThreadEditor',
    props: {
      modelValue: {
        type: String,
        default: ''
      }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const editorContainer = ref(null);
      let quill;
  
      onMounted(() => {
        quill = new Quill(editorContainer.value, {
          theme: 'snow',
          modules: {
            toolbar: [
              ['bold', 'italic'], // Bold and Italic buttons
              // Du kan legge til flere knapper her om ønskelig
            ]
          }
        });
  
        // Sett initial innhold
        quill.root.innerHTML = props.modelValue;
  
        // Oppdater v-model når teksten endres
        quill.on('text-change', () => {
          emit('update:modelValue', quill.root.innerHTML);
        });
      });
  
      // Hvis modelValue endres utenfra, oppdater Quill (valgfritt)
      watch(() => props.modelValue, (newValue) => {
        if (quill && newValue !== quill.root.innerHTML) {
          quill.root.innerHTML = newValue;
        }
      });
  
      return {
        editorContainer
      };
    }
  };
  </script>
  
  <style scoped>
  .thread-editor {
    border: none; /* Ingen ramme */
    border-radius: 6px;
    background: #f0f4f8;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); /* Subtil skygge */
  
    /* Ny linje for å gjøre den 100% bredde av foreldre-containeren: */
    width: 100%;
  }

  /* Legg til i <style scoped> i ThreadEditor.vue, eller i global CSS */

.ql-toolbar.ql-snow {
  border: none; /* Fjern ramme rundt verktøylinje */
  background-color: #f9fafb; /* Veldig lys grå bakgrunn for verktøylinjen */
  border-bottom: 1px solid #e2e8f0; /* Subtil skillelinje under verktøylinjen */
  border-radius: 6px 6px 0 0; /* Avrundede hjørner *kun øverst* */
}

.ql-toolbar.ql-snow .ql-formats button {
  border: none; /* Fjern ramme rundt knapper */
  background-color: transparent; /* Transparent bakgrunn for knapper (som standard) */
  color: #4a5568; /* Mørkere grå farge for knapp-ikoner */
  border-radius: 4px; /* Litt avrundede hjørner for knapper */
  padding: 0.4em 0.5em; /* Litt mindre padding på knappene */
  transition: background-color 0.2s ease-in-out; /* Myk hover-effekt */
}

.ql-toolbar.ql-snow .ql-formats button:hover,
.ql-toolbar.ql-snow .ql-formats button.ql-active {
  background-color: #e5e7eb; /* Lysere grå bakgrunn på hover og aktiv tilstand */
}

.ql-toolbar.ql-snow .ql-formats button:focus {
  outline: none; /* Fjern standard fokus-ramme fra nettleser */
  box-shadow: 0 0 0 2px #a3bffa; /* Egen fokus-indikator (lys blå skygge) */
}
  </style>
  