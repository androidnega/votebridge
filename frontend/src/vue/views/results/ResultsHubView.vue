<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ConnectionStatusIndicator, LoadingSkeleton } from "@/components/dashboard";
import { ResultStatusBadge, ResultsElectionCard, ResultsFilterTabs } from "@/components/results";
import {
  ConfirmDialog,
  EmptyState,
  PageHeader,
  VAlert,
  VButton,
  VCard,
  VTable,
} from "@/components/ui";
import { toastMessages } from "@/config/toastMessages";
import { emptyStates } from "@/config/emptyStates";
import { useToast } from "@/composables/useToast";
import { useAuthStore } from "@/stores/auth";
import { useResultsStore } from "@/stores/results";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const resultsStore = useResultsStore();
const toast = useToast();

const publishOpen = ref(false);
const archiveOpen = ref(false);
const publishTarget = ref(null);
const archiveTarget = ref(null);

const activeFilter = computed(() => route.query.filter || "all");

const filterLabels = {
  all: "All results",
  certification: "Awaiting certification",
  published: "Published results",
  archived: "Archived results",
};

const activeFilterLabel = computed(() => filterLabels[activeFilter.value] || filterLabels.all);

const filteredEmptyState = computed(() => {
  if (activeFilter.value === "archived") {
    return {
      title: "No archived results",
      description: "Archived elections will appear here after publication and archival.",
      icon: "results",
    };
  }
  if (activeFilter.value === "certification") {
    return {
      title: "Nothing awaiting certification",
      description: "Closed elections pending governance review will appear here.",
      icon: "results",
    };
  }
  if (activeFilter.value === "published") {
    return {
      title: "No published results",
      description: "Published official results will appear here once released to students.",
      icon: "results",
    };
  }
  return emptyStates.results;
});

const summaryCounts = computed(() => ({
  certification: resultsStore.results.filter((row) =>
    ["pending_certification", "generated"].includes(row.result_status)
  ).length,
  published: resultsStore.results.filter((row) => row.result_status === "published").length,
  archived: resultsStore.results.filter((row) => row.result_status === "archived").length,
}));

const filterTabs = computed(() => [
  {
    id: "all",
    label: "All elections",
    count: resultsStore.results.length,
    description: "Complete results registry",
  },
  {
    id: "published",
    label: "Published",
    count: summaryCounts.value.published,
    description: "Released to students and staff",
  },
  {
    id: "certification",
    label: "In review",
    count: summaryCounts.value.certification,
    description: "Pending certification workflow",
  },
  {
    id: "archived",
    label: "Archived",
    count: summaryCounts.value.archived,
    description: "Institutional long-term record",
  },
]);

const pageSubtitle = computed(() =>
  authStore.isSuperAdmin
    ? "Certify, publish, and archive official election outcomes."
    : "View published standings and track results from closed elections."
);

const filteredResults = computed(() => {
  const rows = resultsStore.results;
  if (activeFilter.value === "certification") {
    return rows.filter((row) => ["pending_certification", "generated"].includes(row.result_status));
  }
  if (activeFilter.value === "published") {
    return rows.filter((row) => row.result_status === "published");
  }
  if (activeFilter.value === "archived") {
    return rows.filter((row) => row.result_status === "archived");
  }
  return rows;
});

const tableColumns = [
  { key: "election_title", label: "Election" },
  { key: "election_status", label: "Status" },
  { key: "integrity", label: "Integrity" },
  { key: "certification_status", label: "Certification" },
  { key: "publication_status", label: "Publication" },
  { key: "date_closed", label: "Date closed" },
  { key: "actions", label: "Actions" },
];

function integrityLabel(row) {
  if (["certified", "published", "archived"].includes(row.result_status)) return "Verified";
  if (["pending_certification", "generated"].includes(row.result_status)) return "Pending review";
  return "—";
}

function publicationLabel(row) {
  if (row.result_status === "published") return "Published";
  if (row.result_status === "archived") return "Archived";
  if (row.result_status === "certified") return "Ready to publish";
  return "Not published";
}

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
}

function canReview(row) {
  return ["pending_certification", "generated"].includes(row.result_status);
}

function canPublish(row) {
  return row.result_status === "certified";
}

function canArchive(row) {
  return row.result_status === "published";
}

function setFilter(filter) {
  if (activeFilter.value === filter) {
    router.replace({ name: "results", query: {} });
    return;
  }
  router.replace({ name: "results", query: filter === "all" ? {} : { filter } });
}

onMounted(() => {
  resultsStore.fetchResults().catch(() => {});
  if (authStore.isStaff) {
    resultsStore.fetchQueues().catch(() => {});
    resultsStore.connectRealtime();
  }
});

onUnmounted(() => {
  resultsStore.disconnectRealtime();
});

async function confirmPublish() {
  if (!publishTarget.value) return;
  await resultsStore.publish(publishTarget.value.election_uuid);
  publishOpen.value = false;
  publishTarget.value = null;
  toast.success(toastMessages.results.published);
}

async function confirmArchive() {
  if (!archiveTarget.value) return;
  await resultsStore.archive(archiveTarget.value.election_uuid);
  archiveOpen.value = false;
  archiveTarget.value = null;
  toast.success(toastMessages.results.archived);
}

function openPublish(row) {
  publishTarget.value = row;
  publishOpen.value = true;
}

function openArchive(row) {
  archiveTarget.value = row;
  archiveOpen.value = true;
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Election results"
      :subtitle="pageSubtitle"
      :breadcrumbs="[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Results' }]"
    >
      <template v-if="authStore.isSuperAdmin" #actions>
        <ConnectionStatusIndicator :status="resultsStore.realtimeStatus" />
      </template>
    </PageHeader>

    <VAlert v-if="resultsStore.error" variant="error">{{ resultsStore.error }}</VAlert>

    <template v-if="authStore.isSuperAdmin">
      <ResultsFilterTabs :tabs="filterTabs" :active="activeFilter" @change="setFilter" />

      <VCard padding="none">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-border px-card py-3">
          <p class="text-sm text-ink-secondary">
            {{ activeFilterLabel }} · {{ filteredResults.length }} election{{ filteredResults.length === 1 ? "" : "s" }}
          </p>
          <VButton v-if="activeFilter !== 'all'" size="sm" variant="ghost" @click="setFilter('all')">
            Clear filter
          </VButton>
        </div>

        <LoadingSkeleton
          v-if="resultsStore.loading && !resultsStore.results.length"
          variant="list"
          :rows="5"
        />

        <EmptyState
          v-else-if="!filteredResults.length"
          v-bind="filteredEmptyState"
          class="m-card"
        />

        <VTable
          v-else
          :columns="tableColumns"
          :rows="filteredResults"
        >
          <template #cell-election_title="{ row }">
            <span class="font-medium text-ink-primary">{{ row.election_title }}</span>
          </template>
          <template #cell-election_status="{ row }">
            <span class="capitalize">{{ row.election_status }}</span>
          </template>
          <template #cell-integrity="{ row }">
            {{ integrityLabel(row) }}
          </template>
          <template #cell-certification_status="{ row }">
            <ResultStatusBadge :status="row.result_status" />
          </template>
          <template #cell-publication_status="{ row }">
            {{ publicationLabel(row) }}
          </template>
          <template #cell-date_closed="{ row }">
            {{ formatDate(row.generated_at || row.certified_at) }}
          </template>
          <template #cell-actions="{ row }">
            <div class="flex flex-wrap gap-2" @click.stop>
              <VButton
                v-if="canReview(row)"
                size="sm"
                variant="secondary"
                @click="router.push({ name: 'result-review', params: { electionUuid: row.election_uuid } })"
              >
                Review
              </VButton>
              <VButton
                size="sm"
                variant="ghost"
                @click="router.push({ name: 'result-detail', params: { electionUuid: row.election_uuid } })"
              >
                View
              </VButton>
              <VButton
                v-if="canPublish(row)"
                size="sm"
                @click="openPublish(row)"
              >
                Publish
              </VButton>
              <VButton
                v-if="canArchive(row)"
                size="sm"
                variant="secondary"
                @click="openArchive(row)"
              >
                Archive
              </VButton>
            </div>
          </template>
        </VTable>
      </VCard>
    </template>

    <template v-else>
      <ResultsFilterTabs :tabs="filterTabs" :active="activeFilter" @change="setFilter" />

      <LoadingSkeleton
        v-if="resultsStore.loading && !resultsStore.results.length"
        variant="list"
        :rows="3"
      />

      <EmptyState
        v-else-if="!filteredResults.length"
        v-bind="filteredEmptyState"
      />

      <div v-else class="grid grid-cols-1 gap-4">
        <ResultsElectionCard
          v-for="result in filteredResults"
          :key="result.uuid"
          :result="result"
          :show-officer-actions="false"
        />
      </div>
    </template>

    <ConfirmDialog
      v-model="publishOpen"
      title="Publish results?"
      :description="`Publish official results for ${publishTarget?.election_title || 'this election'}?`"
      confirm-label="Publish results"
      icon="results"
      :loading="resultsStore.actionLoading"
      @confirm="confirmPublish"
    />
    <ConfirmDialog
      v-model="archiveOpen"
      title="Archive election?"
      :description="`Archive results for ${archiveTarget?.election_title || 'this election'}?`"
      variant="danger"
      confirm-label="Archive election"
      icon="inbox"
      :loading="resultsStore.actionLoading"
      @confirm="confirmArchive"
    />
  </div>
</template>
