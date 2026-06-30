<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});
</script>

<template>
  <section class="rounded-card border border-[#E5E7EB] bg-white p-6 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)]">
    <header class="mb-5">
      <h3 class="text-base font-semibold text-[#1F2937]">{{ title }}</h3>
      <p v-if="subtitle" class="mt-1 text-sm text-[#64748B]">{{ subtitle }}</p>
    </header>
    <slot />
  </section>
</template>
