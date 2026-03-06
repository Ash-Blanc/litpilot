<template>
    <div class="space-y-10">
        <div class="space-y-2">
            <h3 class="text-3xl font-black font-heading tracking-tight">Mission Briefing</h3>
            <p class="text-sm text-white/40 font-medium">Map out your research session. We'll take it from here.</p>
        </div>

        <div class="relative group">
            <textarea id="research-description"
                class="textarea bg-white/5 border-white/10 w-full min-h-[250px] leading-relaxed transition-all focus:textarea-primary text-base font-medium p-6 rounded-2xl placeholder:opacity-20"
                v-model="description" :placeholder="placeholder" @input="$emit('update:modelValue', description)"
                @paste="handlePaste"></textarea>

            <!-- Top Actions -->
            <div class="absolute top-4 right-4 flex items-center gap-3 space-x-2">
                <div class="tooltip tooltip-left tooltip-primary" data-tip="Connect to Browser MCP / Extension">
                    <button
                        class="btn btn-xs bg-white/5 border-white/10 hover:bg-primary hover:border-primary text-[10px] font-black uppercase tracking-widest gap-2 py-3 h-auto min-h-0 rounded-lg transition-all"
                        :disabled="isFetchingHistory" @click.prevent="fetchBrowserHistory">
                        <span v-if="isFetchingHistory" class="loading loading-spinner w-3 h-3"></span>
                        <Globe v-else class="w-4 h-4" />
                        {{ isFetchingHistory ? 'Connecting...' : 'Fetch Browser Logs' }}
                    </button>
                </div>
                <div class="tooltip tooltip-left tooltip-primary" data-tip="Restore past data">
                    <button
                        class="btn btn-xs bg-white/5 border-white/10 hover:bg-primary hover:border-primary text-[10px] font-black uppercase tracking-widest gap-2 py-3 h-auto min-h-0 rounded-lg transition-all"
                        @click.prevent="$emit('recall-history')">
                        <History class="w-4 h-4" /> Recall History
                    </button>
                </div>
            </div>

            <!-- Character Count -->
            <div class="absolute bottom-4 right-6 text-[10px] font-black font-mono tracking-widest transition-colors"
                :class="description.length > 2000 ? 'text-warning' : 'text-white/20'">
                {{ description.length }} / 3000
            </div>
        </div>

        <!-- ── Upload Area ── -->
        <div class="bg-white/5 border border-dashed border-white/10 rounded-2xl p-10 text-center transition-all cursor-pointer group hover:bg-white/[0.08] hover:border-primary/50"
            :class="isDragOver ? 'border-primary bg-primary/10' : ''" @dragover.prevent="isDragOver = true"
            @dragleave="isDragOver = false" @drop.prevent="handleDrop">
            <input type="file" id="screenshot-upload" accept="image/*" multiple class="hidden"
                @change="handleFileSelect" ref="fileInput" />
            <label for="screenshot-upload" class="cursor-pointer space-y-4 block">
                <div
                    class="h-16 w-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 group-hover:bg-primary/20 text-white/50 group-hover:text-primary transition-all duration-500">
                    <Image class="w-8 h-8" />
                </div>
                <div class="space-y-1">
                    <span class="text-sm font-bold block">Visual Context</span>
                    <span class="text-xs text-white/30 font-medium block">
                        Drop screenshots of papers or search results
                    </span>
                </div>
            </label>

            <div v-if="files.length" class="flex flex-wrap gap-2 mt-8 justify-center">
                <div v-for="(item, i) in files" :key="i"
                    class="bg-white/5 border border-white/10 rounded-xl flex items-center gap-3 py-2 px-4 animate-in">
                    <span class="text-xs font-bold truncate max-w-[120px]">{{ item.file.name }}</span>
                    <button @click.prevent="removeFile(i)" class="text-white/20 hover:text-error transition-colors"
                        aria-label="Remove file">
                        <X class="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>

        <button id="analyze-intent-btn"
            class="btn btn-primary btn-lg w-full h-16 rounded-2xl shadow-2xl shadow-primary/20 font-black text-xs uppercase tracking-[0.2em] border-none"
            :disabled="!description.trim() || loading || isFetchingHistory" @click="$emit('submit')">
            <span v-if="loading" class="loading loading-spinner"></span>
            <Zap v-else class="w-5 h-5 mx-1" />
            {{ loading ? 'Synchronizing...' : 'Launch Agent' }}
        </button>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { getBrowserHistory } from '../composables/useApi.js'
import { Globe, History, Image, X, Zap } from 'lucide-vue-next'

const props = defineProps({
    modelValue: { type: String, default: '' },
    loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'files-changed', 'recall-history'])

const description = ref(props.modelValue)
const files = ref([])
const isDragOver = ref(false)
const fileInput = ref(null)
const isFetchingHistory = ref(false)

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

async function fetchBrowserHistory() {
    isFetchingHistory.value = true
    try {
        const data = await getBrowserHistory()

        let newLog = `[System: Native SQLite DB connection established]\n`

        if (data.status === 'success') {
            newLog += `[Status: Authorized access to local ${data.browser} history]\n\nRecent Browsing Activity (Last 24h):\n`

            data.history.forEach(item => {
                newLog += `- ${item.time}: ${item.title} (${item.url})\n`
            })

            newLog += `\nGoal: Please review these sources and summarize the key findings or intent based on the pages visited.`
        } else {
            newLog += `[Error: ${data.message}]\n`
        }

        description.value = newLog
        emit('update:modelValue', description.value)
    } catch (err) {
        alert('Failed to fetch browser history: ' + err.message)
    } finally {
        isFetchingHistory.value = false
    }
}
</script>

<style scoped>
/* Scoped styles kept minimal as we use Tailwind classes */
</style>
