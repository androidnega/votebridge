<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { VAlert, VButton, VTable } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();

const columns = [
  { key: "code", label: "Code" },
  { key: "name", label: "Name" },
  { key: "channel", label: "Channel" },
  { key: "placeholders", label: "Placeholders" },
];

onMounted(() => {
  store.fetchTemplates().catch(() => {});
});
</script>

<template>
  <div class="space-y-8">
    <div>
      <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/dashboard/communications')">
        ← Back
      </VButton>
      <h2 class="text-2xl font-bold text-slate-900">Notification templates</h2>
      <p class="mt-1 text-sm text-slate-500">Database-stored templates with placeholder support.</p>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.templates.length" variant="list" :rows="5" />

    <template v-else-if="store.templates.length">
      <div class="hidden md:block">
        <VTable :columns="columns" :rows="store.templates" empty-message="No templates.">
          <template #cell-channel="{ row }">
            <span class="capitalize">{{ row.channel }}</span>
          </template>
          <template #cell-placeholders="{ row }">
            {{ (row.placeholders || []).join(", ") || "—" }}
          </template>
        </VTable>
      </div>

      <div class="space-y-3 md:hidden">
        <article
          v-for="row in store.templates"
          :key="row.uuid"
          class="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-900/5"
        >
          <p class="font-medium text-slate-900">{{ row.name }}</p>
          <p class="text-xs text-slate-500">{{ row.code }} · {{ row.channel }}</p>
        </article>
      </div>
    </template>

    <EmptyState
      v-else
      title="No templates"
      description="Templates are seeded via migration."
      icon="📝"
    />
  </div>
</template>
