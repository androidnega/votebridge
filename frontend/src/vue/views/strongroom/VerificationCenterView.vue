<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { EmptyState, LoadingSkeleton } from "@/components/dashboard";
import { IntegrityStatusCard } from "@/components/strongroom";
import { VAlert, VButton, VInput } from "@/components/ui";
import { useStrongroomStore } from "@/stores/strongroom";

const route = useRoute();
const strongroomStore = useStrongroomStore();

const electionUuid = ref(route.query.election?.toString() || "");
const verificationHash = ref(route.query.hash?.toString() || "");

onMounted(() => {
  if (electionUuid.value && verificationHash.value) {
    strongroomStore.publicVerify(electionUuid.value, verificationHash.value).catch(() => {});
  }
});

async function handleVerify() {
  await strongroomStore.publicVerify(electionUuid.value.trim(), verificationHash.value.trim());
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 px-4 py-8 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-xl space-y-8">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">Verification center</h2>
        <p class="mt-2 text-sm leading-relaxed text-slate-500">
          Verify published election integrity using the election UUID and verification hash.
          No confidential voter information is exposed.
        </p>
      </div>

      <form
        class="space-y-5 rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5 sm:p-8"
        aria-label="Public election verification form"
        @submit.prevent="handleVerify"
      >
        <VInput
          v-model="electionUuid"
          label="Election UUID"
          placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
          required
          autocomplete="off"
        />
        <VInput
          v-model="verificationHash"
          label="Verification hash"
          placeholder="Paste the published verification hash"
          required
          autocomplete="off"
        />
        <VButton type="submit" :loading="strongroomStore.actionLoading" block>
          Verify integrity
        </VButton>
      </form>

      <VAlert v-if="strongroomStore.error" variant="error" role="alert">
        {{ strongroomStore.error }}
      </VAlert>

      <LoadingSkeleton
        v-if="strongroomStore.actionLoading && !strongroomStore.verificationResult"
        variant="card"
      />

      <section v-else-if="strongroomStore.verificationResult" class="space-y-4" aria-live="polite">
        <IntegrityStatusCard :score="strongroomStore.verificationResult.integrity_score" />
        <VAlert
          :variant="strongroomStore.verificationResult.is_valid ? 'success' : 'error'"
          :title="strongroomStore.verificationResult.is_valid ? 'Verification passed' : 'Verification failed'"
        >
          <p class="text-sm">{{ strongroomStore.verificationResult.election_title }}</p>
          <p v-if="strongroomStore.verificationResult.published_at" class="mt-1 text-sm">
            Published {{ new Date(strongroomStore.verificationResult.published_at).toLocaleString() }}
          </p>
        </VAlert>
      </section>

      <EmptyState
        v-else-if="!strongroomStore.actionLoading"
        title="Ready to verify"
        description="Enter the election UUID and verification hash published with certified results."
        icon="🔍"
      />
    </div>
  </div>
</template>
