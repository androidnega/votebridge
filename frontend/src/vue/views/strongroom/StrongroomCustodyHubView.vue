<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { PageHeader, VAlert, VButton } from "@/components/ui";
import { useStrongroomStore } from "@/stores/strongroom";

const router = useRouter();
const strongroomStore = useStrongroomStore();

onMounted(() => {
  strongroomStore.fetchElections().catch(() => {});
});
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Chain of custody"
      subtitle="Review sealed ballots and custody events by election."
      :breadcrumbs="[{ label: 'Strong room', to: '/dashboard/strongroom' }, { label: 'Chain of custody' }]"
    />

    <VAlert v-if="strongroomStore.error" variant="error">{{ strongroomStore.error }}</VAlert>
    <LoadingSkeleton
      v-if="strongroomStore.loading && !strongroomStore.elections.length"
      variant="list"
      :rows="4"
    />

    <section v-else class="rounded-xl bg-surface shadow-sm ring-1 ring-border">
      <EmptyState
        v-if="!strongroomStore.elections.length"
        title="No custody records yet"
        description="Custody timelines appear once elections are sealed."
      />
      <ul v-else class="divide-y divide-border">
        <li
          v-for="item in strongroomStore.elections"
          :key="item.election_uuid"
          class="flex flex-col gap-3 p-card sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <p class="font-medium text-slate-900">{{ item.election_title }}</p>
            <p class="text-sm text-slate-500">
              Integrity {{ item.integrity_score ?? "—" }}% · {{ item.custody_events ?? 0 }} custody events
            </p>
          </div>
          <VButton
            variant="secondary"
            size="sm"
            @click="router.push(`/dashboard/strongroom/${item.election_uuid}`)"
          >
            View timeline
          </VButton>
        </li>
      </ul>
    </section>
  </div>
</template>
