<template>
  <section class="system-admin">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">System<em>info</em></div>
        <div class="sec-subtitle">Systemstatus og teknisk informasjon. 9 9.9 ikke rør noe her.</div>
      </div>
    </div>
    <div class="g2">
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Systemstatus</span>
          <span class="badge b-green">Online</span>
        </div>
        <div class="panel-body">
          <div style="display:flex;flex-direction:column;gap:0;">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">Backend (Flask)</span>
              <span style="color:var(--green);font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:900;">Online</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">Database (Supabase)</span>
              <span style="color:var(--green);font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:900;">Online</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">Frontend (Vercel)</span>
              <span style="color:var(--green);font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:900;">Online</span>
            </div>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Versjonsinfo</span></div>
        <div class="panel-body">
          <div style="display:flex;flex-direction:column;gap:0;">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">App-versjon</span>
              <span style="color:var(--bright);font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:900;">v2.4.1</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">Stack</span>
              <span style="color:var(--text);font-size:13px;">Vue 3 · Flask · Supabase · pnpm</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--muted);font-size:12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">GDPR</span>
              <span style="color:var(--muted);font-size:13px;">compliant* (vi tror det)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  // Currently no props or emits needed for this placeholder tab
}
</script>

<style scoped>
/* SystemTab styles handled by admin.css */
</style>
