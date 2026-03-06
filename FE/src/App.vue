<template>
  <div class="app-shell">
    <!-- ── Navigation ──────────────────────────────── -->
    <nav class="nav">
      <div class="nav-inner container">
        <a href="/" class="logo" aria-label="LitPilot Home">
          <span class="logo-icon">📚</span>
          <span class="logo-text">Lit<span class="text-gradient">Pilot</span></span>
        </a>
        <div class="nav-links">
          <a href="https://github.com" target="_blank" class="btn btn-ghost" aria-label="GitHub">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
          </a>
        </div>
      </div>
    </nav>

    <!-- ── Main Content ────────────────────────────── -->
    <main class="main">
      <router-view />
    </main>

    <!-- ── Footer ──────────────────────────────────── -->
    <footer class="footer">
      <div class="container">
        <p>Built with ♥ for the TinyFish $2M Pre-Accelerator Hackathon 2026</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// App shell — no logic needed
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Nav ─────────────────────────────── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10, 14, 26, 0.85);
  backdrop-filter: blur(16px) saturate(1.5);
  -webkit-backdrop-filter: blur(16px) saturate(1.5);
  border-bottom: 1px solid var(--border-subtle);
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Main ────────────────────────────── */
.main {
  flex: 1;
  padding-top: 32px;
  padding-bottom: 80px;
}

/* ── Footer ──────────────────────────── */
.footer {
  border-top: 1px solid var(--border-subtle);
  padding: 24px 0;
  text-align: center;
}

.footer p {
  font-size: 0.85rem;
  color: var(--text-muted);
}
</style>
