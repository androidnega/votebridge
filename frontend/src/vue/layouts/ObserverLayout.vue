<script setup>
import { RouterLink, RouterView } from "vue-router";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="flex h-screen flex-col overflow-hidden bg-surface-muted">
    <header class="shrink-0 border-b border-border bg-surface">
      <div class="mx-auto flex h-14 max-w-wide items-center justify-between px-4 sm:px-8">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <div
            class="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 text-[10px] font-bold text-white"
            aria-hidden="true"
          >
            VB
          </div>
          <div class="leading-tight">
            <p class="text-sm font-semibold text-slate-800">{{ branding.systemName }}</p>
            <p class="text-[11px] text-slate-500">Observer feed</p>
          </div>
        </RouterLink>
        <nav class="flex items-center gap-2 sm:gap-3">
          <RouterLink
            to="/"
            class="hidden min-h-touch items-center px-3 text-sm text-slate-600 hover:text-slate-900 sm:inline-flex"
          >
            Public home
          </RouterLink>
          <RouterLink
            to="/auth/login"
            class="inline-flex min-h-touch items-center rounded-input border border-slate-800 bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800"
          >
            Sign in
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto flex min-h-0 w-full max-w-wide flex-1 flex-col px-4 py-3 sm:px-8 sm:py-4">
      <RouterView />
    </main>
  </div>
</template>
