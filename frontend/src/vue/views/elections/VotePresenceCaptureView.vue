<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VButton } from "@/components/ui";
import { useFacePresence } from "@/composables/useFacePresence";
import { useVotingStore } from "@/stores/voting";

const route = useRoute();
const router = useRouter();
const votingStore = useVotingStore();

const electionUuid = computed(() => route.params.uuid);
const previewImage = ref("");
const submitting = ref(false);
const submitError = ref("");
const photoCaptured = ref(false);

const {
  videoRef,
  faceDetected,
  statusText,
  statusKey,
  cameraError,
  engineError,
  takePhoto,
} = useFacePresence();

const electionTitle = computed(
  () =>
    votingStore.svtSession?.election_title ||
    votingStore.svtAccess?.election_title ||
    votingStore.ballot?.election_title ||
    ""
);

const statusClass = computed(() => {
  if (photoCaptured.value) return "text-success-700";
  if (statusKey.value === "face_detected") return "text-brand-700";
  if (statusKey.value === "camera_error" || statusKey.value === "engine_error") {
    return "text-danger-700";
  }
  return "text-ink-secondary";
});

const displayStatus = computed(() =>
  photoCaptured.value ? "Photo captured successfully" : statusText.value
);

const canTakePhoto = computed(
  () => faceDetected.value && !photoCaptured.value && !submitting.value
);

function handleTakePhoto() {
  if (!canTakePhoto.value) return;
  const frame = takePhoto();
  if (!frame) return;
  previewImage.value = frame;
  photoCaptured.value = true;
}

function handleRetake() {
  previewImage.value = "";
  photoCaptured.value = false;
}

function dataUrlToBlob(dataUrl) {
  const [header, base64] = dataUrl.split(",");
  const mime = header.match(/data:(.*?);/)?.[1] || "image/jpeg";
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: mime });
}

async function handleContinue() {
  if (!photoCaptured.value || !previewImage.value || submitting.value) return;
  submitting.value = true;
  submitError.value = "";
  try {
    const blob = dataUrlToBlob(previewImage.value);
    await votingStore.submitPresenceCapture(electionUuid.value, blob);
    router.push(`/dashboard/elections/${electionUuid.value}/vote`);
  } catch (error) {
    submitError.value = votingStore.error || error.message || "Unable to save your photo.";
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  votingStore.restoreSvtSession(electionUuid.value);
  if (!votingStore.hasValidatedBallotSession) {
    router.replace(`/dashboard/vote/verify/${electionUuid.value}`);
    return;
  }
  try {
    await votingStore.fetchPresenceStatus(electionUuid.value);
    if (!votingStore.needsPresenceCapture) {
      router.replace(`/dashboard/elections/${electionUuid.value}/vote`);
    }
  } catch {
    submitError.value = votingStore.error || "Unable to load presence check.";
  }
});
</script>

<template>
  <div class="w-full min-w-0 vb-vote-phase">
    <article class="w-full overflow-hidden rounded-card border border-border bg-surface p-5 shadow-card sm:p-6">
      <header class="mb-5 border-b border-border pb-4 text-center sm:text-left">
        <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">Pre-vote check</p>
        <h1 class="mt-1 text-xl font-semibold text-ink-primary sm:text-2xl">Confirm your presence</h1>
        <p class="mt-2 text-sm text-ink-secondary">
          Before entering the ballot, please take a quick photo for election integrity.
        </p>
        <p v-if="electionTitle" class="mt-2 text-sm font-medium text-brand-700">{{ electionTitle }}</p>
      </header>

      <div class="mx-auto w-full max-w-xl space-y-4">
        <div
          class="relative overflow-hidden rounded-card border border-border bg-surface-muted"
          :class="photoCaptured ? 'aspect-[4/3]' : 'aspect-[3/4] sm:aspect-[4/3]'"
        >
          <img
            v-if="photoCaptured && previewImage"
            :src="previewImage"
            alt="Captured presence photo preview"
            class="h-full w-full object-cover"
          />
          <video
            v-else
            ref="videoRef"
            class="h-full w-full scale-x-[-1] object-cover"
            autoplay
            muted
            playsinline
          />
        </div>

        <p class="text-center text-sm font-medium" :class="statusClass" aria-live="polite">
          {{ displayStatus }}
        </p>

        <p v-if="cameraError || engineError" class="text-center text-sm text-danger-700" role="alert">
          {{ cameraError || engineError }}
        </p>
        <p v-if="submitError" class="text-center text-sm text-danger-700" role="alert">
          {{ submitError }}
        </p>

        <div class="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <VButton
            v-if="!photoCaptured"
            class="min-h-[44px] sm:min-w-[160px]"
            :disabled="!canTakePhoto"
            @click="handleTakePhoto"
          >
            Take Photo
          </VButton>

          <template v-else>
            <VButton
              variant="secondary"
              class="min-h-[44px] sm:min-w-[160px]"
              :disabled="submitting"
              @click="handleRetake"
            >
              Retake Photo
            </VButton>
            <VButton
              class="min-h-[44px] sm:min-w-[180px]"
              :loading="submitting"
              @click="handleContinue"
            >
              Continue to Ballot
            </VButton>
          </template>
        </div>
      </div>
    </article>
  </div>
</template>
