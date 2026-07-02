<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AdminWorkspaceTile } from "@/components/admin";
import ElectionLifecycleBar from "@/components/elections/ElectionLifecycleBar.vue";
import { adminWorkspaceTiles } from "@/config/adminWorkspace";
import { CountdownTimer, ElectionStatusBadge } from "@/components/voting";
import { LoadingSkeleton, VAlert, VButton, VInput, VModal } from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { useToast } from "@/composables/useToast";
import { useElectionStore } from "@/stores/election";
import { useResultsStore } from "@/stores/results";

const route = useRoute();
const router = useRouter();
const electionStore = useElectionStore();
const resultsStore = useResultsStore();
const toast = useToast();

const electionUuid = computed(() => route.params.uuid);
const election = computed(() => electionStore.currentElection || {});

const showEdit = ref(false);
const saving = ref(false);
const editError = ref(null);

const electionTypes = [
  { value: "general", label: "General" },
  { value: "student_union", label: "Student union" },
  { value: "faculty", label: "Faculty" },
  { value: "departmental", label: "Departmental" },
  { value: "special", label: "Special" },
];

const editForm = ref({
  title: "",
  description: "",
  election_type: "general",
  start_date: "",
  end_date: "",
  allow_web_voting: true,
  allow_ussd_voting: false,
  allow_sms_notifications: false,
});

const status = computed(() => election.value.status || "draft");

const phaseMeta = computed(() => {
  const map = {
    draft: {
      eyebrow: "Setup",
      subtitle: "Configure the ballot, voter roll, and readiness checklist before scheduling.",
      tone: "setup",
    },
    scheduled: {
      eyebrow: "Scheduled",
      subtitle: "Everything is staged. Open the election when the voting window begins.",
      tone: "setup",
    },
    open: {
      eyebrow: "Live voting",
      subtitle: "Students can cast ballots now. Monitor turnout and channel health.",
      tone: "live",
    },
    paused: {
      eyebrow: "Paused",
      subtitle: "Voting is temporarily suspended. Resume when you are ready.",
      tone: "live",
    },
    closed: {
      eyebrow: "Voting ended",
      subtitle: "The ballot is closed. Review certified results and hand off reporting.",
      tone: "complete",
    },
    archived: {
      eyebrow: "Archived",
      subtitle: "This election is stored for reference. All workspace data is read-only.",
      tone: "complete",
    },
  };
  return map[status.value] || map.draft;
});

const isSetupPhase = computed(() => ["draft", "scheduled"].includes(status.value));
const isLivePhase = computed(() => ["open", "paused"].includes(status.value));
const isCompletePhase = computed(() => ["closed", "archived"].includes(status.value));

const canEdit = computed(() => isSetupPhase.value);

const result = computed(() => resultsStore.currentResult);

const resultRoute = computed(() => ({
  name: "result-detail",
  params: { electionUuid: electionUuid.value },
}));

const resultStatusLabel = computed(() => {
  const labels = {
    pending_generation: "Awaiting result generation",
    generated: "Results generated — pending certification",
    pending_certification: "Pending certification",
    certified: "Certified — ready to publish",
    published: "Results published",
    archived: "Results archived",
  };
  return labels[result.value?.result_status] || "View official results";
});

const turnoutSummary = computed(() => {
  const turnout = result.value?.turnout_percentage ?? result.value?.standings?.summary?.turnout_percentage;
  const votes = result.value?.total_votes_cast ?? result.value?.standings?.summary?.total_votes_cast;
  if (turnout == null && votes == null) return null;
  const parts = [];
  if (votes != null) parts.push(`${votes} vote${votes === 1 ? "" : "s"} cast`);
  if (turnout != null) parts.push(`${Number(turnout).toFixed(1)}% turnout`);
  return parts.join(" · ");
});

const votingChannels = computed(() => {
  const channels = [];
  if (election.value.allow_web_voting) channels.push("Web");
  if (election.value.allow_ussd_voting) channels.push("USSD");
  if (election.value.allow_sms_notifications) channels.push("SMS");
  return channels;
});

const statChips = computed(() => {
  const chips = [
    {
      label: "Positions",
      value: election.value.position_count ?? 0,
    },
    {
      label: "Candidates",
      value: election.value.candidate_count ?? 0,
      meta:
        election.value.approved_candidate_count != null
          ? `${election.value.approved_candidate_count} approved`
          : "",
    },
    {
      label: "Type",
      value: election.value.election_type_display || "Election",
    },
    {
      label: "Window",
      value: formatDateRange(election.value.start_date, election.value.end_date),
    },
  ];

  if (votingChannels.value.length) {
    chips.push({
      label: "Channels",
      value: votingChannels.value.join(", "),
    });
  }

  return chips;
});

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDateRange(start, end) {
  if (!start && !end) return "Not set";
  if (start && end) return `${formatDate(start)} — ${formatDate(end)}`;
  return formatDate(start || end);
}

function buildTile(tile) {
  const uuid = electionUuid.value;
  let to = tile.externalRoute || `/dashboard/elections/${uuid}/${tile.routeSuffix}`;
  let actionLabel = isCompletePhase.value ? "View" : "Manage";
  let description = tile.description;
  let value = null;
  let meta = "";
  let disabled = false;

  if (tile.id === "positions") {
    value = election.value.position_count ?? 0;
    if (isCompletePhase.value) description = "Offices that were on the ballot.";
  }

  if (tile.id === "candidates") {
    value = election.value.candidate_count ?? 0;
    meta = `${election.value.approved_candidate_count ?? 0} approved`;
    if (isCompletePhase.value) description = "Nominees who stood for election.";
  }

  if (tile.id === "eligibility") {
    if (isCompletePhase.value) description = "Voter roll and programme filters used.";
    actionLabel = isCompletePhase.value ? "View roll" : "Manage";
  }

  if (tile.id === "readiness") {
    actionLabel = "View checklist";
    if (isCompletePhase.value) {
      description = "Pre-open checks completed before voting.";
    }
  }

  if (tile.id === "results") {
    if (isCompletePhase.value) {
      to = resultRoute.value;
      actionLabel = "View results";
      description = "Official standings, certification, and publication.";
    } else if (isLivePhase.value) {
      to = `/dashboard/elections/${uuid}/monitor`;
      actionLabel = "Monitor turnout";
      description = "Live turnout and channel activity.";
    } else {
      disabled = true;
      actionLabel = "After closing";
      description = "Available once voting has ended.";
    }
  }

  return { ...tile, to, actionLabel, value, meta, description, disabled };
}

const ballotTiles = computed(() =>
  adminWorkspaceTiles
    .filter((tile) => ["positions", "candidates", "eligibility"].includes(tile.id))
    .map(buildTile)
);

const supportTiles = computed(() => {
  const ids = isSetupPhase.value ? ["readiness"] : isLivePhase.value ? [] : [];
  return adminWorkspaceTiles.filter((tile) => ids.includes(tile.id)).map(buildTile);
});

function toLocalInput(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function populateEditForm() {
  editForm.value = {
    title: election.value.title || "",
    description: election.value.description || "",
    election_type: election.value.election_type || "general",
    start_date: toLocalInput(election.value.start_date),
    end_date: toLocalInput(election.value.end_date),
    allow_web_voting: election.value.allow_web_voting ?? true,
    allow_ussd_voting: election.value.allow_ussd_voting ?? false,
    allow_sms_notifications: election.value.allow_sms_notifications ?? false,
  };
}

function openEdit() {
  populateEditForm();
  editError.value = null;
  showEdit.value = true;
}

async function refresh() {
  await electionStore.fetchElection(electionUuid.value);
  if (isCompletePhase.value) {
    resultsStore.fetchResult(electionUuid.value).catch(() => {});
  }
}

async function saveEdit() {
  saving.value = true;
  editError.value = null;
  try {
    await electionStore.updateElection(electionUuid.value, {
      ...editForm.value,
      start_date: new Date(editForm.value.start_date).toISOString(),
      end_date: new Date(editForm.value.end_date).toISOString(),
    });
    toast.success(toastMessages.election.updated);
    showEdit.value = false;
    await refresh();
  } catch {
    editError.value = electionStore.error || "Unable to update election.";
  } finally {
    saving.value = false;
  }
}

function openResults() {
  router.push(resultRoute.value);
}

function openMonitor() {
  router.push(`/dashboard/elections/${electionUuid.value}/monitor`);
}

function openReadiness() {
  router.push(`/dashboard/elections/${electionUuid.value}/readiness`);
}

watch(showEdit, (open) => {
  if (open) populateEditForm();
});

watch(status, (next) => {
  if (["closed", "archived"].includes(next)) {
    resultsStore.fetchResult(electionUuid.value).catch(() => {});
  }
});

onMounted(refresh);

onUnmounted(() => {
  resultsStore.clearCurrent();
});
</script>

<template>
  <div class="vb-page mx-auto max-w-6xl space-y-6">
    <VAlert v-if="electionStore.error" variant="error">{{ electionStore.error }}</VAlert>

    <LoadingSkeleton v-if="electionStore.loading && !election.title" variant="card" />

    <template v-else>
      <section class="overflow-hidden rounded-card border border-border bg-surface shadow-card">
        <div class="border-b border-border/80 bg-slate-50/80 px-5 py-3 sm:px-6">
          <nav class="text-sm text-slate-500" aria-label="Breadcrumb">
            <ol class="flex flex-wrap items-center gap-2">
              <li>
                <button
                  type="button"
                  class="font-medium text-brand-700 transition hover:text-brand-800"
                  @click="router.push('/dashboard/elections')"
                >
                  Elections
                </button>
              </li>
              <li aria-hidden="true" class="text-slate-300">/</li>
              <li class="truncate font-medium text-slate-700" aria-current="page">
                {{ election.title || "Overview" }}
              </li>
            </ol>
          </nav>
        </div>

        <div class="space-y-5 p-5 sm:p-6">
          <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <ElectionStatusBadge :status="election.status" :label="election.status_display" size="lg" />
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
                  :class="
                    phaseMeta.tone === 'live'
                      ? 'bg-emerald-50 text-emerald-800 ring-emerald-200'
                      : phaseMeta.tone === 'complete'
                        ? 'bg-slate-100 text-slate-700 ring-slate-200'
                        : 'bg-brand-50 text-brand-800 ring-brand-200'
                  "
                >
                  {{ phaseMeta.eyebrow }}
                </span>
              </div>

              <h1 class="mt-3 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                {{ election.title || "Election workspace" }}
              </h1>

              <p class="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">
                {{ phaseMeta.subtitle }}
              </p>

              <p v-if="election.description" class="mt-2 max-w-2xl text-sm text-slate-500">
                {{ election.description }}
              </p>
            </div>

            <div class="flex shrink-0 flex-col items-start gap-3 sm:items-end">
              <VButton v-if="canEdit" size="sm" variant="secondary" @click="openEdit">
                Edit election
              </VButton>

              <CountdownTimer
                v-if="isLivePhase || status === 'scheduled'"
                variant="light"
                :start-date="election.start_date"
                :end-date="election.end_date"
                :status="election.status"
              />

              <div
                v-else-if="isCompletePhase"
                class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left sm:min-w-[200px] sm:text-right"
              >
                <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Voting window</p>
                <p class="mt-1 text-sm font-medium text-slate-800">
                  {{ formatDateRange(election.start_date, election.end_date) }}
                </p>
              </div>
            </div>
          </div>

          <dl class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            <div
              v-for="chip in statChips"
              :key="chip.label"
              class="rounded-xl border border-border/80 bg-white px-3 py-2.5"
            >
              <dt class="text-[11px] font-medium uppercase tracking-wide text-slate-500">{{ chip.label }}</dt>
              <dd class="mt-0.5 text-sm font-semibold text-slate-900">{{ chip.value }}</dd>
              <dd v-if="chip.meta" class="mt-0.5 text-xs text-slate-500">{{ chip.meta }}</dd>
            </div>
          </dl>

          <div class="flex flex-wrap items-center gap-3 border-t border-border/80 pt-4">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Lifecycle</p>
            <ElectionLifecycleBar :election="election" @updated="refresh" />
          </div>
        </div>
      </section>

      <section
        v-if="isCompletePhase"
        class="rounded-card border border-rose-200 bg-gradient-to-br from-rose-50 via-white to-white p-5 shadow-card sm:p-6"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wide text-rose-700">Results & reporting</p>
            <p class="mt-1 text-lg font-semibold text-slate-900">{{ resultStatusLabel }}</p>
            <p v-if="turnoutSummary" class="mt-1 text-sm text-slate-600">{{ turnoutSummary }}</p>
            <p v-else class="mt-1 text-sm text-slate-500">Open the results workspace for standings and certification.</p>
          </div>
          <VButton class="shrink-0" @click="openResults">View results</VButton>
        </div>
      </section>

      <section
        v-else-if="isLivePhase"
        class="rounded-card border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-white p-5 shadow-card sm:p-6"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-emerald-700">Live monitor</p>
            <p class="mt-1 text-lg font-semibold text-slate-900">Track turnout while voting is open</p>
            <p class="mt-1 text-sm text-slate-600">Channel activity, participation trends, and incident response.</p>
          </div>
          <VButton class="shrink-0" @click="openMonitor">Open monitor</VButton>
        </div>
      </section>

      <section
        v-else-if="isSetupPhase"
        class="rounded-card border border-violet-200 bg-gradient-to-br from-violet-50 via-white to-white p-5 shadow-card sm:p-6"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-violet-700">Readiness checklist</p>
            <p class="mt-1 text-lg font-semibold text-slate-900">Validate before you open the ballot</p>
            <p class="mt-1 text-sm text-slate-600">
              Confirm positions, approved candidates, and eligibility rules are complete.
            </p>
          </div>
          <VButton class="shrink-0" variant="secondary" @click="openReadiness">View checklist</VButton>
        </div>
      </section>

      <section class="space-y-4">
        <div class="flex items-end justify-between gap-3">
          <div>
            <h2 class="text-base font-semibold text-slate-900">
              {{ isCompletePhase ? "Ballot record" : "Ballot setup" }}
            </h2>
            <p class="mt-1 text-sm text-slate-500">
              {{
                isCompletePhase
                  ? "Review how this election was configured."
                  : "Positions, candidates, and who was eligible to vote."
              }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <AdminWorkspaceTile
            v-for="tile in ballotTiles"
            :key="tile.id"
            :title="tile.title"
            :description="tile.description"
            :value="tile.value"
            :meta="tile.meta"
            :to="tile.to"
            :action-label="tile.actionLabel"
            :palette-key="tile.paletteKey"
            :icon="tile.icon"
            :disabled="tile.disabled"
          />
        </div>
      </section>

      <section v-if="supportTiles.length" class="space-y-4">
        <div>
          <h2 class="text-base font-semibold text-slate-900">Pre-open checks</h2>
          <p class="mt-1 text-sm text-slate-500">Resolve blockers before scheduling or opening.</p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <AdminWorkspaceTile
            v-for="tile in supportTiles"
            :key="tile.id"
            :title="tile.title"
            :description="tile.description"
            :value="tile.value"
            :meta="tile.meta"
            :to="tile.to"
            :action-label="tile.actionLabel"
            :palette-key="tile.paletteKey"
            :icon="tile.icon"
            :disabled="tile.disabled"
          />
        </div>
      </section>
    </template>

    <VModal v-model="showEdit" title="Edit election" size="lg">
      <VAlert v-if="editError" variant="error" class="mb-4">{{ editError }}</VAlert>
      <form class="space-y-4" @submit.prevent="saveEdit">
        <VInput v-model="editForm.title" label="Title" required />
        <div class="space-y-1.5">
          <label class="vb-label" for="edit-description">Description</label>
          <textarea id="edit-description" v-model="editForm.description" rows="4" class="vb-input" />
        </div>
        <div class="space-y-1.5">
          <label class="vb-label" for="edit-election-type">Election type</label>
          <select id="edit-election-type" v-model="editForm.election_type" class="vb-input" required>
            <option v-for="type in electionTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <VInput v-model="editForm.start_date" label="Start date" type="datetime-local" required />
          <VInput v-model="editForm.end_date" label="End date" type="datetime-local" required />
        </div>
        <div class="space-y-2 text-sm text-slate-700">
          <label class="flex items-center gap-2">
            <input v-model="editForm.allow_web_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow web voting
          </label>
          <label class="flex items-center gap-2">
            <input v-model="editForm.allow_ussd_voting" type="checkbox" class="rounded border-border text-brand-600" />
            Allow USSD voting
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="editForm.allow_sms_notifications"
              type="checkbox"
              class="rounded border-border text-brand-600"
            />
            Allow SMS notifications
          </label>
        </div>
        <div class="flex flex-wrap justify-end gap-3 pt-2">
          <VButton variant="secondary" type="button" @click="showEdit = false">Cancel</VButton>
          <VButton type="submit" :loading="saving">Save changes</VButton>
        </div>
      </form>
    </VModal>
  </div>
</template>
