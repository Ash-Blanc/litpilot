<template>
  <div class="card bg-base-100 shadow-xl border border-base-content/5" v-if="intent">
    <div class="card-body gap-8">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-3 h-3 bg-success rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]"></div>
          <h2 class="text-sm font-bold uppercase tracking-widest text-success">Intent Inferred</h2>
        </div>
        <div v-if="intent.confidence" class="badge badge-primary badge-outline font-mono py-3 px-4">
          {{ Math.round(intent.confidence * 100) }}% confidence
        </div>
      </div>

      <!-- Inferred Goal -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold uppercase tracking-widest text-base-content/40">Research Goal</h3>
          <button v-if="!editing" class="btn btn-ghost btn-xs text-primary" @click="startEditing">✏️ Edit</button>
        </div>
        
        <div v-if="!editing" class="p-4 bg-base-200 rounded-xl relative group">
          <p class="text-xl font-medium leading-relaxed">{{ intent.inferred_intent }}</p>
        </div>
        
        <div v-else class="space-y-3">
          <textarea
            class="textarea textarea-bordered w-full text-lg leading-relaxed focus:textarea-primary"
            v-model="editedIntent"
            rows="3"
          ></textarea>
          <div class="flex justify-end gap-2">
            <button class="btn btn-ghost btn-sm" @click="cancelEdit">Cancel</button>
            <button class="btn btn-secondary btn-sm" @click="saveEdit">Save Changes</button>
          </div>
        </div>
      </div>

      <!-- Key Topics -->
      <div class="space-y-4" v-if="intent.key_topics?.length">
        <h3 class="text-xs font-bold uppercase tracking-widest text-base-content/40">Key Topics</h3>
        <div class="flex flex-wrap gap-2">
          <span class="badge badge-info badge-soft py-3 px-4 font-medium" v-for="topic in intent.key_topics" :key="topic">
            {{ topic }}
          </span>
        </div>
      </div>

      <!-- Scope Stats -->
      <div class="stats stats-vertical lg:stats-horizontal bg-base-200 border border-base-content/5 w-full">
        <div class="stat px-6" v-if="intent.scope?.num_papers">
          <div class="stat-title text-3xs font-bold uppercase tracking-widest">Papers</div>
          <div class="stat-value text-2xl">{{ intent.scope.num_papers }}</div>
        </div>
        
        <div class="stat px-6" v-if="intent.scope?.year_range">
          <div class="stat-title text-3xs font-bold uppercase tracking-widest">Period</div>
          <div class="stat-value text-2xl text-primary">{{ intent.scope.year_range }}</div>
        </div>

        <div class="stat px-6" v-if="intent.output_format">
          <div class="stat-title text-3xs font-bold uppercase tracking-widest">Format</div>
          <div class="stat-value text-lg break-words">{{ intent.output_format.replace(/_/g, ' ') }}</div>
        </div>
      </div>

      <!-- Suggested Sources -->
      <div class="space-y-3" v-if="intent.suggested_sources?.length">
        <h3 class="text-xs font-bold uppercase tracking-widest text-base-content/40">Suggested Sources</h3>
        <p class="text-sm opacity-70">{{ intent.suggested_sources.join(' • ') }}</p>
      </div>

      <!-- Action Bar -->
      <div class="card-actions mt-4">
        <button
          id="execute-btn"
          class="btn btn-primary btn-lg w-full shadow-lg shadow-primary/20"
          :disabled="loading"
          @click="$emit('execute', editedIntent || intent.inferred_intent)"
        >
          <span v-if="loading" class="loading loading-spinner"></span>
          <span v-else class="text-xl">🚀</span>
          {{ loading ? 'Starting Execution...' : 'Confirm & Execute Research' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  intent: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['execute'])

const editing = ref(false)
const editedIntent = ref('')

function startEditing() {
  editedIntent.value = props.intent.inferred_intent
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editedIntent.value = ''
}

function saveEdit() {
  editing.value = false
}
</script>

<style scoped>
/* Scoped styles kept minimal as we use Tailwind classes */
</style>
