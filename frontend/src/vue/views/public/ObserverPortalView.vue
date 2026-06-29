<script setup>
import { useRouter } from "vue-router";
import PublicElectionPortalContent from "@/components/public/PublicElectionPortalContent.vue";
import { branding } from "@/config/branding";
import { VButton } from "@/components/ui";

const router = useRouter();
</script>

<template>
  <div class="space-y-section">
    <section class="rounded-card border border-border bg-slate-900 px-6 py-8 text-white sm:px-8">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Election observer portal</p>
      <h1 class="mt-2 text-2xl font-bold sm:text-3xl">Public election transparency</h1>
      <p class="mt-2 max-w-2xl text-sm text-slate-300">
        Read-only view of {{ branding.institutionName }} election status, participation, and official announcements.
        No login required.
      </p>
      <div class="mt-4 flex flex-wrap gap-2">
        <VButton variant="secondary" class="!border-slate-600 !bg-slate-800 !text-white" @click="router.push('/welcome')">
          Public home
        </VButton>
        <VButton @click="router.push('/auth/login')">Sign in to vote</VButton>
      </div>
    </section>

    <PublicElectionPortalContent compact />
  </div>
</template>
