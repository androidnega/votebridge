<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LoadingSkeleton, StatCard, EmptyState } from "@/components/dashboard";
import {
  CustodyTimeline,
  ElectionSealCard,
  IntegrityStatusCard,
} from "@/components/strongroom";
import { VAlert, VButton } from "@/components/ui";
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
  if (authStore.isAdmin) {
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
  <div class="space-y-8">
    <div>
      <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/strongroom')">
        ← Back to strongroom
      </VButton>
      <h2 class="text-2xl font-bold text-slate-900">
        {{ dashboard?.election_title || "Election strongroom" }}
      </h2>
    </div>

    <VAlert v-if="strongroomStore.error" variant="error">{{ strongroomStore.error }}</VAlert>
    <LoadingSkeleton v-if="strongroomStore.loading && !dashboard" variant="card" />

    <template v-else-if="dashboard">
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <IntegrityStatusCard :score="dashboard.integrity_score" />
        <StatCard label="Ballot seals" :value="dashboard.ballot_seals_count ?? 0" accent="brand" />
        <ElectionSealCard
          :status="dashboard.seal_status"
          :sealed-at="dashboard.sealed_at"
          :locked-at="dashboard.locked_at"
          :verification-hash="dashboard.verification_hash"
        />
      </section>

      <section v-if="authStore.isAdmin" class="flex flex-wrap gap-2">
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
        <VButton variant="secondary" @click="router.push('/reports/export')">
          Export reports
        </VButton>
        <VButton variant="secondary" @click="router.push({ name: 'strongroom-audit' })">
          View audit trail
        </VButton>
      </section>

      <section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
        <h3 class="text-lg font-semibold text-slate-900">Verification history</h3>
        <EmptyState
          v-if="!dashboard.verification_history?.length"
          class="mt-4 border-0 bg-transparent"
          title="No verifications yet"
          description="Run an integrity verification to record the first audit result."
          icon="✓"
        />
        <ul v-else class="mt-4 space-y-2">
          <li
            v-for="item in dashboard.verification_history"
            :key="item.uuid"
            class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
          >
            <span class="capitalize">{{ item.verification_type }}</span>
            <span :class="item.is_valid ? 'text-green-700' : 'text-red-700'">
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
      icon="⚠"
    />
  </div>
</template>
