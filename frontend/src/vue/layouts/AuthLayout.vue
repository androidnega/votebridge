<script setup>
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import AuthHelpFab from "@/components/auth/AuthHelpFab.vue";
import { VIcon } from "@/components/ui";
import { branding } from "@/config/branding";

const route = useRoute();
const isInfoPage = computed(() => Boolean(route.meta.infoPage));

function blockImageSave(event) {
  event.preventDefault();
}
</script>

<template>
  <div
    v-if="isInfoPage"
    class="relative min-h-screen bg-surface-muted"
  >
    <header class="border-b border-border bg-white">
      <div class="mx-auto flex h-14 max-w-content items-center gap-3 px-4 sm:px-page">
        <RouterLink
          :to="{ name: 'auth-login' }"
          class="inline-flex min-h-touch items-center gap-2 text-sm font-medium text-brand-600 hover:text-brand-hover"
        >
          <VIcon name="chevronLeft" size="sm" />
          Sign in
        </RouterLink>
      </div>
    </header>

    <main class="mx-auto max-w-content px-4 py-8 sm:px-page">
      <RouterView />
    </main>

    <AuthHelpFab />
  </div>

  <div
    v-else
    class="relative flex min-h-screen flex-col bg-surface-muted lg:flex-row"
  >
    <section
      class="relative flex flex-col items-center justify-center overflow-hidden border-b border-slate-600 px-6 py-10 text-center lg:w-[58%] lg:flex-shrink-0 lg:border-b-0 lg:border-r lg:px-14 lg:py-12"
      @contextmenu.prevent="blockImageSave"
      @dragstart.prevent
    >
      <div
        class="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-60"
        :style="{ backgroundImage: `url(${branding.authPanelImageUrl})` }"
        aria-hidden="true"
      />
      <div class="absolute inset-0 bg-brand-900/80" aria-hidden="true" />

      <div class="relative z-10 w-full max-w-lg px-2 text-white">
        <div class="flex items-center gap-4 text-left sm:gap-5">
          <img
            v-if="branding.institutionLogoUrl"
            :src="branding.institutionLogoUrl"
            :alt="`${branding.institutionName} logo`"
            class="h-[3.25rem] w-[3.25rem] shrink-0 object-contain sm:h-14 sm:w-14 lg:h-16 lg:w-16"
            draggable="false"
            @contextmenu.prevent="blockImageSave"
          />

          <div
            class="min-w-0"
            :class="branding.institutionLogoUrl ? 'border-l border-white/25 pl-4 sm:pl-5' : ''"
          >
            <p class="auth-hero-eyebrow text-[0.6875rem] font-semibold uppercase tracking-[0.16em] text-slate-300">
              {{ branding.institutionName }}
            </p>
            <h1 class="auth-hero-headline mt-1 text-xl font-semibold leading-tight text-white sm:text-2xl lg:text-[1.625rem]">
              Student elections portal
            </h1>
            <p class="auth-hero-tagline mt-1.5 text-sm leading-snug text-slate-300/95">
              {{ branding.tagline }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <main class="flex flex-1 items-center justify-center px-4 py-8 lg:w-[42%] lg:px-10">
      <div class="w-full max-w-sm">
        <div class="rounded-card border border-border bg-white px-5 py-4 shadow-card">
          <RouterView />
        </div>
      </div>
    </main>

    <AuthHelpFab />
  </div>
</template>

<style scoped>
section {
  -webkit-user-select: none;
  user-select: none;
  -webkit-touch-callout: none;
}

.auth-hero-headline {
  font-family: Georgia, "Times New Roman", "Palatino Linotype", serif;
  letter-spacing: -0.02em;
}

.auth-hero-eyebrow {
  font-variant: small-caps;
  letter-spacing: 0.14em;
}

.auth-hero-tagline {
  font-weight: 400;
  letter-spacing: 0.01em;
}
</style>
