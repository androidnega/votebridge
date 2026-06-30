<script setup>
import { computed } from "vue";
import { branding } from "@/config/branding";

defineProps({
  compact: { type: Boolean, default: false },
  logoOnly: { type: Boolean, default: false },
});

const logoUrl = computed(() => branding.institutionLogoUrl);
</script>

<template>
  <header class="text-center" :class="compact && !logoOnly ? '' : logoOnly ? '' : 'mb-2'">
    <img
      v-if="logoUrl"
      :src="logoUrl"
      alt=""
      class="mx-auto object-contain"
      :class="compact ? 'h-20 w-20 sm:h-24 sm:w-24' : 'h-16 w-16'"
      aria-hidden="true"
    />
    <template v-if="!logoOnly">
      <p class="mt-3 text-[11px] font-medium uppercase tracking-[0.18em] text-slate-500">
        {{ branding.institutionName }}
      </p>
      <h1 class="mt-1 text-xl font-semibold text-slate-900 sm:text-2xl">
        {{ branding.systemName }}
      </h1>
      <p v-if="!compact" class="mt-1 text-sm text-slate-500">{{ branding.tagline }}</p>
    </template>
  </header>
</template>
