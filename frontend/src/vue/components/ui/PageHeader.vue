<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: String,
  breadcrumbs: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <header class="space-y-4">
    <nav v-if="breadcrumbs.length" aria-label="Breadcrumb">
      <ol class="flex flex-wrap items-center gap-2 text-sm text-ink-secondary">
        <li v-for="(crumb, index) in breadcrumbs" :key="index" class="flex items-center gap-2">
          <router-link
            v-if="crumb.to"
            :to="crumb.to"
            class="font-medium text-ink-secondary transition duration-150 hover:text-shell-accent"
          >
            {{ crumb.label }}
          </router-link>
          <span v-else class="font-medium text-ink-primary">{{ crumb.label }}</span>
          <span v-if="index < breadcrumbs.length - 1" aria-hidden="true">/</span>
        </li>
      </ol>
    </nav>

    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-ink-primary">{{ title }}</h1>
        <p v-if="subtitle" class="mt-1 text-sm text-ink-secondary">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="flex flex-wrap items-center gap-button-gap">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>
