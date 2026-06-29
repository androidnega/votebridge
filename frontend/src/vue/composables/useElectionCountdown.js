import { onMounted, onUnmounted, ref, unref, watch } from "vue";

function formatCountdown(diffMs) {
  if (diffMs <= 0) return "Now";
  const hours = Math.floor(diffMs / 3_600_000);
  const mins = Math.floor((diffMs % 3_600_000) / 60_000);
  const secs = Math.floor((diffMs % 60_000) / 1000);
  if (hours > 0) return `${hours}h ${mins}m ${secs}s`;
  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

export function useElectionCountdown(targetRef) {
  const countdownText = ref("—");
  let timer = null;

  function update() {
    const target = unref(targetRef);
    if (!target) {
      countdownText.value = "—";
      return;
    }
    const diff = new Date(target).getTime() - Date.now();
    countdownText.value = formatCountdown(diff);
  }

  onMounted(() => {
    update();
    timer = setInterval(update, 1000);
  });

  onUnmounted(() => {
    if (timer) clearInterval(timer);
  });

  watch(
    () => unref(targetRef),
    () => update()
  );

  return { countdownText };
}

export function resolveElectionCountdownTarget(election) {
  if (!election) return null;
  const status = election.status || election.election_status;
  if (status === "open" || status === "paused") return election.end_date;
  if (status === "scheduled") return election.start_date;
  return null;
}

export function resolveCountdownLabel(election) {
  if (!election) return "Time remaining";
  const status = election.status || election.election_status;
  if (status === "scheduled") return "Opens in";
  if (status === "open" || status === "paused") return "Closes in";
  return "Time remaining";
}
