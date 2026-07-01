<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { VAlert, VButton, VCard, VInput } from "@/components/ui";
import { useDashboardStore } from "@/stores/dashboard";

const router = useRouter();
const dashboardStore = useDashboardStore();
const verifyToken = ref("");

async function handleVerify() {
  if (!verifyToken.value.trim()) return;
  try {
    await dashboardStore.verifyBallotToken(verifyToken.value);
  } catch {
    /* error surfaced via store */
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <div>
      <button
        type="button"
        class="text-sm font-medium text-brand-700 hover:text-brand-hover"
        @click="router.push({ name: 'profile' })"
      >
        ← Back to profile
      </button>
      <h2 class="mt-3 text-2xl font-bold text-slate-900">Verify ballot</h2>
      <p class="mt-1 text-sm text-slate-600">
        Confirm your vote was recorded using your Secure Voting Token. Candidate choices are never shown.
      </p>
    </div>

    <VCard title="Secure Voting Token verification">
      <form class="space-y-4" @submit.prevent="handleVerify">
        <VInput
          v-model="verifyToken"
          label="SVT token"
          placeholder="Paste your voting token"
          autocomplete="off"
        />
        <VButton type="submit" class="min-h-[48px] w-full sm:w-auto" :loading="dashboardStore.verifying">
          Verify ballot
        </VButton>
      </form>

      <VAlert v-if="dashboardStore.error" class="mt-4" variant="error">
        {{ dashboardStore.error }}
      </VAlert>

      <VAlert
        v-if="dashboardStore.verificationResult"
        class="mt-4"
        :variant="dashboardStore.verificationResult.is_valid ? 'success' : 'warning'"
        :title="dashboardStore.verificationResult.is_valid ? 'Ballot verified' : 'Verification issue'"
      >
        <p class="text-sm">
          {{ dashboardStore.verificationResult.election_title }} —
          {{ dashboardStore.verificationResult.positions_count }} position(s) completed.
        </p>
      </VAlert>
    </VCard>
  </div>
</template>
