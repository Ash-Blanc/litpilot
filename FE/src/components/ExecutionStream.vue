<template>
    <div class="bg-base-100/50 backdrop-blur-2xl rounded-3xl border border-base-content/10 shadow-2xl overflow-hidden">
        <div class="p-4 sm:p-10 space-y-10">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="relative">
                        <span v-if="!done" class="loading loading-ring loading-md text-primary scale-125"></span>
                        <div v-else
                            class="h-10 w-10 flex items-center justify-center text-primary animate-in fade-in zoom-in">
                            <CheckCircle class="w-8 h-8" />
                        </div>
                    </div>
                    <h2 class="text-xs font-black uppercase tracking-[0.2em]"
                        :class="done ? 'text-success' : 'text-primary'">
                        {{ done ? 'Mission Complete' : 'Autonomous Session' }}
                    </h2>
                </div>
                <div class="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-lg border border-white/10">
                    <span class="text-[10px] font-black font-mono opacity-30">{{ events.length }}
                        EVENT_LOG_EMITTED</span>
                </div>
            </div>

            <!-- Inferred Intent Display (The "Why") -->
            <div v-if="intent"
                class="bg-primary/5 border border-primary/20 rounded-2xl p-6 sm:p-8 space-y-4 relative overflow-hidden group">
                <div
                    class="absolute top-0 right-0 p-8 opacity-[0.03] scale-[4] rotate-12 group-hover:scale-[4.5] transition-transform duration-1000">
                    <Target class="w-8 h-8" />
                </div>
                <div class="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-primary/60">
                    <span class="flex h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
                    Synthesized Objective
                </div>
                <p class="text-xl font-bold leading-tight font-heading text-white/90">
                    {{ intent.inferred_intent }}
                </p>
            </div>

            <!-- Live Event Timeline -->
            <div class="bg-black/20 rounded-2xl p-6 max-h-[450px] overflow-y-auto scrollbar-thin border border-white/5"
                ref="logRef">
                <ul class="space-y-6">
                    <li v-for="(event, i) in events" :key="i" class="animate-in flex gap-4 relative">
                        <div v-if="i < events.length - 1"
                            class="absolute left-[11px] top-8 bottom-[-24px] w-px bg-white/5"></div>

                        <div
                            class="h-6 w-6 rounded-lg bg-white/5 flex items-center justify-center shrink-0 border border-white/10 group-hover:bg-primary/10 transition-all text-white/50">
                            <component :is="eventIcon(event)" class="w-3.5 h-3.5" />
                        </div>

                        <div class="space-y-1 py-0.5">
                            <div class="flex items-center gap-3">
                                <span class="text-[10px] font-black font-mono opacity-20">{{ formatTime(event) }}</span>
                                <span class="text-xs font-bold uppercase tracking-widest"
                                    :class="eventTextClass(event)">
                                    {{ event.type }}
                                </span>
                            </div>
                            <p class="text-sm font-medium text-white/50 leading-relaxed">
                                {{ event.message || 'Executing agent instruction...' }}
                            </p>
                        </div>
                    </li>

                    <!-- Loading placeholder -->
                    <li v-if="!done" class="flex gap-4">
                        <div
                            class="h-6 w-6 rounded-lg bg-white/5 flex items-center justify-center shrink-0 border border-white/10">
                            <span class="loading loading-dots loading-xs text-primary/40"></span>
                        </div>
                        <div class="py-1">
                            <span class="text-xs font-black uppercase tracking-[0.2em] opacity-10">Awaiting
                                stream...</span>
                        </div>
                    </li>
                </ul>
            </div>

            <!-- Error display -->
            <div v-if="error"
                class="bg-error/10 border border-error/20 p-6 rounded-2xl flex items-start gap-4 animate-in">
                <div class="h-10 w-10 bg-error/20 rounded-xl flex items-center justify-center shrink-0 text-error">
                    <AlertTriangle class="w-6 h-6" />
                </div>
                <div class="space-y-1">
                    <div class="text-sm font-black uppercase tracking-widest text-error">Execution Error</div>
                    <p class="text-sm font-medium text-error/80 leading-relaxed">{{ error }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { AlertTriangle, CheckCircle, FileText, Globe, Search, Target, XCircle, Zap } from 'lucide-vue-next'

const props = defineProps({
    intent: { type: Object, default: null },
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
    if (type === 'status') return Zap
    if (type === 'search') return Search
    if (type === 'extract') return FileText
    if (type === 'navigate') return Globe
    if (type === 'error') return XCircle
    if (type === 'done') return CheckCircle
    return Zap
}

function eventTextClass(event) {
    const type = event.type || ''
    if (type === 'error') return 'text-error'
    if (type === 'done') return 'text-success'
    if (type === 'status') return 'text-primary'
    return 'text-white/40'
}

function formatTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}
</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
    width: 4px;
}

.scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}
</style>
