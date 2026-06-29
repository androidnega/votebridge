<script setup>
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ConnectionStatusIndicator, EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { VAlert, VButton } from "@/components/ui";
import { useAuthStore } from "@/stores/auth";
import { useStrongroomStore } from "@/stores/strongroom";

const router = useRouter();
const authStore = useAuthStore();
const strongroomStore = useStrongroomStore();

onMounted(() => {
  strongroomStore.fetchElections().catch(() => {});
  if (authStore.isAdmin) {
    strongroomStore.connectRealtime();
  }
});

onUnmounted(() => {
  strongroomStore.disconnectRealtime();
});
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h2 class="text-2xl font-bold text-slate-900">Strong room overview</h2>
          <ConnectionStatusIndicator
            v-if="authStore.isAdmin"
            :status="strongroomStore.realtimeStatus"
          />
        </div>
        <p class="mt-1 text-sm text-slate-500">
          Election seals, integrity scores, and custody records.
        </p>
      </div>
      <VButton variant="secondary" size="sm" @click="router.push('/verify')">
        Public verification
      </VButton>
    </div>

    <VAlert v-if="strongroomStore.error" variant="error">{{ strongroomStore.error }}</VAlert>

    <LoadingSkeleton v-if="strongroomStore.loading && !strongroomStore.elections.length" variant="list" :rows="4" />

    <section v-else class="rounded-xl bg-white shadow-sm ring-1 ring-slate-900/5">
      <EmptyState
        v-if="!strongroomStore.elections.length"
        title="No sealed elections yet"
        description="Ballots are sealed automatically after submission. Certified elections appear here once results are processed."
        icon="🔒"
      />
      <ul v-else class="divide-y divide-slate-100">
        <li
          v-for="item in strongroomStore.elections"
          :key="item.election_uuid"
          class="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p class="font-medium text-slate-900">{{ item.election_title }}</p>
            <p class="mt-1 text-xs capitalize text-slate-500">Seal: {{ item.seal_status }}</p>
          </div>
          <VButton
            size="sm"
            variant="secondary"
            @click="router.push(`/strongroom/${item.election_uuid}`)"
          >
            Open dashboard
          </VButton>
        </li>
      </ul>
    </section>
  </div>
</template>
