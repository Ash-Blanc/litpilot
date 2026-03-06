<template>
    <div class="bg-base-100/50 backdrop-blur-2xl rounded-3xl border border-base-content/10 shadow-2xl overflow-hidden"
        v-if="content">
        <div class="p-6 sm:p-12">
            <div
                class="flex flex-col sm:flex-row items-center justify-between gap-6 mb-12 pb-8 border-b border-base-content/10">
                <div class="space-y-1 text-center sm:text-left">
                    <div class="text-[10px] font-black uppercase tracking-[0.2em] text-primary mb-2">Synthesis Complete
                    </div>
                    <h2 class="text-3xl font-black tracking-tight font-heading">
                        Literature Review Report
                    </h2>
                </div>
                <div class="flex items-center gap-3">
                    <button class="btn btn-ghost hover:bg-base-200 font-bold text-xs uppercase tracking-widest gap-2"
                        @click="copyReport" :class="{ 'text-success': copied }">
                        <Copy v-if="!copied" class="w-4 h-4" />
                        <Check v-else class="w-4 h-4" />
                        {{ copied ? 'Copied' : 'Copy MD' }}
                    </button>
                    <button
                        class="btn btn-primary px-6 font-black text-xs uppercase tracking-widest shadow-xl shadow-primary/20 border-none"
                        @click="downloadReport">
                        <Save class="w-4 h-4 mr-2" />
                        Export .md
                    </button>
                </div>
            </div>

            <div class="prose prose-lg max-w-none 
        prose-headings:font-heading prose-headings:font-black prose-headings:tracking-tight
        prose-p:font-medium prose-p:leading-relaxed
        prose-li:font-medium
        prose-strong:font-bold
        prose-a:text-primary prose-a:no-underline hover:prose-a:underline
        prose-code:text-primary prose-code:bg-primary/10 prose-code:px-2 prose-code:py-0.5 prose-code:rounded-lg prose-code:before:content-none prose-code:after:content-none
        prose-pre:bg-base-300 prose-pre:border prose-pre:border-base-content/10 prose-pre:rounded-2xl
        " v-html="renderedContent"></div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { marked } from 'marked'
import { Copy, Check, Save } from 'lucide-vue-next'

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
