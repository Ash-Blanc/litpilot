<template>
  <div class="report-display glass-card animate-fade-in-up" v-if="content">
    <div class="report-header">
      <h2>📋 Literature Review Report</h2>
      <div class="report-actions">
        <button class="btn btn-ghost" @click="copyReport" :title="copied ? 'Copied!' : 'Copy'">
          {{ copied ? '✅ Copied' : '📋 Copy' }}
        </button>
        <button class="btn btn-ghost" @click="downloadReport">
          💾 Download
        </button>
      </div>
    </div>

    <div class="report-body" v-html="renderedContent"></div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: { type: String, default: '' },
})

const copied = ref(false)

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content, { breaks: true, gfm: true })
})

async function copyReport() {
  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
    const textarea = document.createElement('textarea')
    textarea.value = props.content
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function downloadReport() {
  const blob = new Blob([props.content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `litpilot-report-${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.report-display {
  padding: 32px;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.report-header h2 {
  font-size: 1.3rem;
}

.report-actions {
  display: flex;
  gap: 4px;
}

/* ── Markdown Rendered Content ──────── */
.report-body {
  line-height: 1.75;
  color: var(--text-secondary);
}

.report-body :deep(h1) {
  font-size: 1.5rem;
  margin: 24px 0 12px;
  color: var(--text-primary);
}

.report-body :deep(h2) {
  font-size: 1.25rem;
  margin: 20px 0 10px;
  color: var(--text-primary);
}

.report-body :deep(h3) {
  font-size: 1.1rem;
  margin: 16px 0 8px;
  color: var(--text-primary);
}

.report-body :deep(p) {
  margin: 8px 0;
  color: var(--text-secondary);
}

.report-body :deep(ul),
.report-body :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.report-body :deep(li) {
  margin: 4px 0;
}

.report-body :deep(a) {
  color: var(--accent-text);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.report-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 0.9rem;
}

.report-body :deep(th),
.report-body :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--border-subtle);
  text-align: left;
}

.report-body :deep(th) {
  background: rgba(255, 255, 255, 0.04);
  font-weight: 600;
  color: var(--text-primary);
}

.report-body :deep(code) {
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.88em;
  font-family: var(--font-mono);
}

.report-body :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 12px 0;
}

.report-body :deep(pre code) {
  background: none;
  padding: 0;
}

.report-body :deep(blockquote) {
  border-left: 3px solid var(--accent-start);
  padding-left: 16px;
  margin: 12px 0;
  color: var(--text-muted);
  font-style: italic;
}

.report-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 24px 0;
}
</style>
