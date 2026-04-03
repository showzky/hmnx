<template>
  <section class="bedriftsmelding-admin">

    <!-- Floating image resize toolbar -->
    <div v-if="imageToolbarVisible" class="img-float-toolbar" :style="imageToolbarStyle">
      <button
        v-for="option in inlineImageSizeOptions"
        :key="option.value"
        type="button"
        class="ift-btn"
        :class="{ active: selectedEditorImageSize === option.value }"
        @mousedown.prevent="applyEditorImageSize(option.value)"
      >{{ option.label }}</button>
      <div class="ift-sep"></div>
      <button
        v-for="align in inlineImageAlignOptions"
        :key="align.value"
        type="button"
        class="ift-btn ift-align-btn"
        :class="{ active: selectedEditorImageAlign === align.value }"
        @mousedown.prevent="applyEditorImageAlign(align.value)"
        :title="align.title"
      >{{ align.icon }}</button>
    </div>
    <!-- Header -->
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Bedrifts<em>meldinger</em></div>
        <div class="sec-subtitle">Kunngjøringer og nyheter fra HMN. Vises på forsiden og Bedriftsmeldinger-siden.</div>
      </div>
    </div>

    <div class="bed-grid">
      <!-- ── LEFT: EDITOR ── -->
      <div class="bed-left">

        <!-- EDITOR PANEL -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">Skriv melding</span>
            <div v-if="editing" class="editing-badge">
              <span class="editing-dot"></span>Redigerer: {{ form.ref }}
            </div>
          </div>
          <div class="panel-body">
            <input
              ref="coverImageInput"
              class="file-input-hidden"
              type="file"
              accept="image/*"
              @change="handleCoverImageSelected"
            />
            <input
              ref="inlineImageInput"
              class="file-input-hidden"
              type="file"
              accept="image/*"
              @change="handleInlineImageSelected"
            />

            <!-- TITLE -->
            <div class="form-group">
              <label class="form-label">Tittel</label>
              <input class="form-input" v-model="form.title" placeholder="Tittel på meldingen..." />
            </div>

            <!-- RICH TEXT -->
            <div class="form-group">
              <div class="form-label-row">
                <label class="form-label">Innhold</label>
                <div class="callout-btns">
                  <button type="button" class="callout-btn callout-btn-red" @click="insertCallout" title="Sett inn rød § callout-boks">
                    § Callout
                  </button>
                  <button type="button" class="callout-btn callout-btn-info" @click="insertInfoCallout" title="Sett inn blå info-boks">
                    ℹ Info
                  </button>
                </div>
              </div>
              <quill-editor
                ref="quillEditor"
                v-model:content="form.content"
                content-type="html"
                :toolbar="toolbarOptions"
                @ready="onEditorReady"
                style="background:var(--s2);border:1px solid var(--border2);border-radius:6px;color:var(--text);"
              />
            </div>

            <div class="form-group">
              <div class="form-label-row">
                <label class="form-label">Forsidebilde</label>
              </div>

              <div class="cover-image-card" :class="{ uploading: uploadingCoverImage, empty: !form.image_url }">
                <template v-if="form.image_url">
                  <!-- Crop preview -->
                  <div
                    class="crop-preview-wrap"
                    @mousedown="startCropDrag"
                    title="Dra opp/ned for å justere utsnitt"
                  >
                    <img
                      :src="form.image_url"
                      :alt="form.image_alt || form.title || 'Bedriftsmelding bilde'"
                      class="crop-preview-img"
                      :style="{ objectPosition: form.image_position || 'center center' }"
                      draggable="false"
                    />
                    <div class="crop-preview-hint">↕ Dra for å justere utsnitt</div>
                  </div>
                  <div class="cover-image-meta">
                    <label class="form-label">Alt-tekst</label>
                    <input
                      class="form-input"
                      v-model="form.image_alt"
                      placeholder="Kort beskrivelse av bildet (valgfritt)"
                    />
                    <div class="cover-image-actions">
                      <button type="button" class="btn btn-cyan btn-sm" @click="triggerCoverImageUpload" :disabled="uploadingCoverImage">
                        {{ uploadingCoverImage ? 'Laster opp...' : 'Bytt bilde' }}
                      </button>
                      <button type="button" class="btn btn-ghost btn-sm" @click="removeCoverImage">Fjern bilde</button>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="cover-image-empty">
                    <div class="cover-image-empty-title">Ingen forsidebilde valgt</div>
                    <div class="cover-image-empty-sub">
                      Bruk ett frivillig forsidebilde for kort, detaljside og forsiden. Bilder inne i teksten styres separat fra editoren.
                    </div>
                    <button type="button" class="btn btn-ghost btn-sm" @click="triggerCoverImageUpload" :disabled="uploadingCoverImage">
                      {{ uploadingCoverImage ? 'Laster opp...' : 'Velg bilde' }}
                    </button>
                  </div>
                </template>
              </div>
            </div>


            <!-- KATEGORI + REF -->
            <div class="form-grid" style="margin-bottom:14px;">
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Kategori</label>
                <select class="form-select" v-model="form.category">
                  <option value="oppdatering">Oppdatering</option>
                  <option value="kaos">Kaos</option>
                  <option value="hendelse">Hendelse</option>
                  <option value="viktig">Viktig</option>
                  <option value="thomas-relatert">Thomas-relatert</option>
                </select>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Referanse (auto)</label>
                <input class="form-input" :value="form.ref || nextRef" readonly style="opacity:0.55;" />
              </div>
            </div>

            <!-- RASK TAG CHIPS -->
            <div class="form-group">
              <label class="form-label">Rask tag</label>
              <div class="tag-row">
                <div
                  v-for="t in tags" :key="t.value"
                  class="tag-chip"
                  :class="[t.cls, { selected: form.tag === t.value }]"
                  @click="form.tag = form.tag === t.value ? null : t.value"
                >
                  <span class="tc-dot"></span>{{ t.label }}
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- PUBLISERINGSVALG -->
        <div class="panel" style="margin-top:16px;">
          <div class="panel-head"><span class="panel-title">Publiseringsvalg</span></div>
          <div class="panel-body" style="padding:14px 16px;">

            <div class="toggle-row">
              <div class="tr-info">
                <div class="tr-label">📌 Fest til forsiden</div>
                <div class="tr-sub">Vises som featured melding øverst på forsiden. Kun én kan være festet om gangen.</div>
              </div>
              <label class="hmn-toggle">
                <input type="checkbox" v-model="form.pinned" />
                <div class="toggle-track" :class="{ 'track-gold': form.pinned }"></div>
                <div class="toggle-thumb" :class="{ 'thumb-gold': form.pinned }"></div>
              </label>
            </div>

            <div class="toggle-row" style="margin-bottom:0;">
              <div class="tr-info">
                <div class="tr-label">🔔 Varsle brukere</div>
                <div class="tr-sub">Sender notifikasjon til alle registrerte pasienter.</div>
              </div>
              <label class="hmn-toggle">
                <input type="checkbox" v-model="form.notify_users" />
                <div class="toggle-track" :class="{ 'track-cyan': form.notify_users }"></div>
                <div class="toggle-thumb" :class="{ 'thumb-cyan': form.notify_users }"></div>
              </label>
            </div>

          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div style="display:flex;gap:8px;margin-top:14px;">
          <button class="btn btn-red" @click="savemelding">
            {{ editing ? 'Oppdater melding' : 'Publiser melding' }}
          </button>
          <button v-if="editing" class="btn btn-ghost" @click="cancelEdit">Avbryt redigering</button>
        </div>

        <div v-if="statusMsg" class="status-msg" :class="{ success: statusOk, error: !statusOk }">
          {{ statusMsg }}
        </div>

      </div>

      <!-- ── RIGHT: FEED ── -->
      <div class="bed-right">

        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">Publiserte meldinger</span>
            <span class="panel-meta">{{ meldinger.length }} totalt</span>
          </div>

          <!-- FILTERS -->
          <div style="padding:10px 12px 4px;">
            <div class="feed-filters">
              <div
                v-for="f in filters" :key="f.value"
                class="ff"
                :class="{ active: activeFilter === f.value }"
                @click="activeFilter = f.value"
              >{{ f.label }}</div>
            </div>
          </div>

          <!-- MELDING LIST -->
          <div class="melding-list" style="padding:0 8px 12px;">
            <div
              v-for="m in filteredMeldinger" :key="m.id"
              class="melding-card"
              :class="{ pinned: m.pinned, editing: editing && form.id === m.id }"
            >
              <div class="mc-head">
                <span v-if="m.pinned" class="mc-pin-icon">📌</span>
                <span class="mc-tag badge" :class="tagBadgeClass(m.category)">{{ categoryLabel(m.category) }}</span>
                <span class="mc-ref">{{ m.ref }}</span>
                <span class="mc-date">{{ formatDate(m.created_at) }}</span>
              </div>
              <div class="mc-body">
                <div class="mc-title">{{ m.title }}</div>
                <div class="mc-preview" v-html="stripHtml(m.content)"></div>
                <img
                  v-if="m.image_url"
                  :src="m.image_url"
                  :alt="m.image_alt || m.title"
                  class="mc-image"
                />
              </div>
              <div class="mc-foot">
                <button class="btn btn-cyan btn-sm" @click="editMelding(m)">Rediger</button>
                <button class="btn btn-sm" :class="m.pinned ? 'btn-gold' : 'btn-ghost'" @click="togglePin(m)">
                  {{ m.pinned ? 'Fjern pin' : 'Pin' }}
                </button>
                <button class="btn btn-danger btn-sm" style="margin-left:auto;" @click="deleteMelding(m.id)">Slett</button>
              </div>
            </div>

            <div v-if="filteredMeldinger.length === 0" class="feed-empty">
              Ingen meldinger funnet.
            </div>
          </div>
        </div>

        <!-- STATISTIKK -->
        <div class="panel" style="margin-top:14px;">
          <div class="panel-head"><span class="panel-title">Statistikk</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;">
            <div style="padding:14px 16px;border-right:1px solid var(--border);text-align:center;">
              <div class="stat-big cyan">{{ meldinger.length }}</div>
              <div class="stat-lbl">Publisert</div>
            </div>
            <div style="padding:14px 16px;text-align:center;">
              <div class="stat-big gold">{{ meldinger.filter(m => m.pinned).length }}</div>
              <div class="stat-lbl">Festet</div>
            </div>
          </div>
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

const createEmptyForm = () => ({
  id: null,
  ref: null,
  title: '',
  content: '',
  image_url: '',
  image_alt: '',
  image_position: 'center center',
  category: 'oppdatering',
  tag: null,
  pinned: false,
  notify_users: false,
});

export default {
  components: { QuillEditor },

  data() {
    return {
      meldinger: [],
      editing: false,
      form: createEmptyForm(),
      statusMsg: '',
      statusOk: true,
      editorInstance: null,
      hasBoundImageHandler: false,
      uploadingCoverImage: false,
      uploadingInlineImage: false,
      selectedEditorImage: null,
      selectedEditorImageSize: 'wide',
      selectedEditorImageAlign: 'center',
      imageToolbarVisible: false,
      imageToolbarStyle: {},
      activeFilter: 'alle',
      _cropDrag: null,
      inlineImageSizeOptions: [
        { value: 'small', label: 'Liten' },
        { value: 'medium', label: 'Medium' },
        { value: 'wide', label: 'Bred' },
        { value: 'full', label: 'Full bredde' },
      ],
      inlineImageAlignOptions: [
        { value: 'left',   icon: '←', title: 'Venstrestill' },
        { value: 'center', icon: '⊟', title: 'Midtstill' },
        { value: 'right',  icon: '→', title: 'Høyrestill' },
      ],
      toolbarOptions: [
        ['bold', 'italic', 'underline'],
        [{ header: [1, 2, false] }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        ['clean'],
      ],
      tags: [
        { value: 'kaos',           label: 'Kaos',           cls: 't-kaos' },
        { value: 'hendelse',       label: 'Hendelse',       cls: 't-hendelse' },
        { value: 'oppdatering',    label: 'Oppdatering',    cls: 't-oppdatering' },
        { value: 'viktig',         label: 'Viktig',         cls: 't-viktig' },
        { value: 'thomas-relatert',label: 'Sporadisk',cls: 't-sporadisk' },
      ],
      filters: [
        { value: 'alle',           label: 'Alle' },
        { value: 'festet',         label: 'Festet' },
        { value: 'oppdatering',    label: 'Oppdatering' },
        { value: 'kaos',           label: 'Kaos' },
        { value: 'thomas-relatert',label: 'Sporadisk' },
      ],
    };
  },

  computed: {
    nextRef() {
      return `HMN-MSG-${String(this.meldinger.length + 1).padStart(3, '0')}`;
    },
    filteredMeldinger() {
      if (this.activeFilter === 'alle') return this.meldinger;
      if (this.activeFilter === 'festet') return this.meldinger.filter(m => m.pinned);
      return this.meldinger.filter(m => m.category === this.activeFilter || m.tag === this.activeFilter);
    },
  },

  methods: {
    emptyForm() {
      return createEmptyForm();
    },

    authHeader() {
      const auth = useAuthStore();
      return { Authorization: `Bearer ${auth.token}` };
    },

    onEditorReady(quill) {
      const editor = quill || this.$refs.quillEditor?.getQuill?.();
      if (!editor) return;

      this.editorInstance = editor;
      if (this.hasBoundImageHandler) return;

      const toolbar = editor.getModule('toolbar');
      toolbar?.addHandler('image', () => this.triggerInlineImageUpload());
      editor.root.addEventListener('click', this.handleEditorRootClick);
      this.hasBoundImageHandler = true;
    },

    inlineImageSizeLabel(size) {
      return this.inlineImageSizeOptions.find((option) => option.value === size)?.label || 'Bred';
    },

    handleEditorRootClick(event) {
      const target = event.target;
      if (target instanceof HTMLImageElement) {
        this.selectedEditorImage = target;
        this.selectedEditorImageSize = this.detectInlineImageSize(target);
        this.selectedEditorImageAlign = this.detectInlineImageAlign(target);
        const rect = target.getBoundingClientRect();
        this.imageToolbarStyle = {
          position: 'fixed',
          top: Math.max(8, rect.top - 44) + 'px',
          left: (rect.left + rect.width / 2) + 'px',
          transform: 'translateX(-50%)',
          zIndex: 9999,
        };
        this.imageToolbarVisible = true;
        return;
      }
      this.selectedEditorImage = null;
      this.imageToolbarVisible = false;
      this.selectedEditorImageSize = 'wide';
      this.selectedEditorImageAlign = 'center';
    },

    detectInlineImageSize(imageEl) {
      if (!(imageEl instanceof HTMLImageElement)) return 'wide';
      if (imageEl.classList.contains('inline-image--small')) return 'small';
      if (imageEl.classList.contains('inline-image--medium')) return 'medium';
      if (imageEl.classList.contains('inline-image--full')) return 'full';
      return 'wide';
    },

    setInlineImageSize(imageEl, size) {
      if (!(imageEl instanceof HTMLImageElement)) return;
      imageEl.classList.add('editor-inline-image');
      imageEl.classList.remove(
        'inline-image--small',
        'inline-image--medium',
        'inline-image--wide',
        'inline-image--full'
      );
      imageEl.classList.add(`inline-image--${size}`);
      imageEl.setAttribute('data-size', size);
      imageEl.removeAttribute('width');
      imageEl.removeAttribute('height');
      imageEl.style.width = '';
      imageEl.style.maxWidth = '';
    },

    applyEditorImageSize(size) {
      if (!this.selectedEditorImage) {
        this.showStatus('Klikk på et bilde i editoren først.', false);
        return;
      }
      this.setInlineImageSize(this.selectedEditorImage, size);
      this.selectedEditorImageSize = size;
      this.form.content = this.editorInstance?.root?.innerHTML || this.form.content;
    },

    detectInlineImageAlign(imageEl) {
      if (!(imageEl instanceof HTMLImageElement)) return 'center';
      if (imageEl.classList.contains('inline-image--align-left')) return 'left';
      if (imageEl.classList.contains('inline-image--align-right')) return 'right';
      return 'center';
    },

    setInlineImageAlign(imageEl, align) {
      if (!(imageEl instanceof HTMLImageElement)) return;
      imageEl.classList.remove('inline-image--align-left', 'inline-image--align-center', 'inline-image--align-right');
      imageEl.classList.add(`inline-image--align-${align}`);
    },

    applyEditorImageAlign(align) {
      if (!this.selectedEditorImage) return;
      this.setInlineImageAlign(this.selectedEditorImage, align);
      this.selectedEditorImageAlign = align;
      this.form.content = this.editorInstance?.root?.innerHTML || this.form.content;
    },

    insertCallout() {
      this._insertCalloutHtml('⚠️', 'Viktig');
    },

    insertInfoCallout() {
      this._insertCalloutHtml('ℹ️', 'Info');
    },

    _insertCalloutHtml(icon, label) {
      const quill = this.$refs.quillEditor?.getQuill?.();
      if (!quill) return;
      const range = quill.getSelection(true);
      const selectedText = range?.length ? quill.getText(range.index, range.length) : '';
      const html = `<p>${icon} <strong>${label}:</strong> ${selectedText || 'Skriv tekst her...'}</p><p><br></p>`;
      if (range?.length) {
        quill.deleteText(range.index, range.length);
        quill.clipboard.dangerouslyPasteHTML(range.index, html);
      } else {
        const idx = range ? range.index : quill.getLength();
        quill.clipboard.dangerouslyPasteHTML(idx, html);
      }
    },

    async uploadBedriftsmeldingImage(file, kind = 'content') {
      if (!file?.type?.startsWith('image/')) {
        throw new Error('Bare bildefiler er tillatt.');
      }

      const formData = new FormData();
      formData.append('image', file);
      formData.append('kind', kind);

      const res = await axios.post(
        `${import.meta.env.VITE_API_URL}/bedriftsmeldinger/upload-image`,
        formData,
        { headers: { ...this.authHeader(), 'Content-Type': 'multipart/form-data' } }
      );

      return res.data?.url;
    },

    triggerCoverImageUpload() {
      if (this.uploadingCoverImage) return;
      this.$refs.coverImageInput?.click();
    },

    async handleCoverImageSelected(event) {
      const file = event.target.files?.[0];
      event.target.value = '';
      if (!file) return;

      this.uploadingCoverImage = true;
      try {
        const imageUrl = await this.uploadBedriftsmeldingImage(file, 'cover');
        this.form.image_url = imageUrl || '';
        if (!this.form.image_alt) {
          this.form.image_alt = this.form.title ? `Illustrasjon til ${this.form.title}` : '';
        }
        this.showStatus('Forsidebildet ble lastet opp.', true);
      } catch (err) {
        this.showStatus(err?.response?.data?.message || err.message || 'Kunne ikke laste opp bildet.', false);
      } finally {
        this.uploadingCoverImage = false;
      }
    },

    removeCoverImage() {
      this.form.image_url = '';
      this.form.image_alt = '';
      this.form.image_position = 'center center';
    },

    startCropDrag(e) {
      const startY = e.clientY;
      // Parse current Y position (0–100)
      const current = this.form.image_position || 'center center';
      const parts = current.split(' ');
      const startPct = parseFloat(parts[1]) || 50;

      const onMove = (ev) => {
        const wrap = e.currentTarget || e.target.closest('.crop-preview-wrap');
        const wrapH = wrap ? wrap.offsetHeight : 200;
        const delta = ev.clientY - startY;
        // Moving down → image shifts down → object-position Y increases
        const newPct = Math.min(100, Math.max(0, startPct + (delta / wrapH) * 100));
        this.form.image_position = `center ${Math.round(newPct)}%`;
      };
      const onUp = () => {
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
      };
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
      e.preventDefault();
    },

    triggerInlineImageUpload() {
      if (this.uploadingInlineImage) return;
      this.onEditorReady();
      if (!this.editorInstance) {
        this.showStatus('Editoren er ikke klar ennå.', false);
        return;
      }
      this.$refs.inlineImageInput?.click();
    },

    async handleInlineImageSelected(event) {
      const file = event.target.files?.[0];
      event.target.value = '';
      if (!file) return;

      this.onEditorReady();
      if (!this.editorInstance) {
        this.showStatus('Editoren er ikke klar ennå.', false);
        return;
      }

      this.uploadingInlineImage = true;
      try {
        const imageUrl = await this.uploadBedriftsmeldingImage(file, 'content');
        const range = this.editorInstance.getSelection(true);
        const index = typeof range?.index === 'number' ? range.index : this.editorInstance.getLength();
        this.editorInstance.insertEmbed(index, 'image', imageUrl, 'user');
        this.$nextTick(() => {
          const images = Array.from(this.editorInstance.root.querySelectorAll(`img[src="${imageUrl}"]`));
          const insertedImage = images[images.length - 1] || null;
          if (insertedImage) {
            this.setInlineImageSize(insertedImage, 'wide');
            this.selectedEditorImage = insertedImage;
            this.selectedEditorImageSize = 'wide';
          }
          this.form.content = this.editorInstance?.root?.innerHTML || this.form.content;
        });
        this.editorInstance.setSelection(index + 1, 0);
        this.showStatus('Bildet ble satt inn i innholdet.', true);
      } catch (err) {
        this.showStatus(err?.response?.data?.message || err.message || 'Kunne ikke sette inn bildet.', false);
      } finally {
        this.uploadingInlineImage = false;
      }
    },

    async fetchMeldinger() {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger`);
        this.meldinger = Array.isArray(res.data) ? res.data : [];
      } catch (err) {
        console.error('Failed to fetch bedriftsmeldinger:', err);
      }
    },

    async savemelding() {
      if (!this.form.title.trim() || !this.form.content) {
        this.showStatus('Tittel og innhold er påkrevd.', false);
        return;
      }
      try {
        const payload = { ...this.form };
        if (this.editing) {
          await axios.put(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${this.form.id}`, payload, { headers: this.authHeader() });
          this.showStatus('Melding oppdatert!', true);
        } else {
          await axios.post(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger`, payload, { headers: this.authHeader() });
          this.showStatus('Melding publisert!', true);
        }
        await this.fetchMeldinger();
        this.resetForm();
      } catch (err) {
        this.showStatus('Noe gikk galt. Prøv igjen.', false);
        console.error(err);
      }
    },

    editMelding(m) {
      this.form = {
        ...this.emptyForm(),
        ...m,
        image_url: m.image_url || '',
        image_alt: m.image_alt || '',
        image_position: m.image_position || 'center center',
      };
      this.editing = true;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    cancelEdit() {
      this.resetForm();
    },

    async deleteMelding(id) {
      if (!confirm('Slett denne meldingen?')) return;
      try {
        await axios.delete(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${id}`, { headers: this.authHeader() });
        await this.fetchMeldinger();
      } catch (err) {
        console.error('Delete failed:', err);
      }
    },

    async togglePin(m) {
      try {
        await axios.put(
          `${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${m.id}`,
          { ...m, pinned: !m.pinned },
          { headers: this.authHeader() }
        );
        await this.fetchMeldinger();
      } catch (err) {
        console.error('Toggle pin failed:', err);
      }
    },

    resetForm() {
      this.form = this.emptyForm();
      this.editing = false;
      this.selectedEditorImage = null;
      this.selectedEditorImageSize = 'wide';
      this.selectedEditorImageAlign = 'center';
    },

    showStatus(msg, ok) {
      this.statusMsg = msg;
      this.statusOk = ok;
      setTimeout(() => { this.statusMsg = ''; }, 3500);
    },

    tagBadgeClass(cat) {
      const map = {
        oppdatering: 'b-green',
        kaos: 'b-red',
        hendelse: 'b-cyan',
        viktig: 'b-gold',
        'thomas-relatert': 'b-purple',
      };
      return map[cat] || 'b-muted';
    },

    categoryLabel(cat) {
      const map = {
        oppdatering: 'Oppdatering',
        kaos: 'Kaos',
        hendelse: 'Hendelse',
        viktig: 'Viktig',
        'thomas-relatert': 'Sporadisk',
      };
      return map[cat] || cat;
    },

    formatDate(iso) {
      if (!iso) return '';
      const d = new Date(iso);
      return d.toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' });
    },

    stripHtml(html) {
      if (!html) return '';
      const tmp = document.createElement('div');
      tmp.innerHTML = html;
      const text = tmp.textContent || tmp.innerText || '';
      return text.length > 80 ? text.slice(0, 80) + '…' : text;
    },
  },

  mounted() {
    this.fetchMeldinger();
    this.$nextTick(() => this.onEditorReady());
  },

  beforeUnmount() {
    this.editorInstance?.root?.removeEventListener?.('click', this.handleEditorRootClick);
  },
};
</script>

<style scoped>
.file-input-hidden {
  display: none;
}

/* Label row with callout buttons */
.form-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.form-label-row .form-label {
  margin-bottom: 0;
}
.callout-btns {
  display: flex;
  gap: 6px;
}
.callout-btn {
  font-size: 11px;
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: 0.06em;
  border-radius: 4px;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.15s;
  text-transform: uppercase;
}
.callout-btn-red {
  color: var(--red2);
  background: rgba(200,16,46,0.08);
  border: 1px solid rgba(200,16,46,0.2);
}
.callout-btn-red:hover {
  background: rgba(200,16,46,0.14);
  border-color: rgba(200,16,46,0.35);
}
.callout-btn-info {
  color: var(--cyan);
  background: rgba(0,184,208,0.07);
  border: 1px solid rgba(0,184,208,0.2);
}
.callout-btn-info:hover {
  background: rgba(0,184,208,0.13);
  border-color: rgba(0,184,208,0.35);
}

/* Layout */
.bed-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 18px;
  align-items: start;
}
.bed-left { display: flex; flex-direction: column; }
.bed-right { display: flex; flex-direction: column; }

/* Editing badge */
.editing-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 4px;
  background: rgba(0,184,208,0.1); border: 1px solid rgba(0,184,208,0.22);
  color: var(--cyan); font-size: 10px;
  font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
}
.editing-dot {
  width: 6px; height: 6px; background: var(--cyan); border-radius: 50%;
  box-shadow: 0 0 6px var(--cyan); animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* Tag chips */
.tag-row { display: flex; gap: 7px; flex-wrap: wrap; }
.tag-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 600;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
  cursor: pointer; border: 1px solid; transition: all 0.15s; user-select: none;
}
.tag-chip:hover { transform: translateY(-1px); }
.tag-chip.selected { box-shadow: 0 0 0 2px currentColor; }
.tc-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.t-kaos         { background:rgba(200,16,46,0.1);  color:var(--red2);  border-color:rgba(200,16,46,0.25); }
.t-kaos .tc-dot         { background:var(--red2); }
.t-hendelse     { background:rgba(0,184,208,0.1);  color:var(--cyan);  border-color:rgba(0,184,208,0.25); }
.t-hendelse .tc-dot     { background:var(--cyan); }
.t-oppdatering  { background:rgba(40,184,96,0.1);  color:var(--green); border-color:rgba(40,184,96,0.25); }
.t-oppdatering .tc-dot  { background:var(--green); }
.t-viktig       { background:rgba(216,152,32,0.1); color:var(--gold);  border-color:rgba(216,152,32,0.25); }
.t-viktig .tc-dot       { background:var(--gold); }
.t-sporadisk       { background:rgba(112,80,216,0.1); color:#9070f0;      border-color:rgba(112,80,216,0.25); }
.t-sporadisk .tc-dot       { background:#9070f0; }

/* Toggle */
.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; background: rgba(255,255,255,0.02);
  border: 1px solid var(--border); border-radius: 7px; margin-bottom: 14px;
}
.tr-info { flex: 1; }
.tr-label { font-size: 13px; color: var(--bright); font-family: 'Barlow', sans-serif; font-weight: 500; margin-bottom: 2px; }
.tr-sub { font-size: 11px; color: var(--muted); font-family: 'Barlow', sans-serif; }
.hmn-toggle { position: relative; width: 40px; height: 22px; cursor: pointer; flex-shrink: 0; }
.hmn-toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-track {
  position: absolute; inset: 0; border-radius: 11px;
  background: rgba(255,255,255,0.08); border: 1px solid var(--border2); transition: all 0.2s;
}
.toggle-track.track-gold { background: rgba(216,152,32,0.3); border-color: rgba(216,152,32,0.5); }
.toggle-track.track-cyan { background: rgba(0,184,208,0.25); border-color: rgba(0,184,208,0.45); }
.toggle-thumb {
  position: absolute; top: 3px; left: 3px;
  width: 14px; height: 14px; border-radius: 50%; background: var(--muted); transition: all 0.2s; pointer-events: none;
}
.toggle-thumb.thumb-gold { left: 21px; background: var(--gold); box-shadow: 0 0 6px rgba(216,152,32,0.5); }
.toggle-thumb.thumb-cyan { left: 21px; background: var(--cyan); box-shadow: 0 0 6px rgba(0,184,208,0.5); }

/* Cover image */
.cover-image-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
}
.cover-image-card.uploading {
  border-color: rgba(0,184,208,0.3);
}
.cover-image-card.empty {
  display: block;
}
.crop-preview-wrap {
  width: 200px;
  height: 128px;
  flex-shrink: 0;
  border-radius: 6px;
  border: 1px solid var(--border2);
  background: rgba(255,255,255,0.03);
  overflow: hidden;
  position: relative;
  cursor: ns-resize;
  user-select: none;
}
.crop-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  pointer-events: none;
}
.crop-preview-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.55);
  color: rgba(255,255,255,0.7);
  font-size: 10px;
  text-align: center;
  padding: 3px 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
}
.crop-preview-wrap:hover .crop-preview-hint {
  opacity: 1;
}
.cover-image-meta {
  flex: 1;
  display: grid;
  gap: 8px;
  min-width: 0;
}
.cover-image-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.cover-image-empty {
  display: grid;
  gap: 10px;
}
.cover-image-empty-title {
  color: var(--bright);
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.cover-image-empty-sub {
  color: var(--text-muted);
  font-family: 'Barlow', sans-serif;
  font-size: 12px;
  line-height: 1.6;
}

.inline-image-state {
  font-size: 11px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
}
.inline-image-state.active {
  color: var(--cyan);
}
.inline-image-size-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.size-chip {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--border2);
  background: rgba(255,255,255,0.03);
  color: var(--muted);
  font-size: 11px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}
.size-chip:hover:not(:disabled) {
  color: var(--text);
  border-color: rgba(0,184,208,0.25);
}
.size-chip.active {
  color: var(--cyan);
  background: rgba(0,184,208,0.08);
  border-color: rgba(0,184,208,0.28);
}
.size-chip:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Feed filters */
.feed-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.ff {
  padding: 5px 12px; border-radius: 5px; font-size: 11px; font-weight: 600;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
  cursor: pointer; border: 1px solid var(--border); background: rgba(255,255,255,0.03); color: var(--muted); transition: all 0.15s;
}
.ff:hover { color: var(--text); border-color: var(--border2); }
.ff.active { background: rgba(0,184,208,0.08); border-color: rgba(0,184,208,0.2); color: var(--cyan); }

/* Melding cards */
.melding-list { display: flex; flex-direction: column; gap: 8px; }
.melding-card {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden; transition: all 0.2s;
}
.melding-card:hover { border-color: var(--border2); }
.melding-card.pinned { border-color: rgba(216,152,32,0.3); background: rgba(216,152,32,0.04); }
.melding-card.editing { border-color: rgba(0,184,208,0.3); background: rgba(0,184,208,0.04); }
.mc-head {
  padding: 10px 14px; display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border);
}
.mc-pin-icon { font-size: 12px; color: var(--gold); flex-shrink: 0; }
.mc-tag { flex-shrink: 0; }
.mc-ref { font-size: 10px; color: var(--muted); font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; flex: 1; }
.mc-date { font-size: 10px; color: var(--muted); flex-shrink: 0; }
.mc-body { padding: 10px 14px; }
.mc-title { font-size: 14px; font-weight: 600; color: var(--bright); font-family: 'Barlow', sans-serif; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mc-preview { font-size: 12px; color: rgba(255,255,255,0.35); font-family: 'Barlow', sans-serif; line-height: 1.55; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mc-image {
  width: 100%;
  height: 96px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border);
  margin-top: 10px;
}
.mc-foot {
  padding: 8px 14px; border-top: 1px solid var(--border);
  background: rgba(0,0,0,0.15); display: flex; align-items: center; gap: 6px;
}
.feed-empty { padding: 32px; text-align: center; color: var(--muted); font-size: 13px; font-family: 'Barlow', sans-serif; font-style: italic; }

/* Stat */
.stat-big { font-family: 'Barlow Condensed', sans-serif; font-size: 24px; font-weight: 900; line-height: 1; }
.stat-big.cyan { color: var(--cyan); }
.stat-big.gold { color: var(--gold); }
.stat-lbl { font-size: 10px; color: var(--muted); margin-top: 3px; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; letter-spacing: 0.07em; }

/* Status message */
.status-msg { margin-top: 10px; padding: 8px 12px; border-radius: 6px; font-size: 13px; font-family: 'Barlow', sans-serif; }
.status-msg.success { background: rgba(40,184,96,0.1); color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.status-msg.error { background: rgba(200,16,46,0.1); color: var(--red2); border: 1px solid rgba(200,16,46,0.2); }

/* Quill dark overrides */
:deep(.ql-toolbar) { background: var(--s3); border-color: var(--border2); border-radius: 6px 6px 0 0; }
:deep(.ql-toolbar .ql-stroke) { stroke: var(--muted); }
:deep(.ql-toolbar .ql-fill) { fill: var(--muted); }
:deep(.ql-toolbar .ql-picker) { color: var(--muted); }
:deep(.ql-container) { border-color: var(--border2); font-family: inherit; font-size: 14px; border-radius: 0 0 6px 6px; }
:deep(.ql-editor) { min-height: 140px; color: var(--text); background: var(--s2); }
:deep(.ql-editor img) { max-width: 100%; border-radius: 8px; }
.img-float-toolbar {
  display: flex;
  gap: 4px;
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 5px 7px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  pointer-events: all;
}
.img-float-toolbar::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--border2);
}
.ift-btn {
  padding: 4px 10px;
  border-radius: 5px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--muted);
  font-size: 11px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.12s;
}
.ift-btn:hover { background: rgba(255,255,255,0.06); color: var(--text); }
.ift-btn.active { background: rgba(0,184,208,0.12); color: var(--cyan); border-color: rgba(0,184,208,0.25); }
.ift-align-btn { font-size: 13px; padding: 4px 8px; }
.ift-sep { width: 1px; background: var(--border2); margin: 2px 3px; }

:deep(.ql-editor img.editor-inline-image) {
  display: block;
  margin: 18px auto;
  border: 1px solid var(--border2);
  box-shadow: 0 12px 28px rgba(0,0,0,0.2);
}
:deep(.ql-editor img.inline-image--small) { width: min(220px, 100%); }
:deep(.ql-editor img.inline-image--medium) { width: min(360px, 100%); }
:deep(.ql-editor img.inline-image--wide) { width: min(640px, 100%); }
:deep(.ql-editor img.inline-image--full) { width: 100%; }
:deep(.ql-editor img.inline-image--align-left) { margin-left: 0; margin-right: auto; }
:deep(.ql-editor img.inline-image--align-center) { margin-left: auto; margin-right: auto; }
:deep(.ql-editor img.inline-image--align-right) { margin-left: auto; margin-right: 0; }
</style>
