<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { VAlert, VButton, PageHeader } from "@/components/ui";
import { emptyStates } from "@/config/emptyStates";
import { useAuthStore } from "@/stores/auth";
import { useStrongroomStore } from "@/stores/strongroom";

const router = useRouter();
const authStore = useAuthStore();
const strongroomStore = useStrongroomStore();

onMounted(() => {
  strongroomStore.fetchElections().catch(() => {});
  if (authStore.isSuperAdmin) {
    strongroomStore.connectRealtime();
  }
});

onUnmounted(() => {
  strongroomStore.disconnectRealtime();
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Strong room"
      subtitle="Certification, integrity verification, chain of custody, and audit history."
    >
      <template #actions>
        <ConnectionStatusIndicator
          v-if="authStore.isSuperAdmin"
          :status="strongroomStore.realtimeStatus"
        />
        <VButton variant="secondary" size="sm" @click="router.push('/verify')">
          Public verification
        </VButton>
      </template>
    </PageHeader>

    <section class="vb-vault-shell" aria-label="Strong room principles">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article class="vb-vault-panel">
          <p class="vb-vault-caption">Certification</p>
          <p class="mt-2 text-sm text-slate-200">Commission review before publication.</p>
        </article>
        <article class="vb-vault-panel">
          <p class="vb-vault-caption">Integrity</p>
          <p class="mt-2 text-sm text-slate-200">Cryptographic verification of ballot seals.</p>
        </article>
        <article class="vb-vault-panel">
          <p class="vb-vault-caption">Chain of custody</p>
          <p class="mt-2 text-sm text-slate-200">Immutable custody events and timestamps.</p>
        </article>
        <article class="vb-vault-panel">
          <p class="vb-vault-caption">Audit history</p>
          <p class="mt-2 text-sm text-slate-200">Full trail for independent observers.</p>
        </article>
      </div>
    </section>

    <VAlert v-if="strongroomStore.error" variant="error">{{ strongroomStore.error }}</VAlert>

    <LoadingSkeleton v-if="strongroomStore.loading && !strongroomStore.elections.length" variant="list" :rows="4" />

    <section v-else class="vb-table-shell">
      <EmptyState v-if="!strongroomStore.elections.length" v-bind="emptyStates.strongroom" />
      <ul v-else class="vb-divider-list">
        <li
          v-for="item in strongroomStore.elections"
          :key="item.election_uuid"
          class="flex flex-col gap-4 p-card sm:flex-row sm:items-center sm:justify-between"
        >
          <div class="min-w-0">
            <p class="font-semibold text-slate-900">{{ item.election_title }}</p>
            <div class="mt-2 flex flex-wrap items-center gap-2">
              <span class="vb-status-pill bg-slate-100 text-slate-700 ring-slate-200 capitalize">
                Seal: {{ item.seal_status }}
              </span>
              <span v-if="item.integrity_score != null" class="vb-caption">
                Integrity {{ item.integrity_score }}%
              </span>
            </div>
          </div>
          <VButton
            size="sm"
            @click="router.push(`/dashboard/strongroom/${item.election_uuid}`)"
          >
            Open vault
          </VButton>
        </li>
      </ul>
    </section>
  </div>
</template>
