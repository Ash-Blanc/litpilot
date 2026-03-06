<template>
    <div class="card bg-base-100 shadow-xl border border-base-content/5">
        <div class="card-body gap-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span v-if="!done" class="loading loading-ring loading-md text-primary"></span>
                    <span v-else class="text-2xl text-success">✅</span>
                    <h2 class="text-xs font-black uppercase tracking-widest"
                        :class="done ? 'text-success' : 'text-primary'">
                        {{ done ? 'Execution Complete' : 'Active Mission' }}
                    </h2>
                </div>
                <span class="badge badge-ghost font-mono text-xs">{{ events.length }} events</span>
            </div>

            <!-- Inferred Intent Display (The "Why") -->
            <div v-if="intent" class="bg-primary/5 border border-primary/20 rounded-xl p-5 space-y-2">
                <div class="flex items-center gap-2 text-[10px] font-bold uppercase tracking-tight text-primary">
                    <span class="flex h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
                    Synthesized Goal
                </div>
                <p class="text-sm font-medium leading-relaxed italic text-base-content/80">
                    "{{ intent.inferred_intent }}"
                </p>
            </div>

            <!-- Live Event Timeline -->
            <div class="bg-base-200 rounded-xl p-4 max-h-[400px] overflow-y-auto scrollbar-thin" ref="logRef">
                <ul class="timeline timeline-vertical timeline-compact">
                    <li v-for="(event, i) in events" :key="i"
                        class="animate-in fade-in slide-in-from-left-2 duration-300">
                        <hr v-if="i > 0" :class="eventClass(event)" />
                        <div class="timeline-middle">
                            <span class="text-lg">{{ eventIcon(event) }}</span>
                        </div>
                        <div class="timeline-end mb-4 px-3">
                            <time class="font-mono text-[10px] opacity-40 block">{{ formatTime(event) }}</time>
                            <div class="text-sm font-medium" :class="eventTextClass(event)">
                                {{ event.message || event.type }}
                            </div>
                        </div>
                        <hr v-if="i < events.length - 1" :class="eventClass(event)" />
                    </li>

                    <!-- Loading placeholder -->
                    <li v-if="!done">
                        <hr class="bg-primary/20" />
                        <div class="timeline-middle">
                            <span class="loading loading-dots loading-xs text-primary opacity-50"></span>
                        </div>
                        <div class="timeline-end px-3">
                            <span class="text-xs italic opacity-40">Awaiting next step...</span>
                        </div>
                    </li>
                </ul>
            </div>

            <!-- Error display -->
            <div v-if="error" class="alert alert-error shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ error }}</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

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
    if (type === 'status') return '⚡'
    if (type === 'search') return '🔍'
    if (type === 'extract') return '📄'
    if (type === 'navigate') return '🌐'
    if (type === 'error') return '❌'
    if (type === 'done') return '✅'
    return '•'
}

function eventClass(event) {
    const type = event.type || ''
    if (type === 'error') return 'bg-error'
    if (type === 'done') return 'bg-success'
    return 'bg-primary/30'
}

function eventTextClass(event) {
    const type = event.type || ''
    if (type === 'error') return 'text-error'
    if (type === 'done') return 'text-success'
    if (type === 'status') return 'text-primary'
    return 'text-base-content/80'
}

function formatTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
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
