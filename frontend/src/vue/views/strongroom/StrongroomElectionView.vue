<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton, EmptyState } from "@/components/dashboard";
import {
  CustodyTimeline,
  ElectionSealCard,
  IntegrityStatusCard,
} from "@/components/strongroom";
import { VAlert, VButton, PageHeader } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useStrongroomStore } from "@/stores/strongroom";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const strongroomStore = useStrongroomStore();

const electionUuid = computed(() => route.params.electionUuid);
const dashboard = computed(() => strongroomStore.dashboard);

onMounted(() => {
  strongroomStore.fetchDashboard(electionUuid.value).catch(() => {});
  if (authStore.isSuperAdmin) {
    strongroomStore.connectRealtime();
  }
});

onUnmounted(() => {
  strongroomStore.disconnectRealtime();
  strongroomStore.clearDashboard();
});

async function runVerification() {
  await strongroomStore.verifyIntegrity(electionUuid.value);
}

async function lockElection() {
  await strongroomStore.lockElection(electionUuid.value);
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      :title="dashboard?.election_title || 'Election vault'"
      subtitle="Integrity verification, custody chain, and audit history."
      :breadcrumbs="[
        { label: 'Strong room', to: '/dashboard/strongroom' },
        { label: dashboard?.election_title || 'Election' },
      ]"
    />

    <VAlert v-if="strongroomStore.error" variant="error">{{ strongroomStore.error }}</VAlert>
    <LoadingSkeleton v-if="strongroomStore.loading && !dashboard" variant="card" />

    <template v-else-if="dashboard">
      <section class="vb-vault-shell">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <IntegrityStatusCard :score="dashboard.integrity_score" />
          <div class="vb-vault-panel">
            <p class="vb-vault-caption">Ballot seals</p>
            <p class="mt-2 text-3xl font-bold tabular-nums text-slate-100">
              {{ dashboard.ballot_seals_count ?? 0 }}
            </p>
          </div>
          <ElectionSealCard
            :status="dashboard.seal_status"
            :sealed-at="dashboard.sealed_at"
            :locked-at="dashboard.locked_at"
            :verification-hash="dashboard.verification_hash"
          />
        </div>
      </section>

      <section v-if="authStore.isSuperAdmin" class="flex flex-wrap gap-2">
        <VButton :loading="strongroomStore.actionLoading" @click="runVerification">
          Run integrity verification
        </VButton>
        <VButton
          v-if="dashboard.seal_status === 'sealed'"
          variant="secondary"
          :loading="strongroomStore.actionLoading"
          @click="lockElection"
        >
          Lock election
        </VButton>
        <VButton
          v-if="dashboard.verification_hash"
          variant="secondary"
          @click="router.push({ path: '/verify', query: { election: electionUuid, hash: dashboard.verification_hash } })"
        >
          Export verification
        </VButton>
        <VButton variant="secondary" @click="router.push({ name: 'strongroom-audit' })">
          View audit trail
        </VButton>
      </section>

      <section class="vb-vault-panel bg-slate-800/70">
        <h3 class="vb-section-title !text-slate-100">Verification history</h3>
        <EmptyState
          v-if="!dashboard.verification_history?.length"
          class="mt-4 border-slate-600 bg-slate-900/40"
          title="No verifications yet"
          description="Run an integrity verification to record the first audit result."
          icon="shield-check"
        />
        <ul v-else class="mt-4 space-y-2">
          <li
            v-for="item in dashboard.verification_history"
            :key="item.uuid"
            class="flex items-center justify-between rounded-input bg-slate-900/50 px-3 py-2 text-sm text-slate-200"
          >
            <span class="capitalize">{{ item.verification_type }}</span>
            <span :class="item.is_valid ? 'text-success-600' : 'text-danger-600'">
              {{ item.integrity_score }}% — {{ item.is_valid ? "Valid" : "Invalid" }}
            </span>
          </li>
        </ul>
      </section>

      <CustodyTimeline
        :items="dashboard.custody_timeline || []"
        :loading="strongroomStore.loading"
      />
    </template>

    <EmptyState
      v-else-if="!strongroomStore.loading && strongroomStore.error"
      title="Unable to load strongroom"
      :description="strongroomStore.error"
      icon="alert-triangle"
    />
  </div>
</template>
