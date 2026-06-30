<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { VAlert, VButton, VCard } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();
const testResults = ref({});

onMounted(() => {
  store.fetchProviders().catch(() => {});
});

async function testConnection(uuid) {
  testResults.value[uuid] = await store.testProvider(uuid);
}
</script>

<template>
  <div class="space-y-8">
    <div>
      <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/dashboard/communications')">
        ← Back
      </VButton>
      <h2 class="text-2xl font-bold text-slate-900">Provider management</h2>
      <p class="mt-1 text-sm text-slate-500">Arkesel SMS and SMTP email providers.</p>
    </div>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.providers.length" variant="list" :rows="2" />

    <EmptyState
      v-else-if="!store.providers.length"
      title="No providers"
      description="Run migrations to seed default providers."
      icon="📡"
    />

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <VCard v-for="provider in store.providers" :key="provider.uuid" :title="provider.name">
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-slate-500">Type</dt>
            <dd class="capitalize text-slate-900">{{ provider.provider_type.replace(/_/g, " ") }}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-slate-500">Status</dt>
            <dd class="capitalize" :class="provider.connection_status === 'connected' ? 'text-green-700' : 'text-amber-700'">
              {{ provider.connection_status }}
            </dd>
          </div>
          <div v-if="provider.last_success_at" class="flex justify-between gap-4">
            <dt class="text-slate-500">Last success</dt>
            <dd class="text-slate-900">{{ new Date(provider.last_success_at).toLocaleString() }}</dd>
          </div>
          <div v-if="provider.last_error" class="rounded-lg bg-red-50 p-3 text-xs text-red-700">
            {{ provider.last_error }}
          </div>
        </dl>
        <VButton
          class="mt-4"
          size="sm"
          :loading="store.actionLoading"
          @click="testConnection(provider.uuid)"
        >
          Test connection
        </VButton>
        <VAlert
          v-if="testResults[provider.uuid]"
          class="mt-3"
          :variant="testResults[provider.uuid].success ? 'success' : 'error'"
        >
          {{ testResults[provider.uuid].message }}
        </VAlert>
      </VCard>
    </div>
  </div>
</template>
