<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ElectionStatusBadge } from "@/components/voting";
import { VButton, VModal } from "@/components/ui";
import { useToast } from "@/composables/useToast";
import { useElectionStore } from "@/stores/election";

const props = defineProps({
  election: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["updated"]);

const router = useRouter();
const electionStore = useElectionStore();
const toast = useToast();

const status = computed(() => props.election?.status);
const loading = computed(() => electionStore.actionLoading);

const confirmAction = computed(() => electionStore.pendingLifecycleAction);
const showConfirm = computed({
  get: () => Boolean(confirmAction.value),
  set: (value) => {
    if (!value) cancelConfirm();
  },
});

async function runAction(action, label) {
  const uuid = props.election.uuid;
  try {
    if (action === "schedule") await electionStore.scheduleElection(uuid);
    else if (action === "open") await electionStore.openElection(uuid);
    else if (action === "pause") await electionStore.pauseElection(uuid);
    else if (action === "resume") await electionStore.openElection(uuid);
    else if (action === "close") await electionStore.closeElection(uuid);
    else if (action === "archive") await electionStore.archiveElection(uuid);
    toast.success(`${label} completed.`);
    emit("updated");
    if (action === "close") {
      router.push("/results");
    }
  } catch {
    toast.error(electionStore.error || `${label} failed.`);
  } finally {
    electionStore.clearPendingLifecycleAction();
  }
}

function askConfirm(action, label, message) {
  electionStore.setPendingLifecycleAction({ action, label, message });
}

function confirm() {
  if (!confirmAction.value) return;
  runAction(confirmAction.value.action, confirmAction.value.label);
}

function cancelConfirm() {
  electionStore.clearPendingLifecycleAction();
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <ElectionStatusBadge :status="status" />

    <VButton
      v-if="status === 'draft'"
      size="sm"
      variant="secondary"
      :loading="loading"
      @click="runAction('schedule', 'Schedule')"
    >
      Schedule
    </VButton>

    <VButton
      v-if="status === 'scheduled'"
      size="sm"
      :loading="loading"
      @click="runAction('open', 'Open')"
    >
      Open election
    </VButton>

    <VButton
      v-if="status === 'open'"
      size="sm"
      variant="secondary"
      :loading="loading"
      @click="askConfirm('pause', 'Pause', 'Pause voting for this election?')"
    >
      Pause
    </VButton>

    <VButton
      v-if="status === 'paused'"
      size="sm"
      :loading="loading"
      @click="runAction('resume', 'Resume')"
    >
      Resume
    </VButton>

    <VButton
      v-if="['open', 'paused'].includes(status)"
      size="sm"
      variant="danger"
      :loading="loading"
      @click="askConfirm('close', 'Close', 'Close this election? Voting will end and results processing will begin.')"
    >
      Close
    </VButton>

    <VButton
      v-if="status === 'closed'"
      size="sm"
      variant="secondary"
      :loading="loading"
      @click="askConfirm('archive', 'Archive', 'Archive this election?')"
    >
      Archive
    </VButton>

    <VModal
      v-model="showConfirm"
      :title="confirmAction?.label"
      @close="cancelConfirm"
    >
      <p class="text-sm text-slate-600">{{ confirmAction?.message }}</p>
      <template #footer>
        <VButton variant="secondary" @click="cancelConfirm">Cancel</VButton>
        <VButton :loading="loading" @click="confirm">Confirm</VButton>
      </template>
    </VModal>
  </div>
</template>
