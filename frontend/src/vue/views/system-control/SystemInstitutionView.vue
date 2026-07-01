<script setup>
import { onMounted, reactive } from "vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const form = reactive({
  institution_name: "",
  short_name: "",
  primary_color: "",
  secondary_color: "",
  academic_year: "",
  campus: "",
  contact_email: "",
  contact_phone: "",
  election_office_email: "",
  election_office_phone: "",
  footer_text: "",
});

onMounted(async () => {
  try {
    const data = await store.fetchInstitution();
    Object.assign(form, data);
  } catch {
    /* handled in store */
  }
});

async function previewChanges() {
  const data = await store.saveInstitution({ ...form }, true);
  toast.info("Preview generated — review before saving.");
  return data;
}

async function saveChanges() {
  await store.saveInstitution({ ...form });
  toast.success("Institution settings saved.");
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Institution Settings"
      subtitle="Configure institution identity and contact information."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Institution', to: r.institution.hub }, { label: 'Institution profile' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.institution" variant="list" :rows="8" />

    <VCard v-else title="Institution profile">
      <form class="grid grid-cols-1 gap-4 md:grid-cols-2" @submit.prevent="saveChanges">
        <VInput v-model="form.institution_name" label="Institution name" />
        <VInput v-model="form.short_name" label="Short name" />
        <VInput v-model="form.primary_color" label="Primary colour" />
        <VInput v-model="form.secondary_color" label="Secondary colour" />
        <VInput v-model="form.academic_year" label="Academic year" />
        <VInput v-model="form.campus" label="Campus" />
        <VInput v-model="form.contact_email" label="Contact email" />
        <VInput v-model="form.contact_phone" label="Contact phone" />
        <VInput v-model="form.election_office_email" label="Election office email" />
        <VInput v-model="form.election_office_phone" label="Election office phone" />
        <VInput v-model="form.footer_text" label="Footer text" class="md:col-span-2" />
        <div class="flex flex-wrap gap-3 md:col-span-2">
          <VButton type="button" variant="secondary" @click="previewChanges">Preview</VButton>
          <VButton type="submit" variant="primary" :loading="store.actionLoading">Save changes</VButton>
        </div>
      </form>
    </VCard>
  </div>
</template>
