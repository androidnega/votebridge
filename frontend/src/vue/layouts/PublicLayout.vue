<script setup>
import { RouterLink, RouterView } from "vue-router";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <header class="border-b border-border bg-surface">
      <div class="mx-auto flex h-topbar max-w-content items-center justify-between px-4 sm:px-page">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-[11px] font-bold text-white"
            aria-hidden="true"
          >
            VB
          </div>
          <div class="leading-tight">
            <p class="text-sm font-semibold text-slate-800">{{ branding.systemName }}</p>
            <p class="hidden text-xs text-slate-500 sm:block">{{ branding.institutionName }}</p>
          </div>
        </RouterLink>
        <nav class="flex items-center gap-3 sm:gap-5">
          <RouterLink
            to="/observe"
            class="hidden min-h-touch items-center text-sm text-slate-600 hover:text-brand-700 sm:inline-flex"
          >
            Observer portal
          </RouterLink>
          <RouterLink
            to="/#faq"
            class="hidden min-h-touch items-center text-sm text-slate-600 hover:text-brand-700 sm:inline-flex"
          >
            FAQ
          </RouterLink>
          <RouterLink
            to="/#support"
            class="hidden min-h-touch items-center text-sm text-slate-600 hover:text-brand-700 md:inline-flex"
          >
            Support
          </RouterLink>
          <RouterLink
            to="/auth/login"
            class="inline-flex min-h-touch items-center rounded-input bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-hover"
          >
            Sign in
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-content px-4 py-8 sm:px-page sm:py-10">
      <RouterView />
    </main>

    <footer class="border-t border-border bg-surface py-5">
      <p class="text-center text-xs text-slate-500">
        &copy; {{ new Date().getFullYear() }} {{ branding.institutionName }} · {{ branding.systemName }}
      </p>
    </footer>
  </div>
</template>
