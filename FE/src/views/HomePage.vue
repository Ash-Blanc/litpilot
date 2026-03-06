<template>
  <div class="home-page container">
    <!-- ── Hero Section ──────────────────────────── -->
    <section class="hero animate-fade-in-up">
      <div class="hero-badge">🤖 Powered by TinyFish Web Agent + EMNLP 2025 Research</div>
      <h1>
        Your AI <span class="text-gradient">Research Autopilot</span>
      </h1>
      <p class="hero-sub">
        Describe your partial research session. LitPilot infers your goal and
        autonomously completes the literature review on live academic sites.
      </p>
    </section>

    <!-- ── Step Indicator ────────────────────────── -->
    <div class="steps-bar">
      <div class="step" :class="{ active: phase >= 0, done: phase > 0 }">
        <span class="step-num">1</span>
        <span class="step-label">Describe</span>
      </div>
      <div class="step-line" :class="{ active: phase > 0 }"></div>
      <div class="step" :class="{ active: phase >= 1, done: phase > 1 }">
        <span class="step-num">2</span>
        <span class="step-label">Review Intent</span>
      </div>
      <div class="step-line" :class="{ active: phase > 1 }"></div>
      <div class="step" :class="{ active: phase >= 2, done: phase >= 3 }">
        <span class="step-num">3</span>
        <span class="step-label">Execute & Report</span>
      </div>
    </div>

    <!-- ── Phase 0: Input ────────────────────────── -->
    <section class="phase-section glass-card" :class="{ collapsed: phase > 0 }">
      <InputForm
        v-model="description"
        :loading="inferring"
        @submit="handleInferIntent"
        @files-changed="handleFilesChanged"
      />
    </section>

    <!-- ── Phase 1: Intent Review ────────────────── -->
    <section v-if="phase >= 1" class="phase-section section-gap">
      <IntentReview
        :intent="intentData"
        :loading="executing"
        @execute="handleExecute"
      />
    </section>

    <!-- ── Phase 2: Execution Stream ─────────────── -->
    <section v-if="phase >= 2" class="phase-section section-gap">
      <ExecutionStream
        :events="streamEvents"
        :done="executionDone"
        :error="executionError"
      />
    </section>

    <!-- ── Phase 3: Final Report ─────────────────── -->
    <section v-if="phase >= 3" class="phase-section section-gap">
      <ReportDisplay :content="reportContent" />
    </section>

    <!-- ── Reset Button ──────────────────────────── -->
    <div v-if="phase >= 3" class="reset-area section-gap text-center">
      <button class="btn btn-secondary" @click="resetAll">
        🔄 Start New Research
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InputForm from '../components/InputForm.vue'
import IntentReview from '../components/IntentReview.vue'
import ExecutionStream from '../components/ExecutionStream.vue'
import ReportDisplay from '../components/ReportDisplay.vue'
import { inferIntent, executeResearch } from '../composables/useApi.js'

// ── State ──────────────────────────────
const phase = ref(0)          // 0=input, 1=review, 2=executing, 3=report
const description = ref('')
const screenshots = ref([])   // array of base64 strings
const inferring = ref(false)
const executing = ref(false)

const intentData = ref(null)
const streamEvents = ref([])
const executionDone = ref(false)
const executionError = ref('')
const reportContent = ref('')

// ── Handlers ───────────────────────────

function handleFilesChanged(base64Files) {
  screenshots.value = base64Files
}

async function handleInferIntent() {
  inferring.value = true
  try {
    const formattedImages = screenshots.value.map(base64 => ({ url: base64 }))
    const result = await inferIntent(description.value, formattedImages)
    intentData.value = result.intent
    phase.value = 1
  } catch (err) {
    alert('Error: ' + err.message)
  } finally {
    inferring.value = false
  }
}

function handleExecute(intent) {
  executing.value = true
  phase.value = 2
  streamEvents.value = []
  executionDone.value = false
  executionError.value = ''
  reportContent.value = ''

  executeResearch(intent, {
    onEvent(event) {
      streamEvents.value.push(event)
    },
    onDone(content) {
      reportContent.value = content
      executionDone.value = true
      executing.value = false
      phase.value = 3
    },
    onError(msg) {
      executionError.value = msg
      executionDone.value = true
      executing.value = false
    },
  })
}

function resetAll() {
  phase.value = 0
  description.value = ''
  intentData.value = null
  streamEvents.value = []
  executionDone.value = false
  executionError.value = ''
  reportContent.value = ''
}
</script>

<style scoped>
/* ── Hero ────────────────────────────── */
.hero {
  text-align: center;
  padding: 48px 0 16px;
}

.hero-badge {
  display: inline-block;
  padding: 6px 18px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--accent-text);
  margin-bottom: 20px;
}

.hero h1 {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
  line-height: 1.1;
}

.hero-sub {
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* ── Steps Bar ──────────────────────── */
.steps-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin: 40px 0 32px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted);
  transition: all var(--duration-normal) var(--ease-out);
}

.step.active {
  color: var(--accent-text);
}

.step.done {
  color: var(--success);
}

.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  font-size: 0.75rem;
  font-weight: 700;
  transition: all var(--duration-normal) var(--ease-out);
}

.step.active .step-num {
  background: rgba(6, 182, 212, 0.15);
  border-color: var(--accent-start);
  color: var(--accent-text);
}

.step.done .step-num {
  background: rgba(52, 211, 153, 0.15);
  border-color: var(--success);
  color: var(--success);
}

.step-line {
  flex: 0 0 40px;
  height: 2px;
  background: var(--border-subtle);
  transition: background var(--duration-slow);
}

.step-line.active {
  background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
}

/* ── Phases ──────────────────────────── */
.phase-section {
  transition: all var(--duration-slow) var(--ease-out);
}

.phase-section.glass-card {
  padding: 28px;
}

.phase-section.collapsed {
  opacity: 0.5;
  pointer-events: none;
  transform: scale(0.98);
}

/* ── Reset ───────────────────────────── */
.reset-area {
  padding-bottom: 40px;
}

/* ── Responsive ──────────────────────── */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }

  .hero-sub {
    font-size: 0.95rem;
  }

  .steps-bar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .step-line {
    display: none;
  }

  .step-label {
    display: none;
  }
}
</style>
