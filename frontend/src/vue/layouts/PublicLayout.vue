<script setup>
import { RouterLink, RouterView } from "vue-router";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <header class="border-b border-border bg-white">
      <div class="mx-auto flex h-topbar max-w-content items-center justify-between px-4 sm:px-page">
        <RouterLink to="/welcome" class="flex items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-xs font-bold text-white"
            aria-hidden="true"
          >
            VB
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-800">{{ branding.systemName }}</p>
            <p class="text-xs text-slate-500">{{ branding.institutionName }}</p>
          </div>
        </RouterLink>
        <RouterLink
          to="/auth/login"
          class="inline-flex min-h-touch items-center rounded-input bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
        >
          Sign in
        </RouterLink>
      </div>
    </header>

    <main class="mx-auto max-w-content px-4 py-page sm:px-page">
      <RouterView />
    </main>

    <footer class="border-t border-border bg-white py-6">
      <p class="text-center text-xs text-slate-500">
        &copy; {{ new Date().getFullYear() }} {{ branding.institutionName }}
      </p>
    </footer>
  </div>
</template>
