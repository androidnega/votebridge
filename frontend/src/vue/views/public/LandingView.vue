<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { publicApi } from "@/api/public";
import { branding } from "@/config/branding";
import { VButton } from "@/components/ui";

const router = useRouter();
const loading = ref(true);
const campusStatus = ref({ phase: "before_election", election: null });
const institutionBranding = ref(null);

const phaseContent = {
  before_election: {
    badge: "Standby",
    badgeClass: "bg-slate-700 text-slate-200",
    headline: "Campus elections portal",
    message: "No active election cycle right now. Check back when the Electoral Commission publishes the next schedule.",
  },
  election_scheduled: {
    badge: "Scheduled",
    badgeClass: "bg-info-50 text-info-700 ring-info-200",
    headline: "Election scheduled",
    message: "Voting has not opened yet. Eligible students will be notified when ballots open.",
  },
  election_open: {
    badge: "Voting open",
    badgeClass: "bg-success-50 text-success-700 ring-success-200",
    headline: "Election in progress",
    message: "Voting is open. Sign in with your index number or email to cast your ballot securely.",
  },
  awaiting_certification: {
    badge: "Processing",
    badgeClass: "bg-warning-50 text-warning-700 ring-warning-200",
    headline: "Awaiting certification",
    message: "Voting has closed. Official results are being verified before publication.",
  },
  results_published: {
    badge: "Results published",
    badgeClass: "bg-brand-50 text-brand-700 ring-brand-200",
    headline: "Official results available",
    message: "Certified results have been published. Sign in to review outcomes for your elections.",
  },
};

const phase = computed(() => phaseContent[campusStatus.value.phase] || phaseContent.before_election);
const election = computed(() => campusStatus.value.election);
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
    a: "Results are generated after close, certified by the Electoral Commission, then published for students.",
  },
];

onMounted(async () => {
  try {
    const [status, brand] = await Promise.all([
      publicApi.getCampusElectionStatus(),
      publicApi.getBranding().catch(() => null),
    ]);
    campusStatus.value = status;
    institutionBranding.value = brand;
  } catch {
    /* keep defaults */
  } finally {
    loading.value = false;
  }
});

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
</script>

<template>
  <div class="space-y-section">
    <!-- Hero -->
    <section class="overflow-hidden rounded-card bg-brand-700 px-6 py-10 text-white sm:px-10 sm:py-14">
      <div class="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
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
          <p class="mt-2 text-sm text-brand-100/90">
            Secure, auditable campus elections — web, USSD, and strong-room integrity.
          </p>
          <div class="mt-6 flex flex-wrap gap-3">
            <VButton @click="router.push('/auth/login')">Sign in to vote</VButton>
            <VButton variant="secondary" class="!bg-white/10 !text-white !ring-white/30 hover:!bg-white/20" @click="router.push('/verify')">
              Verify results
            </VButton>
          </div>
        </div>
      </div>
    </section>

    <!-- Current election status -->
    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Current status</p>
          <h2 class="mt-1 text-xl font-semibold text-slate-900">{{ phase.headline }}</h2>
        </div>
        <span
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset"
          :class="phase.badgeClass"
        >
          {{ phase.badge }}
        </span>
      </div>
      <p v-if="loading" class="mt-4 h-4 w-2/3 animate-pulse rounded bg-slate-200" />
      <template v-else>
        <p class="mt-3 text-sm leading-relaxed text-slate-600">{{ phase.message }}</p>
        <dl v-if="election" class="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt class="text-slate-500">Election</dt>
            <dd class="font-medium text-slate-800">{{ election.title }}</dd>
          </div>
          <div v-if="election.start_date">
            <dt class="text-slate-500">Opens</dt>
            <dd class="font-medium text-slate-800">{{ formatDate(election.start_date) }}</dd>
          </div>
          <div v-if="election.end_date">
            <dt class="text-slate-500">Closes</dt>
            <dd class="font-medium text-slate-800">{{ formatDate(election.end_date) }}</dd>
          </div>
        </dl>
      </template>
    </section>

    <!-- Secure voting overview -->
    <section class="grid gap-4 md:grid-cols-3">
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Secure voting</h3>
        <p class="mt-2 text-sm text-slate-600">
          Ballots are encrypted end-to-end. Candidate rankings stay hidden while voting is open.
        </p>
      </article>
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Multi-channel access</h3>
        <p class="mt-2 text-sm text-slate-600">
          Vote on the web or via USSD where enabled. One voter, one ballot — enforced centrally.
        </p>
      </article>
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h3 class="font-semibold text-slate-900">Verifiable results</h3>
        <p class="mt-2 text-sm text-slate-600">
          Strong-room sealing and public verification hashes support independent integrity checks.
        </p>
      </article>
    </section>

    <!-- Voting process -->
    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">Voting process</h2>
      <ol class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <li class="rounded-input border border-border p-4">
          <span class="text-xs font-bold text-brand-700">1</span>
          <p class="mt-2 font-medium text-slate-800">Sign in</p>
          <p class="mt-1 text-sm text-slate-600">Index number or email, OTP, and biometric check.</p>
        </li>
        <li class="rounded-input border border-border p-4">
          <span class="text-xs font-bold text-brand-700">2</span>
          <p class="mt-2 font-medium text-slate-800">Select election</p>
          <p class="mt-1 text-sm text-slate-600">Review positions and candidate profiles.</p>
        </li>
        <li class="rounded-input border border-border p-4">
          <span class="text-xs font-bold text-brand-700">3</span>
          <p class="mt-2 font-medium text-slate-800">Cast ballot</p>
          <p class="mt-1 text-sm text-slate-600">Confirm choices; receive a secure voting token.</p>
        </li>
        <li class="rounded-input border border-border p-4">
          <span class="text-xs font-bold text-brand-700">4</span>
          <p class="mt-2 font-medium text-slate-800">Verify</p>
          <p class="mt-1 text-sm text-slate-600">Keep your token to confirm your vote was recorded.</p>
        </li>
      </ol>
    </section>

    <!-- Platform security & Why VoteBridge -->
    <section class="grid gap-4 lg:grid-cols-2">
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Platform security</h2>
        <ul class="mt-3 space-y-2 text-sm text-slate-600">
          <li>Role separation between election officers and electoral commissioners</li>
          <li>Trusted device registration and risk-based authentication</li>
          <li>Real-time fraud monitoring and audit trails</li>
          <li>Strong-room ballot custody with cryptographic verification</li>
        </ul>
      </article>
      <article class="rounded-card border border-border bg-surface p-card shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Why VoteBridge</h2>
        <ul class="mt-3 space-y-2 text-sm text-slate-600">
          <li>Built for TTU-scale campus elections with Ghanaian student workflows</li>
          <li>Mobile-first experience for students and election officers</li>
          <li>Enterprise dashboards for turnout, security, and certification</li>
          <li>Transparent publication after independent certification</li>
        </ul>
      </article>
    </section>

    <!-- FAQ -->
    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <h2 class="text-lg font-semibold text-slate-900">Frequently asked questions</h2>
      <dl class="mt-4 space-y-4">
        <div v-for="item in faqs" :key="item.q">
          <dt class="font-medium text-slate-800">{{ item.q }}</dt>
          <dd class="mt-1 text-sm text-slate-600">{{ item.a }}</dd>
        </div>
      </dl>
    </section>

    <!-- Support & Login -->
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
