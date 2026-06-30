<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ElectionStatusBadge } from "@/components/voting";
import { ConfirmDialog, VButton } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
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

const confirmVariant = computed(() =>
  ["close", "archive"].includes(confirmAction.value?.action) ? "danger" : "primary"
);

const confirmIcon = computed(() => {
  const action = confirmAction.value?.action;
  if (action === "close") return "strongroom";
  if (action === "pause") return "bolt";
  return "help";
});

const toastForAction = {
  schedule: toastMessages.election.scheduled,
  open: toastMessages.election.opened,
  pause: toastMessages.election.paused,
  resume: toastMessages.election.resumed,
  close: toastMessages.election.closed,
  archive: toastMessages.election.archived,
};

async function runAction(action) {
  const uuid = props.election.uuid;
  try {
    if (action === "schedule") await electionStore.scheduleElection(uuid);
    else if (action === "open") await electionStore.openElection(uuid);
    else if (action === "pause") await electionStore.pauseElection(uuid);
    else if (action === "resume") await electionStore.openElection(uuid);
    else if (action === "close") await electionStore.closeElection(uuid);
    else if (action === "archive") await electionStore.archiveElection(uuid);
    toast.success(toastForAction[action] || toastMessages.generic.saved);
    emit("updated");
    if (action === "close") {
      router.push("/dashboard/results");
    }
  } catch {
    toast.error(electionStore.error || toastMessages.generic.error);
  } finally {
    electionStore.clearPendingLifecycleAction();
  }
}

function askConfirm(action, label, message) {
  electionStore.setPendingLifecycleAction({ action, label, message });
}

function confirm() {
  if (!confirmAction.value) return;
  runAction(confirmAction.value.action);
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
      @click="runAction('schedule')"
    >
      Schedule
    </VButton>

    <VButton v-if="status === 'scheduled'" size="sm" :loading="loading" @click="runAction('open')">
      Open election
    </VButton>

    <VButton
      v-if="status === 'open'"
      size="sm"
      variant="secondary"
      :loading="loading"
      @click="askConfirm('pause', 'Pause election', 'Voting will be temporarily suspended. Students cannot submit ballots while paused.')"
    >
      Pause
    </VButton>

    <VButton v-if="status === 'paused'" size="sm" :loading="loading" @click="runAction('resume')">
      Resume
    </VButton>

    <VButton
      v-if="['open', 'paused'].includes(status)"
      size="sm"
      variant="danger"
      :loading="loading"
      @click="
        askConfirm(
          'close',
          'Close election',
          'Voting will end and results processing will begin. This cannot be undone.'
        )
      "
    >
      Close
    </VButton>

    <VButton
      v-if="status === 'closed'"
      size="sm"
      variant="secondary"
      :loading="loading"
      @click="askConfirm('archive', 'Archive election', 'Archive this election for long-term storage?')"
    >
      Archive
    </VButton>

    <ConfirmDialog
      v-model="showConfirm"
      :title="confirmAction?.label || 'Confirm'"
      :description="confirmAction?.message || ''"
      :variant="confirmVariant"
      :icon="confirmIcon"
      confirm-label="Confirm"
      cancel-label="Cancel"
      :loading="loading"
      @confirm="confirm"
      @cancel="cancelConfirm"
    />
  </div>
</template>
