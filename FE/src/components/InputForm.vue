<template>
  <div class="input-form">
    <div class="form-header">
      <h3>Describe Your Research Session</h3>
      <p>Tell us what you've done so far — step by step. We'll figure out the rest.</p>
    </div>

    <div class="textarea-wrap">
      <textarea
        id="research-description"
        class="input"
        v-model="description"
        :placeholder="placeholder"
        rows="8"
        @input="$emit('update:modelValue', description)"
        @paste="handlePaste"
      ></textarea>
      <span class="char-count" :class="{ warn: description.length > 2000 }">
        {{ description.length }} / 3000
      </span>
    </div>

    <!-- Optional screenshot upload -->
    <div
      class="drop-zone"
      :class="{ 'drop-active': isDragOver }"
      @dragover.prevent="isDragOver = true"
      @dragleave="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <input
        type="file"
        id="screenshot-upload"
        accept="image/*"
        multiple
        class="sr-only"
        @change="handleFileSelect"
        ref="fileInput"
      />
      <label for="screenshot-upload" class="drop-label">
        <span class="drop-icon">🖼️</span>
        <span class="drop-text">
          <strong>Drop screenshots</strong> or click to upload (optional)
        </span>
      </label>
      <div v-if="files.length" class="file-list">
        <div v-for="(item, i) in files" :key="i" class="file-chip">
          <span>{{ item.file.name }}</span>
          <button @click="removeFile(i)" class="file-remove" aria-label="Remove file">✕</button>
        </div>
      </div>
    </div>

    <button
      id="analyze-intent-btn"
      class="btn btn-primary btn-lg"
      :disabled="!description.trim() || loading"
      @click="$emit('submit')"
    >
      <span v-if="loading" class="spinner"></span>
      <span v-else>🔍</span>
      {{ loading ? 'Analyzing...' : 'Analyze Intent' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'files-changed'])

const description = ref(props.modelValue)
const files = ref([])
const isDragOver = ref(false)
const fileInput = ref(null)

const placeholder = `Example:
1. Searched Google Scholar for "decomposed intent extraction web agents"
2. Opened the first PDF result — a 2025 EMNLP paper
3. Skimmed the methods section, highlighted the two-stage approach
4. Went back to results, opened arXiv link for reference #12
5. Started a comparison table in my notes...`

async function handlePaste(e) {
  const items = e.clipboardData?.items
  if (!items) return

  const pastedFiles = []
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        pastedFiles.push(file)
      }
    }
  }

  if (pastedFiles.length > 0) {
    // Only intercept the paste if we found images
    e.preventDefault()
    await addFiles(pastedFiles)
  }
}

// Compress and convert file to base64
async function processFile(file) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const maxDim = 1024
        let width = img.width
        let height = img.height

        if (width > height && width > maxDim) {
          height *= maxDim / width
          width = maxDim
        } else if (height > maxDim) {
          width *= maxDim / height
          height = maxDim
        }

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        
        // Compress as JPEG
        resolve(canvas.toDataURL('image/jpeg', 0.8))
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

async function handleDrop(e) {
  isDragOver.value = false
  const dropped = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  await addFiles(dropped)
}

async function handleFileSelect(e) {
  const selected = Array.from(e.target.files)
  await addFiles(selected)
}

async function addFiles(newFiles) {
  for (const file of newFiles) {
    const base64 = await processFile(file)
    files.value.push({ file, base64 })
  }
  emit('files-changed', files.value.map(f => f.base64))
}

function removeFile(index) {
  files.value.splice(index, 1)
  emit('files-changed', files.value.map(f => f.base64))
}
</script>

<style scoped>
.input-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-header h3 {
  margin-bottom: 6px;
}

.form-header p {
  font-size: 0.9rem;
}

.textarea-wrap {
  position: relative;
}

.textarea-wrap .input {
  min-height: 200px;
  font-size: 0.95rem;
}

.char-count {
  position: absolute;
  bottom: 12px;
  right: 14px;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.char-count.warn {
  color: var(--warning);
}

/* ── Drop Zone ──────────────────────── */
.drop-zone {
  border: 2px dashed var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  transition: all var(--duration-normal) var(--ease-out);
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone.drop-active {
  border-color: var(--accent-start);
  background: rgba(6, 182, 212, 0.05);
}

.drop-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  color: var(--text-secondary);
}

.drop-icon {
  font-size: 1.3rem;
}

.drop-text {
  font-size: 0.9rem;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.file-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.file-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.7rem;
  padding: 2px;
}

.file-remove:hover {
  color: var(--error);
}

/* ── Button ─────────────────────────── */
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
