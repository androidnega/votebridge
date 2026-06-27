<script setup>
import { onMounted, reactive } from "vue";
import { systemControlNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const branding = reactive({
  login_background: "",
  email_header_color: "",
  sms_sender_name: "",
  public_verification_logo: "",
  pdf_header_text: "",
});

onMounted(async () => {
  const data = await store.fetchInstitution().catch(() => null);
  if (data?.branding) Object.assign(branding, data.branding);
});

async function saveBranding() {
  await store.saveInstitution({ branding: { ...branding } });
  toast.success("Branding updated.");
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Branding"
      subtitle="Logos, colours, and channel-specific branding assets."
      :breadcrumbs="[{ label: 'Overview', to: '/' }, { label: 'System Control', to: '/system-control' }, { label: 'Branding' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.institution" variant="list" :rows="5" />
    <VCard v-else title="Theme & channel branding">
      <form class="grid grid-cols-1 gap-4 md:grid-cols-2" @submit.prevent="saveBranding">
        <VInput v-model="branding.login_background" label="Login background URL" />
        <VInput v-model="branding.email_header_color" label="Email header colour" />
        <VInput v-model="branding.sms_sender_name" label="SMS sender name" />
        <VInput v-model="branding.public_verification_logo" label="Public verification logo URL" />
        <VInput v-model="branding.pdf_header_text" label="PDF header text" class="md:col-span-2" />
        <div class="md:col-span-2">
          <VButton type="submit" variant="primary" :loading="store.actionLoading">Save branding</VButton>
        </div>
      </form>
    </VCard>
  </div>
</template>
