<script setup>
import { RouterView } from "vue-router";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <header class="border-b border-border bg-white shadow-sm">
      <div class="mx-auto flex max-w-content flex-col items-center gap-2 px-4 py-6 text-center sm:px-page">
        <div
          class="flex h-12 w-12 items-center justify-center rounded-card bg-brand-600 text-sm font-bold text-white"
          aria-hidden="true"
        >
          VB
        </div>
        <h1 class="text-xl font-semibold text-slate-800">{{ branding.systemName }}</h1>
        <p class="text-sm text-slate-500">Public verification portal</p>
      </div>
    </header>

    <main class="mx-auto max-w-content px-4 py-page sm:px-page">
      <RouterView />
    </main>
  </div>
</template>
