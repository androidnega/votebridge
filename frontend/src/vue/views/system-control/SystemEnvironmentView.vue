<script setup>
import { onMounted } from "vue";
import { StatCard } from "@/components/dashboard";
import { systemControlNav } from "@/config/moduleNav";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();

onMounted(() => store.fetchEnvironment().catch(() => {}));
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Environment"
      subtitle="Runtime environment and deployment information (read-only)."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'System Control', to: '/system-control' }, { label: 'Environment' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.environment" variant="stats" :rows="4" />

    <template v-else-if="store.environment">
      <section class="grid grid-cols-1 gap-4 xs:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Python" :value="store.environment.python_version" accent="slate" />
        <StatCard label="Django" :value="store.environment.django_version" accent="brand" />
        <StatCard label="Deployment" :value="store.environment.deployment_mode" accent="green" />
        <StatCard label="Redis" :value="store.environment.redis_status" accent="amber" />
      </section>
      <VCard title="System details">
        <dl class="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
          <div><dt class="text-slate-500">PostgreSQL</dt><dd>{{ store.environment.postgresql_version || '—' }}</dd></div>
          <div><dt class="text-slate-500">Operating system</dt><dd>{{ store.environment.operating_system }}</dd></div>
          <div><dt class="text-slate-500">CPU cores</dt><dd>{{ store.environment.cpu_count ?? '—' }}</dd></div>
          <div><dt class="text-slate-500">RAM (GB)</dt><dd>{{ store.environment.ram_gb ?? '—' }}</dd></div>
          <div><dt class="text-slate-500">Disk (GB)</dt><dd>{{ store.environment.disk_gb ?? '—' }}</dd></div>
          <div><dt class="text-slate-500">Uptime (seconds)</dt><dd>{{ store.environment.uptime_seconds ?? '—' }}</dd></div>
        </dl>
      </VCard>
    </template>
  </div>
</template>
