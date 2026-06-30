<script setup>
import { onMounted, onUnmounted, ref } from "vue";

const props = defineProps({
  lines: {
    type: Array,
    required: true,
  },
  /** Minimum time to show terminal before emitting complete (ms) */
  minDuration: { type: Number, default: 1800 },
});

const emit = defineEmits(["complete"]);

const visibleLines = ref([]);
let lineTimer = null;
let completeTimer = null;
const startedAt = ref(0);

onMounted(() => {
  startedAt.value = Date.now();
  let index = 0;

  function showNext() {
    if (index < props.lines.length) {
      visibleLines.value.push({ text: props.lines[index], id: index });
      index += 1;
      lineTimer = window.setTimeout(showNext, 420);
      return;
    }

    const elapsed = Date.now() - startedAt.value;
    const remaining = Math.max(0, props.minDuration - elapsed);
    completeTimer = window.setTimeout(() => emit("complete"), remaining);
  }

  showNext();
});

onUnmounted(() => {
  if (lineTimer) window.clearTimeout(lineTimer);
  if (completeTimer) window.clearTimeout(completeTimer);
});
</script>

<template>
  <div class="vb-auth-terminal" aria-live="polite" aria-busy="true">
    <p class="vb-auth-terminal-label">Secure channel</p>
    <ul class="vb-auth-terminal-lines">
      <li v-for="line in visibleLines" :key="line.id" class="vb-auth-terminal-line">
        <span class="vb-auth-terminal-prompt">&gt;</span>
        {{ line.text }}
      </li>
      <li class="vb-auth-terminal-line vb-auth-terminal-cursor">
        <span class="vb-auth-terminal-prompt">&gt;</span>
        <span class="inline-block w-2 animate-pulse bg-slate-400" aria-hidden="true">&nbsp;</span>
      </li>
    </ul>
  </div>
</template>
