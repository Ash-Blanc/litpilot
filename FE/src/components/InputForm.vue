<template>
    <div class="space-y-6">
        <div class="space-y-2">
            <h3 class="text-xl font-bold">Describe Your Research Session</h3>
            <p class="text-sm text-base-content/60">Tell us what you've done so far — step by step. We'll figure out the
                rest.</p>
        </div>

        <div class="relative group">
            <textarea id="research-description"
                class="textarea textarea-bordered textarea-lg w-full min-h-[200px] leading-relaxed transition-all focus:textarea-primary"
                v-model="description" :placeholder="placeholder" @input="$emit('update:modelValue', description)"
                @paste="handlePaste"></textarea>
            <div class="absolute top-3 right-4 flex items-center gap-2">
                <button class="btn btn-xs btn-outline btn-primary gap-1.5 font-bold" @click="$emit('recall-history')"
                    title="Recall past research notes">
                    🕰️ Recall History
                </button>
            </div>
            <div class="absolute bottom-3 right-4 text-xs font-mono transition-colors"
                :class="description.length > 2000 ? 'text-warning' : 'text-base-content/40'">
                {{ description.length }} / 3000
            </div>
        </div>

        <!-- Optional screenshot upload -->
        <div class="border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer group hover:bg-base-200"
            :class="isDragOver ? 'border-primary bg-primary/5' : 'border-base-content/10'"
            @dragover.prevent="isDragOver = true" @dragleave="isDragOver = false" @drop.prevent="handleDrop">
            <input type="file" id="screenshot-upload" accept="image/*" multiple class="hidden"
                @change="handleFileSelect" ref="fileInput" />
            <label for="screenshot-upload" class="cursor-pointer space-y-3 block">
                <span class="text-4xl block group-hover:scale-110 transition-transform">🖼️</span>
                <span class="text-sm text-base-content/60 block">
                    <strong class="text-base-content">Drop screenshots</strong> or click to upload (optional)
                </span>
            </label>

            <div v-if="files.length" class="flex flex-wrap gap-2 mt-6 justify-center">
                <div v-for="(item, i) in files" :key="i" class="badge badge-outline badge-md gap-2 py-3 px-4">
                    <span class="truncate max-w-[150px]">{{ item.file.name }}</span>
                    <button @click.prevent="removeFile(i)" class="hover:text-error transition-colors"
                        aria-label="Remove file">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M18 6 6 18M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <button id="analyze-intent-btn" class="btn btn-primary btn-lg w-full shadow-lg shadow-primary/20"
            :disabled="!description.trim() || loading" @click="$emit('submit')">
            <span v-if="loading" class="loading loading-spinner"></span>
            <span v-else class="text-lg">🔍</span>
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

const emit = defineEmits(['update:modelValue', 'submit', 'files-changed', 'recall-history'])

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
        e.preventDefault()
        await addFiles(pastedFiles)
    }
}

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
/* Scoped styles kept minimal as we use Tailwind classes */
</style>
