<script setup>
import { computed } from "vue";
import { branding } from "@/config/branding";

defineProps({
  compact: { type: Boolean, default: false },
});

const logoUrl = computed(() => branding.institutionLogoUrl);
</script>

<template>
  <header class="text-center" :class="compact ? 'mb-5' : 'mb-8'">
    <img
      v-if="logoUrl"
      :src="logoUrl"
      :alt="branding.institutionName"
      class="mx-auto object-contain"
      :class="compact ? 'h-12 w-12' : 'h-16 w-16'"
    />
    <p class="mt-3 text-[11px] font-medium uppercase tracking-[0.18em] text-slate-500">
      {{ branding.institutionName }}
    </p>
    <h1 class="mt-1 text-xl font-semibold text-slate-900 sm:text-2xl">
      {{ branding.systemName }}
    </h1>
    <p v-if="!compact" class="mt-1 text-sm text-slate-500">{{ branding.tagline }}</p>
  </header>
</template>
