<script setup>
import { onMounted } from "vue";
import SettingsForm from "@/components/system-control/SettingsForm.vue";
import { systemControlNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();

onMounted(() => store.fetchRuntime().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Runtime Configuration"
      subtitle="Adjust runtime values without redeploying where supported."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'System Control', to: '/dashboard/system-control' }, { label: 'Runtime' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.runtime" variant="list" :rows="3" />
    <VCard v-else title="Runtime settings">
      <p class="mb-4 text-sm text-slate-600">{{ store.runtime?.note }}</p>
      <SettingsForm
        :items="store.runtime?.runtime || []"
        :loading="store.actionLoading"
        @save="(updates) => store.saveSettings('runtime', updates)"
      />
    </VCard>
  </div>
</template>
