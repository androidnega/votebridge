<script setup>
import { onMounted, ref } from "vue";
import OnOffRadioToggle from "@/components/system-control/OnOffRadioToggle.vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { systemControlNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import { LoadingSkeleton, ModuleNav, PageHeader, VAlert, VCard } from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();
const pendingKey = ref(null);

onMounted(() => store.fetchFeatureFlags().catch(() => {}));

function formatChangedAt(value) {
  if (!value) return null;
  return new Date(value).toLocaleString();
}

function changeSummary(flag) {
  const parts = [];
  if (flag.last_changed_by) parts.push(flag.last_changed_by);
  const when = formatChangedAt(flag.last_changed_at);
  if (when) parts.push(when);
  return parts.length ? parts.join(" · ") : null;
}

function onFlagChange(flag, enabled) {
  if (flag.enabled === enabled) return;

  stepUp.requireStepUp(() => {
    pendingKey.value = flag.key;
    return store
      .toggleFeatureFlag(flag.key, enabled)
      .then(() => toast.success(`${flag.name} ${enabled ? "enabled" : "disabled"}.`))
      .catch(() => {})
      .finally(() => {
        pendingKey.value = null;
      });
  });
}

function isFlagLoading(flag) {
  return store.actionLoading && pendingKey.value === flag.key;
}
</script>

<template>
  <div class="vb-page">
    <PageHeader
      title="Feature Flags"
      subtitle="Enable or disable platform modules without code changes."
      :breadcrumbs="[{ label: 'Settings', to: r.overview }, { label: 'Advanced', to: r.advanced.hub }, { label: 'Feature flags' }]"
    />
    <ModuleNav :items="systemControlNav" />
    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <LoadingSkeleton v-if="store.loading && !store.featureFlags.length" variant="list" :rows="8" />

    <div v-else class="grid grid-cols-1 gap-3 lg:grid-cols-2">
      <VCard v-for="flag in store.featureFlags" :key="flag.key" padding="sm" class="!shadow-sm">
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-sm font-semibold text-slate-900">{{ flag.name }}</h3>
            <p class="mt-0.5 line-clamp-2 text-xs leading-relaxed text-slate-600">
              {{ flag.description }}
            </p>
            <p v-if="changeSummary(flag)" class="mt-1.5 text-[0.6875rem] text-slate-400">
              Last changed: {{ changeSummary(flag) }}
            </p>
          </div>

          <OnOffRadioToggle
            compact
            :model-value="flag.enabled"
            :label="flag.name"
            :loading="isFlagLoading(flag)"
            :disabled="Boolean(pendingKey && pendingKey !== flag.key)"
            @update:model-value="onFlagChange(flag, $event)"
          />
        </div>
      </VCard>
    </div>

    <StepUpModal
      v-model="stepUp.modalOpen.value"
      :otp-code="stepUp.otpCode.value"
      :verifying="stepUp.verifying.value"
      :requesting="stepUp.requesting.value"
      @update:otp-code="stepUp.otpCode.value = $event"
      @verify="stepUp.verifyAndContinue()"
      @resend="stepUp.requestChallenge()"
    />
  </div>
</template>
