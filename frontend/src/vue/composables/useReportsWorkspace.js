import { computed, ref } from "vue";
import { electionsApi } from "@/api/elections";
import { analyticsApi } from "@/api/analytics";
import { useAnalyticsStore } from "@/stores/analytics";

const EMPTY_FILTERS = {
  election: "",
  academicYear: "",
  faculty: "",
  department: "",
  programme: "",
};

function deriveAcademicYear(startDate) {
  if (!startDate) return null;
  const year = new Date(startDate).getFullYear();
  return `${year}/${year + 1}`;
}

function average(values) {
  if (!values.length) return 0;
  return Math.round((values.reduce((sum, value) => sum + value, 0) / values.length) * 10) / 10;
}

/**
 * Institutional reports workspace — composes existing analytics APIs with client-side filters.
 */
export function useReportsWorkspace() {
  const store = useAnalyticsStore();
  const filters = ref({ ...EMPTY_FILTERS });
  const electionMeta = ref([]);
  const initialLoading = ref(false);
  const exportLoading = ref(false);

  async function loadWorkspace() {
    initialLoading.value = true;
    try {
      const [electionList] = await Promise.all([
        electionsApi.list({ page_size: 100 }).catch(() => ({ items: [] })),
        store.fetchOverview().catch(() => {}),
        store.fetchElections().catch(() => {}),
        store.fetchParticipation().catch(() => {}),
        store.fetchFaculties().catch(() => {}),
        store.fetchHistorical("daily").catch(() => {}),
      ]);
      electionMeta.value = electionList?.items || electionList || [];
    } finally {
      initialLoading.value = false;
    }
  }

  const electionYearMap = computed(() => {
    const map = new Map();
    for (const election of electionMeta.value) {
      const uuid = election.uuid || election.election_uuid;
      if (uuid) {
        map.set(uuid, deriveAcademicYear(election.start_date));
      }
    }
    return map;
  });

  const allElectionRows = computed(() => store.elections?.comparison || []);

  const filteredElectionRows = computed(() => {
    let rows = allElectionRows.value;
    if (filters.value.election) {
      rows = rows.filter((row) => row.election_uuid === filters.value.election);
    }
    if (filters.value.academicYear) {
      rows = rows.filter(
        (row) => electionYearMap.value.get(row.election_uuid) === filters.value.academicYear
      );
    }
    return rows;
  });

  const programmeRows = computed(() => store.participation?.programmes || []);

  const filteredProgrammes = computed(() => {
    let rows = programmeRows.value;
    if (filters.value.faculty) {
      rows = rows.filter((row) => row.faculty === filters.value.faculty);
    }
    if (filters.value.department) {
      rows = rows.filter((row) => row.label === filters.value.department);
    }
    if (filters.value.programme) {
      rows = rows.filter(
        (row) => row.code === filters.value.programme || row.label === filters.value.programme
      );
    }
    return rows;
  });

  const filteredFaculties = computed(() => {
    const faculties = store.faculties || [];
    if (!filters.value.faculty && !filters.value.department && !filters.value.programme) {
      return faculties;
    }

    const facultyMap = new Map();
    for (const programme of filteredProgrammes.value) {
      const existing = facultyMap.get(programme.faculty) || {
        faculty: programme.faculty,
        eligible: 0,
        participated: 0,
      };
      existing.eligible += programme.eligible || 0;
      existing.participated += programme.participated || 0;
      facultyMap.set(programme.faculty, existing);
    }

    return [...facultyMap.values()].map((row) => ({
      ...row,
      turnout_percent:
        row.eligible > 0 ? Math.round((row.participated / row.eligible) * 1000) / 10 : 0,
    }));
  });

  const filterOptions = computed(() => ({
    elections: allElectionRows.value.map((row) => ({
      value: row.election_uuid,
      label: row.title,
    })),
    academicYears: [
      ...new Set(
        [...electionYearMap.value.values()].filter(Boolean).sort((a, b) => b.localeCompare(a))
      ),
    ],
    faculties: [...new Set(programmeRows.value.map((row) => row.faculty).filter(Boolean))].sort(),
    departments: [...new Set(programmeRows.value.map((row) => row.label).filter(Boolean))].sort(),
    programmes: programmeRows.value.map((row) => ({
      value: row.code,
      label: row.label,
    })),
  }));

  const kpis = computed(() => {
    const rows = filteredElectionRows.value;
    const programmes = filteredProgrammes.value;
    const overview = store.overview;

    const completedFromRows = rows.filter((row) =>
      ["closed", "archived"].includes(row.status)
    ).length;

    return {
      completedElections:
        rows.length > 0 ? completedFromRows : overview?.completed_elections ?? 0,
      averageTurnout:
        rows.length > 0
          ? average(rows.map((row) => row.turnout_percent || 0))
          : overview?.average_turnout_percent ?? overview?.overall_turnout_percent ?? 0,
      registeredVoters:
        programmes.length > 0
          ? programmes.reduce((sum, row) => sum + (row.eligible || 0), 0)
          : overview?.total_active_voters ?? 0,
      totalVotesCast:
        rows.length > 0
          ? rows.reduce((sum, row) => sum + (row.votes_cast || 0), 0)
          : overview?.total_votes ?? 0,
    };
  });

  const turnoutTrend = computed(() => {
    const points = store.historical?.vote_trends?.length
      ? store.historical.vote_trends
      : store.elections?.trend || [];

    if (!filters.value.academicYear) {
      return points;
    }

    const [startYear] = filters.value.academicYear.split("/");
    return points.filter((point) => String(point.label).includes(startYear));
  });

  const turnoutTrendLabels = computed(() => turnoutTrend.value.map((point) => point.label));
  const turnoutTrendValues = computed(() => turnoutTrend.value.map((point) => point.value));

  const facultyChartLabels = computed(() =>
    [...filteredFaculties.value]
      .sort((a, b) => (b.turnout_percent || 0) - (a.turnout_percent || 0))
      .map((row) => row.faculty)
  );
  const facultyChartValues = computed(() =>
    [...filteredFaculties.value]
      .sort((a, b) => (b.turnout_percent || 0) - (a.turnout_percent || 0))
      .map((row) => row.turnout_percent)
  );

  const electionDistribution = computed(() => {
    const rows = filteredElectionRows.value;
    if (!rows.length) {
      return (store.elections?.comparison || []).map((row) => ({
        name: row.title,
        value: row.votes_cast || row.turnout_percent || 1,
      }));
    }
    return rows.map((row) => ({
      name: row.title,
      value: row.votes_cast || row.turnout_percent || 1,
    }));
  });

  const governanceSummary = computed(() => {
    const overview = store.overview;
    if (!overview) return null;
    return {
      securityAlerts: overview.total_security_alerts ?? 0,
      fraudCases: overview.total_fraud_cases ?? 0,
      smsSuccessPercent: overview.average_sms_delivery_success_percent ?? 0,
      ussdRequestsToday: overview.average_ussd_usage ?? 0,
    };
  });

  function resetFilters() {
    filters.value = { ...EMPTY_FILTERS };
  }

  async function exportReport(format) {
    exportLoading.value = true;
    try {
      const params = {};
      if (filters.value.election) {
        params.election_uuid = filters.value.election;
      }
      const data = await analyticsApi.getReport("institution", format, params);

      if (format === "csv" && data.content) {
        const blob = new Blob([data.content], { type: "text/csv" });
        triggerDownload(blob, data.filename || "votebridge-reports.csv");
        return data;
      }

      const payload =
        typeof data.content === "string" ? data.content : JSON.stringify(data.content, null, 2);
      const extension = format === "pdf" ? "pdf" : format === "excel" ? "xlsx" : "json";
      const mime =
        format === "pdf"
          ? "application/pdf"
          : format === "excel"
            ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            : "application/json";
      const blob = new Blob([payload], { type: mime });
      triggerDownload(blob, `votebridge-reports.${extension}`);
      return data;
    } finally {
      exportLoading.value = false;
    }
  }

  return {
    store,
    filters,
    initialLoading,
    exportLoading,
    filterOptions,
    filteredElectionRows,
    kpis,
    turnoutTrendLabels,
    turnoutTrendValues,
    facultyChartLabels,
    facultyChartValues,
    electionDistribution,
    governanceSummary,
    loadWorkspace,
    resetFilters,
    exportReport,
  };
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
