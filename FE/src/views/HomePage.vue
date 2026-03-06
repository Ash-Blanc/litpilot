<template>
    <div class="max-w-4xl mx-auto space-y-16 py-8">
        <!-- ── Hero Section ── -->
        <section class="text-center space-y-8 animate-in">
            <div
                class="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-[0.2em] shadow-2xl">
                <span class="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>
                <span>Decomposed Intent Extraction Engine</span>
            </div>
            <h1 class="text-5xl sm:text-7xl font-black tracking-tight leading-[0.9] font-heading">
                Research <br /> <span class="text-primary">On Autopilot</span>
            </h1>
            <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed font-medium">
                Describe your browsing steps. Our multi-model consensus engine infers your goal and autonomously
                completes the review.
            </p>
        </section>

        <!-- ── Step Indicator ── -->
        <div class="flex flex-col items-center">
            <div class="flex items-center gap-4 sm:gap-8 w-full max-w-2xl">
                <div v-for="(label, i) in ['Define', 'Execute', 'Report']" :key="i"
                    class="flex-1 flex flex-col items-center gap-3">
                    <div class="h-10 w-10 rounded-xl flex items-center justify-center font-bold transition-all duration-500"
                        :class="phase >= (i === 0 ? 0 : i + 1) ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'bg-white/5 border border-white/10 opacity-30'">
                        {{ i + 1 }}
                    </div>
                    <span class="text-[10px] font-black uppercase tracking-widest transition-opacity duration-500"
                        :class="phase >= (i === 0 ? 0 : i + 1) ? 'opacity-100' : 'opacity-20'">
                        {{ label }}
                    </span>
                </div>
            </div>
        </div>

        <!-- ── Phase 0: Input ── -->
        <section
            class="bg-base-100/50 backdrop-blur-2xl rounded-3xl border border-base-content/10 shadow-2xl transition-all duration-700"
            :class="{ 'opacity-20 blur-sm scale-95 pointer-events-none': phase > 0 }">
            <div class="p-4 sm:p-8">
                <InputForm v-model="description" :loading="inferring" @submit="handleInferIntent"
                    @files-changed="handleFilesChanged" @recall-history="showHistoryModal = true" />
            </div>
        </section>

        <!-- ── Phase 1: Implicit Inference (Subtle Loader) ── -->
        <section v-if="phase === 1" class="flex flex-col items-center justify-center p-20 space-y-6 animate-in">
            <div class="relative">
                <div class="absolute inset-0 bg-primary/20 blur-3xl rounded-full"></div>
                <span class="loading loading-ring loading-lg text-primary relative z-10 scale-150"></span>
            </div>
            <div class="text-center space-y-2">
                <p class="text-sm font-black uppercase tracking-widest text-primary">Orchestrating Consensus</p>
                <p class="text-xs text-white/40 font-medium">Synthesizing research strategy across LLM experts...</p>
            </div>
        </section>

        <!-- ── Phase 2: Execution Stream ── -->
        <section v-if="phase >= 2" class="animate-in">
            <ExecutionStream :intent="intentData" :events="streamEvents" :done="executionDone"
                :error="executionError" />
        </section>

        <!-- ── Phase 3: Final Report ── -->
        <section v-if="phase >= 3" class="animate-in delay-300">
            <ReportDisplay :content="reportContent" />
        </section>

        <!-- ── Reset Button ── -->
        <div v-if="phase >= 3" class="flex justify-center py-12">
            <button class="btn btn-ghost hover:bg-white/5 gap-3 font-bold uppercase tracking-widest text-xs"
                @click="resetAll">
                <RotateCcw class="w-4 h-4" /> New Mission
            </button>
        </div>

        <!-- ── History Modal ── -->
        <div v-if="showHistoryModal" class="modal modal-open backdrop-blur-xl">
            <div
                class="modal-box bg-base-100/80 backdrop-blur-2xl border border-base-content/10 p-10 max-w-2xl rounded-3xl shadow-2xl">
                <h3 class="font-heading text-3xl font-black mb-2">Recall Past Data</h3>
                <p class="text-sm text-white/50 mb-8 leading-relaxed font-medium">
                    Paste rough notes or logs from research you did days/weeks ago.
                    LitPilot will archaeologically reconstruct the context.
                </p>
                <textarea
                    class="textarea textarea-bordered bg-white/5 border-white/10 w-full h-48 font-mono text-xs focus:textarea-primary transition-all p-4"
                    v-model="historyNotes" placeholder="Last week I was looking at EMNLP papers..."></textarea>
                <div class="modal-action gap-4">
                    <button class="btn btn-ghost font-bold text-xs uppercase"
                        @click="showHistoryModal = false">Cancel</button>
                    <button
                        class="btn btn-primary px-8 font-black text-xs uppercase tracking-widest shadow-xl shadow-primary/20"
                        :disabled="!historyNotes.trim() || reconstructing" @click="handleHistoryImport">
                        <span v-if="reconstructing" class="loading loading-spinner"></span>
                        {{ reconstructing ? 'Restoring...' : 'Restore Context' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import InputForm from '../components/InputForm.vue'
import ExecutionStream from '../components/ExecutionStream.vue'
import ReportDisplay from '../components/ReportDisplay.vue'
import { inferIntent, executeResearch, reconstructHistory } from '../composables/useApi.js'
import { RotateCcw } from 'lucide-vue-next'

// ── State ──
const phase = ref(0)          // 0=input, 1=review, 2=executing, 3=report
const description = ref('')
const screenshots = ref([])   // array of base64 strings
const inferring = ref(false)
const executing = ref(false)

const intentData = ref(null)
const streamEvents = ref([])
const executionDone = ref(false)
const executionError = ref('')
const reportContent = ref('')

// ── Historical Recall State ──
const showHistoryModal = ref(false)
const historyNotes = ref('')
const reconstructing = ref(false)
const pastContextSummary = ref('')

// ── Handlers ──
function handleFilesChanged(base64Files) {
    screenshots.value = base64Files
}

async function handleInferIntent() {
    if (!description.value.trim()) {
        alert('Please enter a research description first')
        return
    }
    inferring.value = true
    phase.value = 1
    try {
        console.log('Starting intent inference...')
        const formattedImages = screenshots.value.map(base64 => ({ url: base64 }))
        const result = await inferIntent(description.value, formattedImages)
        intentData.value = result.intent
        console.log('Intent inferred:', result.intent)

        // Implicit transition: Start execution automatically
        handleExecute(result.intent)
    } catch (err) {
        console.error('Inference error:', err)
        alert('Error during inference: ' + err.message)
        phase.value = 0
    } finally {
        inferring.value = false
    }
}

function handleExecute(intent) {
    console.log('Starting execution with intent:', intent)
    executing.value = true
    phase.value = 2
    streamEvents.value = []
    executionDone.value = false
    executionError.value = ''
    reportContent.value = ''

    executeResearch(intent, {
        onEvent(event) {
            console.log('Stream event:', event)
            streamEvents.value.push(event)
        },
        onDone(content) {
            console.log('Execution complete, report length:', content?.length)
            reportContent.value = content
            executionDone.value = true
            executing.value = false
            phase.value = 3
        },
        onError(msg) {
            console.error('Execution error:', msg)
            executionError.value = msg
            executionDone.value = true
            executing.value = false
        },
    })
}

async function handleHistoryImport() {
    if (!historyNotes.value.trim()) {
        alert('Please enter some notes to reconstruct')
        return
    }
    reconstructing.value = true
    try {
        console.log('Reconstructing history from notes...')
        const result = await reconstructHistory(historyNotes.value)
        console.log('Reconstructed intent:', result.reconstructed_intent)
        description.value = result.reconstructed_intent
        pastContextSummary.value = result.summary || ''
        showHistoryModal.value = false
        alert(`Context Restored!\n\n${pastContextSummary.value || 'Research intent has been added to the input field.'}`)
    } catch (err) {
        console.error('History reconstruction error:', err)
        alert('Error during history reconstruction: ' + err.message)
    } finally {
        reconstructing.value = false
    }
}

function resetAll() {
    phase.value = 0
    description.value = ''
    intentData.value = null
    streamEvents.value = []
    executionDone.value = false
    executionError.value = ''
    reportContent.value = ''
    historyNotes.value = ''
}
</script>

<style scoped>
/* Scoped styles kept minimal as we use Tailwind classes */
</style>
