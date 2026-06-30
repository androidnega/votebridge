<script setup>
defineProps({
  title: String,
  subtitle: String,
  padding: {
    type: String,
    default: "md",
  },
  hoverable: Boolean,
});

const paddingClasses = {
  none: "p-0",
  sm: "p-4",
  md: "p-card",
  lg: "p-8",
};
</script>

<template>
  <section
    class="rounded-card border border-border bg-white shadow-card vb-fade-in"
    :class="[
      paddingClasses[padding],
      hoverable ? 'transition hover:shadow-md' : '',
    ]"
  >
    <header v-if="title || subtitle || $slots.header" class="mb-4">
      <slot name="header">
        <h3 v-if="title" class="text-lg font-semibold text-ink-primary">{{ title }}</h3>
        <p v-if="subtitle" class="mt-1 text-sm text-ink-secondary">{{ subtitle }}</p>
      </slot>
    </header>
    <slot />
    <footer v-if="$slots.footer" class="mt-4 border-t border-border pt-4">
      <slot name="footer" />
    </footer>
  </section>
</template>
