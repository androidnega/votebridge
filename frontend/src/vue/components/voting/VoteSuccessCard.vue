<script setup>
import { computed, ref } from "vue";
import { FaIcon, VButton } from "@/components/ui";

const props = defineProps({
  confirmation: {
    type: Object,
    required: true,
  },
});

const downloading = ref(false);

const formattedTimestamp = computed(() => {
  if (!props.confirmation.timestamp) return null;
  return new Date(props.confirmation.timestamp).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
});

function buildReceiptHtml() {
  const reference = props.confirmation.confirmation_reference || "—";
  const election = props.confirmation.election_title || "Election";
  const submitted = formattedTimestamp.value || "Just now";
  const skipped = props.confirmation.positions_skipped;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Vote Receipt ${reference}</title>
  <style>
    body { font-family: Inter, system-ui, sans-serif; max-width: 520px; margin: 2rem auto; color: #1f2937; line-height: 1.5; }
    h1 { font-size: 1.25rem; margin: 0 0 0.5rem; color: #1e5f46; }
    .meta { color: #6b7280; font-size: 0.875rem; margin-bottom: 1.5rem; }
    dl { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem 1.25rem; margin: 0; }
    dt { font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6b7280; margin-top: 1rem; }
    dt:first-child { margin-top: 0; }
    dd { margin: 0.25rem 0 0; font-size: 1rem; font-weight: 600; }
    .ref { font-family: ui-monospace, monospace; font-size: 1.125rem; }
    footer { margin-top: 1.5rem; font-size: 0.8125rem; color: #6b7280; }
  </style>
</head>
<body>
  <h1>Vote Successfully Recorded</h1>
  <p class="meta">VoteBridge official voting receipt. Candidate choices are never shown.</p>
  <dl>
    <dt>Reference</dt>
    <dd class="ref">${reference}</dd>
    <dt>Election</dt>
    <dd>${election}</dd>
    <dt>Submitted</dt>
    <dd>${submitted}</dd>
    ${typeof skipped === "number" ? `<dt>Positions skipped</dt><dd>${skipped}</dd>` : ""}
  </dl>
  <footer>Keep this reference to verify your ballot was recorded. You cannot vote again in this election.</footer>
</body>
</html>`;
}

function downloadReceipt() {
  if (downloading.value) return;
  downloading.value = true;

  try {
    const reference = props.confirmation.confirmation_reference || "receipt";
    const safeRef = String(reference).replace(/[^\w-]+/g, "_");
    const blob = new Blob([buildReceiptHtml()], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `vote-receipt-${safeRef}.html`;
    anchor.click();
    URL.revokeObjectURL(url);
  } finally {
    downloading.value = false;
  }
}
</script>

<template>
  <article class="overflow-hidden rounded-xl border border-border bg-surface">
    <div class="bg-success-600 px-6 py-8 text-white sm:px-8">
      <div class="flex items-start gap-4">
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white/20 text-2xl"
          aria-hidden="true"
        >
          ✓
        </div>
        <div>
          <h2 class="text-2xl font-bold">Vote Successfully Recorded</h2>
          <p class="mt-1 text-sm text-green-100">
            Thank you for participating. Your selections remain confidential.
          </p>
        </div>
      </div>
    </div>

    <dl class="grid gap-4 px-6 py-6 sm:grid-cols-2 sm:px-8">
      <div class="rounded-lg bg-surface-muted p-4 sm:col-span-2">
        <dt class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Reference</dt>
        <dd class="mt-1 font-mono text-lg font-semibold text-ink-primary">
          {{ confirmation.confirmation_reference || "—" }}
        </dd>
      </div>

      <div class="rounded-lg bg-surface-muted p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Election</dt>
        <dd class="mt-1 text-base font-semibold text-ink-primary">
          {{ confirmation.election_title }}
        </dd>
      </div>

      <div class="rounded-lg bg-surface-muted p-4">
        <dt class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Submitted</dt>
        <dd class="mt-1 text-base font-semibold text-ink-primary">
          {{ formattedTimestamp || "Just now" }}
        </dd>
      </div>
    </dl>

    <div class="flex flex-col gap-3 border-t border-border px-6 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8">
      <p class="text-sm text-ink-secondary">
        You cannot vote again in this election. Candidate choices are never shown after submission.
      </p>
      <VButton
        variant="secondary"
        class="shrink-0 min-h-[44px]"
        :loading="downloading"
        @click="downloadReceipt"
      >
        <FaIcon icon="fa-download" class="mr-2" />
        Download receipt
      </VButton>
    </div>
  </article>
</template>
