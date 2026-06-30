<script setup>
import { onMounted } from "vue";
import { systemControlNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();

onMounted(() => store.fetchLicense().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="License"
      subtitle="Application license and support information."
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'System Control', to: '/dashboard/system-control' }, { label: 'License' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.license" variant="list" :rows="4" />
    <VCard v-else-if="store.license" title="License details">
      <dl class="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
        <div><dt class="text-slate-500">Version</dt><dd>{{ store.license.application_version }}</dd></div>
        <div><dt class="text-slate-500">Release channel</dt><dd>{{ store.license.release_channel }}</dd></div>
        <div><dt class="text-slate-500">Build</dt><dd>{{ store.license.build_number }}</dd></div>
        <div><dt class="text-slate-500">Institution license</dt><dd>{{ store.license.institution_license }}</dd></div>
        <div><dt class="text-slate-500">Support email</dt><dd>{{ store.license.support_email }}</dd></div>
        <div><dt class="text-slate-500">Support phone</dt><dd>{{ store.license.support_phone }}</dd></div>
        <div><dt class="text-slate-500">Developer</dt><dd>{{ store.license.developer }}</dd></div>
        <div><dt class="text-slate-500">Copyright</dt><dd>{{ store.license.copyright }}</dd></div>
      </dl>
    </VCard>
  </div>
</template>
