<template>
  <div class="execution-stream glass-card animate-fade-in-up">
    <div class="stream-header">
      <div class="stream-badge" :class="{ active: !done, complete: done }">
        <span class="badge-dot" :class="{ spinning: !done }"></span>
        {{ done ? 'Execution Complete' : 'Agent Working...' }}
      </div>
      <span class="event-count">{{ events.length }} events</span>
    </div>

    <!-- Live Event Log -->
    <div class="event-log" ref="logRef">
      <div
        v-for="(event, i) in events"
        :key="i"
        class="event-item animate-fade-in"
        :class="eventClass(event)"
      >
        <span class="event-icon">{{ eventIcon(event) }}</span>
        <span class="event-message">{{ event.message || event.type }}</span>
        <span class="event-time">{{ formatTime(event) }}</span>
      </div>

      <!-- Typing indicator while running -->
      <div v-if="!done" class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>

    <!-- Error display -->
    <div v-if="error" class="error-bar">
      <span>⚠️</span> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  events: { type: Array, default: () => [] },
  done: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const logRef = ref(null)

// Auto-scroll to bottom when new events arrive
watch(
  () => props.events.length,
  async () => {
    await nextTick()
    if (logRef.value) {
      logRef.value.scrollTop = logRef.value.scrollHeight
    }
  }
)

function eventIcon(event) {
  const type = event.type || ''
  if (type === 'status') return '⚡'
  if (type === 'search') return '🔍'
  if (type === 'extract') return '📄'
  if (type === 'navigate') return '🌐'
  if (type === 'error') return '❌'
  if (type === 'done') return '✅'
  return '→'
}

function eventClass(event) {
  return `event-${event.type || 'info'}`
}

function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
</script>

<style scoped>
.execution-stream {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stream-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stream-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent-text);
}

.stream-badge.complete {
  color: var(--success);
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-start);
}

.badge-dot.spinning {
  animation: pulse-glow 1.5s ease-in-out infinite;
  box-shadow: 0 0 10px var(--accent-glow);
}

.stream-badge.complete .badge-dot {
  background: var(--success);
  animation: none;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
}

.event-count {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* ── Event Log ──────────────────────── */
.event-log {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.event-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  background: rgba(255, 255, 255, 0.02);
  transition: background var(--duration-fast);
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.event-icon {
  flex-shrink: 0;
  font-size: 1rem;
}

.event-message {
  flex: 1;
  color: var(--text-secondary);
}

.event-time {
  flex-shrink: 0;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.event-error .event-message {
  color: var(--error);
}

/* ── Typing Indicator ───────────────── */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 16px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--accent-start);
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* ── Error Bar ──────────────────────── */
.error-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 0.9rem;
}
</style>
