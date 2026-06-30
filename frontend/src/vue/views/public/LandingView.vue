<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import PublicElectionPortalContent from "@/components/public/PublicElectionPortalContent.vue";
import { publicApi } from "@/api/public";
import { branding } from "@/config/branding";

const institutionBranding = ref(null);
const logoUrl = computed(() => institutionBranding.value?.logo_url || branding.institutionLogoUrl);

const faqs = [
  {
    q: "Who can vote?",
    a: "Registered students on the voter roll for each election. Eligibility is verified at login.",
  },
  {
    q: "How do I sign in?",
    a: "Use your index number or institutional email, then complete OTP and biometric verification when prompted.",
  },
  {
    q: "Can I vote more than once?",
    a: "No. Each eligible voter may submit one ballot per election.",
  },
  {
    q: "How are results released?",
    a: "Results are generated when voting closes, certified by the Electoral Commission, then published.",
  },
];

onMounted(async () => {
  institutionBranding.value = await publicApi.getBranding().catch(() => null);
});
</script>

<template>
  <div class="vb-page">
    <section class="vb-portal-hero">
      <div class="flex items-start gap-4">
        <img
          v-if="logoUrl"
          :src="logoUrl"
          :alt="branding.institutionName"
          class="h-11 w-11 shrink-0 rounded-lg bg-white object-contain p-1"
        />
        <div>
          <p class="text-xs font-medium text-brand-100">{{ branding.institutionName }}</p>
          <h1 class="vb-portal-hero-title">{{ branding.systemName }}</h1>
          <p class="vb-portal-hero-lead">{{ branding.tagline }}</p>
        </div>
      </div>

      <div class="vb-portal-hero-actions">
        <RouterLink to="/auth/login" class="vb-portal-hero-cta">Sign in to vote</RouterLink>
        <RouterLink to="/observe" class="vb-portal-hero-link">Observer portal</RouterLink>
        <RouterLink to="/#faq" class="vb-portal-hero-link">FAQ</RouterLink>
        <RouterLink to="/#support" class="vb-portal-hero-link">Support</RouterLink>
        <RouterLink to="/verify" class="vb-portal-hero-link">Verify results</RouterLink>
      </div>
    </section>

    <PublicElectionPortalContent />

    <section class="vb-portal-info-grid">
      <article class="vb-surface-panel">
        <h2 class="vb-section-title">How it works</h2>
        <ul class="mt-3 space-y-2 text-sm text-slate-600">
          <li>Secure, encrypted ballots with hidden rankings while voting is open</li>
          <li>Automated results when voting closes, then official certification</li>
          <li>Strong-room integrity checks and public verification hashes</li>
          <li>Full audit trails and separation of duties across election roles</li>
        </ul>
      </article>

      <article id="faq" class="vb-surface-panel scroll-mt-24">
        <h2 class="vb-section-title">Common questions</h2>
        <dl class="mt-3 space-y-3">
          <div v-for="item in faqs" :key="item.q">
            <dt class="text-sm font-medium text-slate-800">{{ item.q }}</dt>
            <dd class="mt-0.5 text-sm text-slate-600">{{ item.a }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section id="support" class="rounded-card border border-border bg-surface px-card py-5 text-center scroll-mt-24">
      <p class="text-sm text-slate-600">
        Need help? Contact the Electoral Commission at
        <a class="font-medium text-brand-700 hover:underline" :href="`mailto:${branding.electionOfficeEmail}`">
          {{ branding.electionOfficeEmail }}
        </a>
        or {{ branding.electionOfficePhone }}.
      </p>
    </section>
  </div>
</template>
