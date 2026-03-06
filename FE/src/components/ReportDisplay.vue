<template>
    <div class="card bg-base-100 shadow-2xl border border-base-content/5" v-if="content">
        <div class="card-body p-6 sm:p-10">
            <div
                class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-8 pb-6 border-b border-base-content/5">
                <h2 class="text-2xl font-black tracking-tight flex items-center gap-3">
                    <span class="text-3xl">📋</span>
                    Literature Review Report
                </h2>
                <div class="flex items-center gap-2">
                    <button class="btn btn-ghost btn-sm sm:btn-md gap-2" @click="copyReport"
                        :class="{ 'btn-success text-white': copied }">
                        <span v-if="!copied">📋</span>
                        <span v-else>✅</span>
                        {{ copied ? 'Copied' : 'Copy' }}
                    </button>
                    <button class="btn btn-secondary btn-sm sm:btn-md gap-2" @click="downloadReport">
                        <span>💾</span>
                        Download
                    </button>
                </div>
            </div>

            <div class="prose prose-lg max-w-none prose-headings:text-base-content prose-p:text-base-content/80 prose-li:text-base-content/80 prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none prose-pre:bg-base-300 prose-pre:border prose-pre:border-base-content/5"
                v-html="renderedContent"></div>
        </div>
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
/* Scoped styles kept minimal as we use DaisyUI typography plugin or Tailwind prose */
/* Since it's marked as prose, make sure it has the class */
</style>
