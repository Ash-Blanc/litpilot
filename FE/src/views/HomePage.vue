<template>
    <div class="max-w-4xl mx-auto space-y-12">
        <!-- ── Hero Section ── -->
        <section class="text-center space-y-6 animate-in fade-in slide-in-from-bottom-5 duration-700">
            <div
                class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider">
                <span>🤖</span>
                <span>Powered by TinyFish Web Agent + EMNLP 2025</span>
            </div>
            <h1 class="text-4xl sm:text-6xl font-black tracking-tight leading-none">
                Your AI <span class="text-gradient">Research Autopilot</span>
            </h1>
            <p class="text-lg text-base-content/70 max-w-2xl mx-auto leading-relaxed">
                Describe your partial research session. LitPilot infers your goal and
                autonomously completes the literature review on live academic sites.
            </p>
        </section>

        <div class="flex flex-col items-center">
            <ul class="steps steps-vertical sm:steps-horizontal w-full max-w-2xl text-sm">
                <li class="step" :class="{ 'step-primary': phase >= 0 }">Define Goal</li>
                <li class="step" :class="{ 'step-primary': phase >= 2 }">Autonomous Execution</li>
                <li class="step" :class="{ 'step-primary': phase >= 3 }">Research Report</li>
            </ul>
        </div>

        <!-- ── Phase 0: Input ── -->
        <section class="card bg-base-100 shadow-xl border border-base-content/5 transition-all duration-500"
            :class="{ 'opacity-50 scale-95 pointer-events-none': phase > 0 }">
            <div class="card-body">
                <InputForm v-model="description" :loading="inferring" @submit="handleInferIntent"
                    @files-changed="handleFilesChanged" @recall-history="showHistoryModal = true" />
            </div>
        </section>

        <!-- ── Phase 1: Implicit Inference (Subtle Loader) ── -->
        <section v-if="phase === 1" class="flex flex-col items-center justify-center p-12 space-y-4 animate-pulse">
            <span class="loading loading-spinner loading-lg text-primary"></span>
            <p class="text-sm font-medium text-base-content/60">Synthesizing research strategy via Multi-Model
                Consensus...</p>
        </section>

        <!-- ── Phase 2: Execution Stream ── -->
        <section v-if="phase >= 2" class="animate-in fade-in slide-in-from-bottom-10 duration-500">
            <ExecutionStream :intent="intentData" :events="streamEvents" :done="executionDone"
                :error="executionError" />
        </section>

        <!-- ── Phase 3: Final Report ── -->
        <section v-if="phase >= 3" class="animate-in fade-in zoom-in-95 duration-500">
            <ReportDisplay :content="reportContent" />
        </section>

        <!-- ── Reset Button ── -->
        <div v-if="phase >= 3" class="flex justify-center py-8">
            <button class="btn btn-outline btn-secondary" @click="resetAll">
                🔄 Start New Research
            </button>
        </div>

        <!-- ── History Modal ── -->
        <div v-if="showHistoryModal" class="modal modal-open">
            <div class="modal-box max-w-2xl bg-base-100 border border-base-content/10">
                <h3 class="font-bold text-lg">Recall Past Research</h3>
                <p class="py-4 text-sm text-base-content/60">
                    Paste notes, browser logs, or summaries from manual research you did days or weeks ago.
                    LitPilot will reconstruct the context and build upon it.
                </p>
                <textarea class="textarea textarea-bordered w-full h-48 font-mono text-sm" v-model="historyNotes"
                    placeholder="e.g. Last week I was looking at EMNLP papers on agents. I found 3 papers about decomposition but wanted more focus on multi-model verification..."></textarea>
                <div class="modal-action">
                    <button class="btn btn-ghost" @click="showHistoryModal = false">Cancel</button>
                    <button class="btn btn-primary" :disabled="!historyNotes.trim() || reconstructing"
                        @click="handleHistoryImport">
                        <span v-if="reconstructing" class="loading loading-spinner"></span>
                        {{ reconstructing ? 'Reconstructing...' : 'Restore Context' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import InputForm from '../components/InputForm.vue'
import IntentReview from '../components/IntentReview.vue'
import ExecutionStream from '../components/ExecutionStream.vue'
import ReportDisplay from '../components/ReportDisplay.vue'
import { inferIntent, executeResearch, reconstructHistory } from '../composables/useApi.js'

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
    inferring.value = true
    phase.value = 1
    try {
        const formattedImages = screenshots.value.map(base64 => ({ url: base64 }))
        const result = await inferIntent(description.value, formattedImages)
        intentData.value = result.intent

        // Implicit transition: Start execution automatically
        handleExecute(result.intent)
    } catch (err) {
        alert('Error during inference: ' + err.message)
        phase.value = 0
    } finally {
        inferring.value = false
    }
}

function handleExecute(intent) {
    executing.value = true
    phase.value = 2
    streamEvents.value = []
    executionDone.value = false
    executionError.value = ''
    reportContent.value = ''

    executeResearch(intent, {
        onEvent(event) {
            streamEvents.value.push(event)
        },
        onDone(content) {
            reportContent.value = content
            executionDone.value = true
            executing.value = false
            phase.value = 3
        },
        onError(msg) {
            executionError.value = msg
            executionDone.value = true
            executing.value = false
        },
    })
}

async function handleHistoryImport() {
    reconstructing.value = true
    try {
        const result = await reconstructHistory(historyNotes.value)
        description.value = result.reconstructed_intent
        pastContextSummary.value = result.summary
        showHistoryModal.value = false
        // Note: In a real app, we'd save this to a global context or database
        alert(`Context Restored: ${result.summary}`)
    } catch (err) {
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
