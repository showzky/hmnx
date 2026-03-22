<template>
  <section class="news-admin">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Nyheter / <em>Innlegg</em></div>
        <div class="sec-subtitle">Publiser og administrer nyhetsinnlegg på forsiden.</div>
      </div>
    </div>
    <div class="g2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">{{ editing ? 'Rediger innlegg' : 'Nytt innlegg' }}</span></div>
        <div class="panel-body">
          <form @submit.prevent="saveNews">
            <div class="form-group">
              <label class="form-label">Tittel</label>
              <input class="form-input" v-model="form.title" placeholder="Tittel på innlegg..." required />
            </div>
            <div class="form-group" style="margin-bottom:16px;">
              <label class="form-label">Innhold</label>
              <quill-editor
                v-model:content="form.content"
                content-type="html"
                :toolbar="toolbarOptions"
                style="background:var(--s2);border:1px solid var(--border);border-radius:6px;color:var(--text);"
              />
            </div>
            <div style="display:flex;gap:8px;margin-top:12px;">
              <button type="submit" class="btn btn-red">{{ editing ? 'Oppdater' : 'Publiser' }}</button>
              <button type="button" v-if="editing" class="btn btn-ghost" @click="cancelEdit">Avbryt</button>
            </div>
          </form>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Alle innlegg</span>
          <span class="panel-meta">{{ newsItems.length }} stk</span>
        </div>
        <div class="panel-body" style="padding:0;">
          <table class="data-table">
            <thead>
              <tr><th>Tittel</th><th>Dato</th><th>Handlinger</th></tr>
            </thead>
            <tbody>
              <tr v-for="item in newsItems" :key="item.id">
                <td>{{ item.title }}</td>
                <td style="color:var(--muted);font-size:12px;">{{ item.date }}</td>
                <td>
                  <div style="display:flex;gap:6px;">
                    <button class="btn btn-cyan btn-sm" @click="editNews(item)">Rediger</button>
                    <button class="btn btn-danger btn-sm" @click="deleteNews(item.id)">Slett</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!newsItems.length">
                <td colspan="3" style="color:var(--muted);font-style:italic;">Ingen innlegg ennå.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  components: { QuillEditor },
  data() {
    return {
      newsItems: [],
      form: { id: null, title: "", content: "", date: "" },
      editing: false,
      toolbarOptions: [
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'header': [1, 2, 3, false] }],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'font': [] }],
        [{ 'align': [] }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        ['link', 'image'],
        ['clean']
      ]
    }
  },
  methods: {
async saveNews() {
  try {
    const auth = useAuthStore();
    const token = auth.token;
    if (!token) {
      console.warn('Missing token — cannot post news.');
      return;
    }

    const payload = {
      title: this.form.title,
      content: this.form.content,
      date: new Date().toISOString().slice(0, 10)
    };

    const config = {
      headers: {
        Authorization: `Bearer ${token}`
      }
    };

    if (this.editing) {
      await axios.put(`${import.meta.env.VITE_API_URL}/news/${this.form.id}`, payload, config);
    } else {
      await axios.post(`${import.meta.env.VITE_API_URL}/news`, payload, config);
    }

    await this.fetchNews();
    this.resetForm();
  } catch (err) {
    console.error('Failed to save news:', err.response?.data || err.message);
  }
  },

  editNews(item) {
    this.form = { ...item };
    this.editing = true;
  },

async deleteNews(id) {
  if (!id) return console.error('No news ID provided');

  const auth = useAuthStore();
  const token = auth.token;
  if (!token) {
    console.warn('Missing token — cannot delete news.');
    return;
  }

  try {
    await axios.delete(`${import.meta.env.VITE_API_URL}/news/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    await this.fetchNews();
  } catch (err) {
    console.error('Failed to delete news:', err.response?.data || err.message);
  }
  },

  cancelEdit() {
    this.resetForm();
  },

resetForm() {
  this.form = { id: null, title: "", content: "" };
  this.editing = false;
},
async fetchNews() {
  try {

        const auth = useAuthStore();
        const headers = {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Expires': '0'
        };

        if (auth.token) { // Use auth store here too
          headers.Authorization = `Bearer ${auth.token}`;
        }

    const response = await axios.get(`${import.meta.env.VITE_API_URL}/news`, { headers });
    console.log('Fetched news:', response.data);
    this.newsItems = Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    console.error('Failed to fetch news:', err.response?.data || err.message);
  }
}


  },
  mounted() {
    this.fetchNews();
  }
}
</script>

<style scoped>
/* Quill dark-theme overrides */
:deep(.ql-toolbar) {
  background: var(--s3);
  border-color: var(--border2);
  border-radius: 6px 6px 0 0;
}
:deep(.ql-toolbar .ql-stroke) { stroke: var(--muted); }
:deep(.ql-toolbar .ql-fill) { fill: var(--muted); }
:deep(.ql-toolbar .ql-picker) { color: var(--muted); }
:deep(.ql-container) {
  border-color: var(--border);
  font-family: inherit;
  font-size: 14px;
  border-radius: 0 0 6px 6px;
}
:deep(.ql-editor) {
  min-height: 160px;
  color: var(--text);
  background: var(--s2);
}
</style>