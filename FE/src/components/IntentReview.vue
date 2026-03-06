<template>
  <div class="intent-review glass-card animate-fade-in-up" v-if="intent">
    <div class="review-header">
      <div class="review-badge">
        <span class="badge-dot"></span>
        Intent Inferred
      </div>
      <span class="confidence" v-if="intent.confidence">
        {{ Math.round(intent.confidence * 100) }}% confidence
      </span>
    </div>

    <!-- Inferred Goal -->
    <div class="goal-section">
      <h3>Research Goal</h3>
      <div v-if="!editing" class="goal-display">
        <p class="goal-text">{{ intent.inferred_intent }}</p>
        <button class="btn btn-ghost" @click="startEditing">✏️ Edit</button>
      </div>
      <div v-else class="goal-edit">
        <textarea
          class="input"
          v-model="editedIntent"
          rows="3"
        ></textarea>
        <div class="edit-actions">
          <button class="btn btn-ghost" @click="cancelEdit">Cancel</button>
          <button class="btn btn-secondary" @click="saveEdit">Save</button>
        </div>
      </div>
    </div>

    <!-- Key Topics -->
    <div class="topics-section" v-if="intent.key_topics?.length">
      <h4>Key Topics</h4>
      <div class="topic-pills">
        <span class="pill" v-for="topic in intent.key_topics" :key="topic">
          {{ topic }}
        </span>
      </div>
    </div>

    <!-- Scope Details -->
    <div class="scope-section" v-if="intent.scope">
      <div class="scope-grid">
        <div class="scope-item" v-if="intent.scope.num_papers">
          <span class="scope-label">Papers</span>
          <span class="scope-value">{{ intent.scope.num_papers }}</span>
        </div>
        <div class="scope-item" v-if="intent.scope.year_range">
          <span class="scope-label">Period</span>
          <span class="scope-value">{{ intent.scope.year_range }}</span>
        </div>
        <div class="scope-item" v-if="intent.output_format">
          <span class="scope-label">Format</span>
          <span class="scope-value">{{ intent.output_format.replace(/_/g, ' ') }}</span>
        </div>
        <div class="scope-item" v-if="intent.suggested_sources?.length">
          <span class="scope-label">Sources</span>
          <span class="scope-value">{{ intent.suggested_sources.join(', ') }}</span>
        </div>
      </div>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <button
        id="execute-btn"
        class="btn btn-primary btn-lg"
        :disabled="loading"
        @click="$emit('execute', editedIntent || intent.inferred_intent)"
      >
        <span v-if="loading" class="spinner"></span>
        <span v-else>🚀</span>
        {{ loading ? 'Starting...' : 'Execute Research' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  intent: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['execute'])

const editing = ref(false)
const editedIntent = ref('')

function startEditing() {
  editedIntent.value = props.intent.inferred_intent
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editedIntent.value = ''
}

function saveEdit() {
  editing.value = false
}
</script>

<style scoped>
.intent-review {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Header ─────────────────────────── */
.review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.review-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--success);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
}

.confidence {
  font-size: 0.85rem;
  font-family: var(--font-mono);
  color: var(--accent-text);
  background: rgba(6, 182, 212, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid rgba(6, 182, 212, 0.2);
}

/* ── Goal ────────────────────────────── */
.goal-section h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.goal-display {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.goal-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.goal-edit {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* ── Topics ──────────────────────────── */
.topics-section h4 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.topic-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  padding: 5px 14px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 20px;
  font-size: 0.85rem;
  color: var(--info);
  font-weight: 500;
}

/* ── Scope ───────────────────────────── */
.scope-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.scope-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.scope-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.scope-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* ── Action Bar ─────────────────────── */
.action-bar {
  padding-top: 4px;
}

.btn-lg {
  width: 100%;
  padding: 16px 32px;
  font-size: 1.05rem;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
</style>
