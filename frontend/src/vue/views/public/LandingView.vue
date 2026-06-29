<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import PublicElectionPortalContent from "@/components/public/PublicElectionPortalContent.vue";
import { publicApi } from "@/api/public";
import { branding } from "@/config/branding";
import { VButton } from "@/components/ui";

const router = useRouter();
const institutionBranding = ref(null);
const logoUrl = computed(() => institutionBranding.value?.logo_url || branding.institutionLogoUrl);

const faqs = [
  {
    q: "Who can vote?",
    a: "Registered students listed on the voter roll for each election. Your eligibility is verified at login.",
  },
  {
    q: "How do I sign in?",
    a: "Use your index number or institutional email, then complete OTP and biometric verification when prompted.",
  },
  {
    q: "Can I vote more than once?",
    a: "No. Each eligible voter may submit one ballot per election. Duplicate attempts are blocked automatically.",
  },
  {
    q: "How are results released?",
    a: "Results are generated automatically when voting closes, certified by the Electoral Commission, then published.",
  },
];

onMounted(async () => {
  institutionBranding.value = await publicApi.getBranding().catch(() => null);
});
</script>

<template>
  <div class="space-y-section">
    <section class="overflow-hidden rounded-card bg-brand-700 px-6 py-10 text-white sm:px-10 sm:py-14">
      <div class="max-w-2xl">
        <div class="flex items-center gap-3">
          <img
            v-if="logoUrl"
            :src="logoUrl"
            :alt="branding.institutionName"
            class="h-12 w-12 rounded-lg bg-white object-contain p-1"
          />
          <div>
            <p class="text-sm font-medium text-brand-100">{{ branding.institutionName }}</p>
            <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ branding.systemName }}</h1>
          </div>
        </div>
        <p class="mt-4 text-lg text-brand-100">{{ branding.tagline }}</p>
        <div class="mt-6 flex flex-wrap gap-3">
          <VButton @click="router.push('/auth/login')">Sign in to vote</VButton>
          <VButton
            variant="secondary"
            class="!bg-white/10 !text-white !ring-white/30 hover:!bg-white/20"
            @click="router.push('/observe')"
          >
            Observer portal
          </VButton>
          <VButton
            variant="secondary"
            class="!bg-white/10 !text-white !ring-white/30 hover:!bg-white/20"
            @click="router.push('/verify')"
          >
            Verify results
          </VButton>
        </div>
      </div>
    </section>

    <PublicElectionPortalContent />

    <section class="grid gap-4 md:grid-cols-3">
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Secure voting</h3>
        <p class="mt-2 text-sm text-slate-600">
          Ballots are encrypted end-to-end. Candidate rankings stay hidden while voting is open.
        </p>
      </article>
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Automated results</h3>
        <p class="mt-2 text-sm text-slate-600">
          Results are generated when voting closes, then certified before publication.
        </p>
      </article>
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Strong-room integrity</h3>
        <p class="mt-2 text-sm text-slate-600">
          Cryptographic verification supports independent audit of published outcomes.
        </p>
      </article>
    </section>

    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">Platform security</h2>
      <ul class="mt-3 space-y-2 text-sm text-slate-600">
        <li>Separation of duties between election officers and electoral commissioners</li>
        <li>Trusted device registration and risk-based authentication</li>
        <li>Real-time fraud monitoring with full audit trails</li>
        <li>Strong-room ballot custody with public verification hashes</li>
      </ul>
    </section>

    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">Frequently asked questions</h2>
      <dl class="mt-4 space-y-4">
        <div v-for="item in faqs" :key="item.q">
          <dt class="font-medium text-slate-800">{{ item.q }}</dt>
          <dd class="mt-1 text-sm text-slate-600">{{ item.a }}</dd>
        </div>
      </dl>
    </section>

    <section class="rounded-card bg-surface-muted p-card text-center">
      <h2 class="text-lg font-semibold text-slate-900">Need help?</h2>
      <p class="mt-2 text-sm text-slate-600">
        Contact the Electoral Commission office at
        <a class="text-brand-700 underline" :href="`mailto:${branding.electionOfficeEmail}`">{{ branding.electionOfficeEmail }}</a>
        or {{ branding.electionOfficePhone }}.
      </p>
      <VButton class="mt-4" @click="router.push('/auth/login')">Sign in</VButton>
    </section>
  </div>
</template>
