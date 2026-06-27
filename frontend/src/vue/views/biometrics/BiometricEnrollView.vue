<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import CameraCapture from "@/components/biometrics/CameraCapture.vue";
import { LoadingSkeleton, PageHeader, VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useBiometricsStore } from "@/stores/biometrics";
import { useToast } from "@/composables/useToast";

const router = useRouter();
const route = useRoute();
const store = useBiometricsStore();
const toast = useToast();

const captures = ref([]);
const userUuid = ref(route.query.user_uuid || "");
const submitError = ref("");

const poses = ["Look forward", "Blink", "Turn left", "Turn right"];
const stepsTotal = computed(() => store.enrollmentRequirements?.image_count || 10);
const currentPose = computed(() => {
  const idx = captures.value.length % poses.length;
  return poses[idx];
});

onMounted(async () => {
  await store.fetchEnrollmentRequirements();
});

async function handleFrame(frame) {
  captures.value.push(frame);
  if (captures.value.length >= stepsTotal.value) {
    await completeEnrollment();
  }
}

async function completeEnrollment() {
  submitError.value = "";
  if (!userUuid.value) {
    submitError.value = "Select a user to enroll.";
    return;
  }
  try {
    await store.enroll(userUuid.value, captures.value);
    toast.success("Biometric enrollment complete");
    await router.push({ name: "biometrics-history" });
  } catch (error) {
    submitError.value = error.message || store.error;
    captures.value = [];
  }
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Biometric enrollment"
      :breadcrumbs="[
        { label: 'System', to: '/system-control' },
        { label: 'Identity Assurance', to: '/system-control/identity-assurance' },
        { label: 'Enroll' },
      ]"
    />

    <VAlert v-if="submitError" variant="error">{{ submitError }}</VAlert>
    <LoadingSkeleton v-if="!store.enrollmentRequirements" variant="card" :rows="4" />

    <VCard v-else title="Enrollment wizard">
      <p class="mb-4 text-sm text-slate-600">
        Capture {{ stepsTotal }} images following pose prompts. Only Super Admin can enroll privileged users.
      </p>

      <VInput
        v-model="userUuid"
        label="User UUID"
        placeholder="Administrator UUID to enroll"
        class="mb-4"
      />

      <p class="mb-2 font-medium text-brand">{{ currentPose }}</p>
      <CameraCapture @frame="handleFrame" />
      <p class="mt-3 text-sm text-slate-500">Progress: {{ captures.length }} / {{ stepsTotal }}</p>

      <div class="mt-4 flex gap-4">
        <VButton
          variant="primary"
          :loading="store.actionLoading"
          :disabled="captures.length < stepsTotal"
          @click="completeEnrollment"
        >
          Complete enrollment
        </VButton>
        <VButton variant="secondary" @click="captures = []">Reset captures</VButton>
      </div>
    </VCard>
  </div>
</template>
