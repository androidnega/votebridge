<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { CustodyTimeline } from "@/components/strongroom";
import { LoadingSkeleton, VAlert, VButton, VCard } from "@/components/ui";
import { useStrongroomStore } from "@/stores/strongroom";

const route = useRoute();
const router = useRouter();
const store = useStrongroomStore();

const sessionUuid = computed(() => route.params.sessionUuid);
const electionUuid = computed(() => route.params.uuid);
const activeSection = ref("overview");
const pollTimer = ref(null);

const evidence = computed(() => store.vaultEvidence?.evidence);
const session = computed(() => store.vaultEvidence);

const sections = [
  { id: "overview", label: "Election Overview" },
  { id: "integrity", label: "Integrity Summary" },
  { id: "certification", label: "Certification Summary" },
  { id: "custody", label: "Chain of Custody" },
  { id: "audit", label: "Audit Summary" },
  { id: "investigations", label: "Investigation Outcomes" },
  { id: "export", label: "Evidence Export" },
];

async function loadEvidence() {
  try {
    await store.fetchVaultEvidence(sessionUuid.value);
  } catch {
    router.replace({
      name: "election-vault-access",
      params: { uuid: electionUuid.value },
    });
  }
}

async function closeVault() {
  await store.closeVaultSession(sessionUuid.value);
  router.push({ name: "election-vault-access", params: { uuid: electionUuid.value } });
}

onMounted(async () => {
  await loadEvidence();
  pollTimer.value = window.setInterval(async () => {
    const status = await store.fetchVaultSession(sessionUuid.value).catch(() => null);
    if (status?.status === "resealed" || status?.status === "expired") {
      router.replace({ name: "election-vault-access", params: { uuid: electionUuid.value } });
    }
  }, 30000);
});

onUnmounted(() => {
  if (pollTimer.value) window.clearInterval(pollTimer.value);
});
</script>

<template>
  <div class="vb-page">
    <div class="vb-vault-shell mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-lg font-semibold text-white">Election vault</h2>
        <p class="text-sm text-slate-400">
          Session active · expires {{ session?.expires_at ? new Date(session.expires_at).toLocaleString() : "—" }}
        </p>
      </div>
      <VButton variant="secondary" size="sm" @click="closeVault">Close vault</VButton>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !evidence" variant="card" />

    <template v-else-if="evidence">
      <nav class="mb-4 flex flex-wrap gap-2">
        <button
          v-for="section in sections"
          :key="section.id"
          type="button"
          class="rounded-input border px-3 py-2 text-sm font-medium transition"
          :class="
            activeSection === section.id
              ? 'border-brand-600 bg-brand-600 text-white'
              : 'border-border bg-white text-ink-primary hover:bg-surface-muted'
          "
          @click="activeSection = section.id"
        >
          {{ section.label }}
        </button>
      </nav>

      <VCard v-if="activeSection === 'overview'">
        <dl class="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt class="text-ink-secondary">Title</dt><dd class="font-medium">{{ evidence.election_overview?.title }}</dd></div>
          <div><dt class="text-ink-secondary">Status</dt><dd class="font-medium capitalize">{{ evidence.election_overview?.status }}</dd></div>
          <div><dt class="text-ink-secondary">Seal</dt><dd class="font-medium capitalize">{{ evidence.election_overview?.seal_status }}</dd></div>
        </dl>
      </VCard>

      <VCard v-else-if="activeSection === 'integrity'">
        <dl class="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt class="text-ink-secondary">Integrity score</dt><dd class="text-2xl font-semibold">{{ evidence.integrity_summary?.integrity_score ?? "—" }}%</dd></div>
          <div><dt class="text-ink-secondary">Ballot seals</dt><dd class="font-medium">{{ evidence.integrity_summary?.ballot_seals_count }}</dd></div>
          <div class="sm:col-span-2"><dt class="text-ink-secondary">Verification hash</dt><dd class="break-all font-mono text-xs">{{ evidence.integrity_summary?.verification_hash }}</dd></div>
        </dl>
      </VCard>

      <VCard v-else-if="activeSection === 'certification'">
        <pre class="overflow-x-auto text-xs text-ink-secondary">{{ JSON.stringify(evidence.certification_summary, null, 2) || "No certification data." }}</pre>
      </VCard>

      <VCard v-else-if="activeSection === 'custody'">
        <CustodyTimeline :items="evidence.chain_of_custody || []" />
      </VCard>

      <VCard v-else-if="activeSection === 'audit'">
        <pre class="overflow-x-auto text-xs text-ink-secondary">{{ JSON.stringify(evidence.audit_summary, null, 2) || "No audit summary." }}</pre>
      </VCard>

      <VCard v-else-if="activeSection === 'investigations'">
        <pre class="overflow-x-auto text-xs text-ink-secondary">{{ JSON.stringify(evidence.investigation_outcomes, null, 2) || "No investigations." }}</pre>
      </VCard>

      <VCard v-else-if="activeSection === 'export'">
        <p class="text-sm text-ink-secondary">Export session evidence as structured JSON for institutional records.</p>
        <p class="mt-2 font-mono text-xs text-ink-primary">Session: {{ evidence.evidence_export?.session_uuid }}</p>
      </VCard>
    </template>
  </div>
</template>
