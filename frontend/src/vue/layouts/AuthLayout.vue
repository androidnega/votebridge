<script setup>
import { RouterView } from "vue-router";
import { branding } from "@/config/branding";
</script>

<template>
  <div class="flex min-h-screen bg-surface-muted">
    <div
      class="hidden w-1/2 flex-col justify-between bg-brand-800 p-12 text-white lg:flex"
    >
      <div>
        <div class="flex items-center gap-3">
          <div
            class="flex h-12 w-12 items-center justify-center rounded-card bg-white/10 text-lg font-bold"
            aria-hidden="true"
          >
            VB
          </div>
          <div>
            <p class="text-lg font-semibold">{{ branding.systemName }}</p>
            <p class="text-sm text-brand-100">{{ branding.tagline }}</p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <h2 class="text-3xl font-semibold leading-tight">
          Trusted campus elections, built for integrity.
        </h2>
        <p class="max-w-md text-brand-100">
          Secure authentication, real-time monitoring, and auditable results for
          {{ branding.institutionName }}.
        </p>
      </div>

      <p class="text-xs text-brand-200">
        &copy; {{ new Date().getFullYear() }} {{ branding.institutionName }}
      </p>
    </div>

    <div class="flex flex-1 flex-col justify-center px-4 py-12 sm:px-8 lg:px-16">
      <div class="mx-auto w-full max-w-md">
        <div class="mb-8 text-center lg:text-left">
          <div class="mb-6 flex flex-col items-center gap-4 lg:items-start">
            <div class="flex items-center gap-3">
              <div
                class="flex h-11 w-11 items-center justify-center rounded-card bg-brand-600 text-sm font-bold text-white"
                aria-hidden="true"
              >
                VB
              </div>
              <img
                v-if="branding.institutionLogoUrl"
                :src="branding.institutionLogoUrl"
                :alt="`${branding.institutionName} logo`"
                class="h-11 w-auto object-contain"
              />
            </div>
            <div>
              <h1 class="text-2xl font-semibold text-slate-800">
                {{ branding.systemName }}
              </h1>
              <p class="mt-1 text-sm text-slate-500">{{ branding.institutionName }}</p>
              <p class="mt-0.5 text-sm font-medium text-brand-600">
                {{ branding.tagline }}
              </p>
            </div>
          </div>
        </div>

        <div class="rounded-card bg-white p-card shadow-card ring-1 ring-slate-900/5">
          <RouterView />
        </div>
      </div>
    </div>
  </div>
</template>
