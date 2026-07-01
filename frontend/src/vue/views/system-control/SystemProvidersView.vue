<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import ProviderConfigForm from "@/components/system-control/ProviderConfigForm.vue";
import StepUpModal from "@/components/system-control/StepUpModal.vue";
import OpsHealthBadge from "@/components/operations/OpsHealthBadge.vue";
import {
  buildProviderConfigPayload,
  draftFromProvider,
  getProviderConfigFields,
  hasStoredProviderSecret,
} from "@/config/providerConfig";
import { settingsRoutes as r } from "@/config/settingsRoutes";
import { settingsNav } from "@/config/moduleNav";
import { useStepUp } from "@/composables/useStepUp";
import { useToast } from "@/composables/useToast";
import {
  EmptyState,
  LoadingSkeleton,
  ModuleNav,
  PageHeader,
  VAlert,
  VButton,
  VCard,
} from "@/components/ui";
import { useSystemControlStore } from "@/stores/systemControl";

const props = defineProps({
  providerType: { type: String, default: "" },
  title: { type: String, default: "Communication Providers" },
});

const route = useRoute();
const store = useSystemControlStore();
const toast = useToast();
const stepUp = useStepUp();
const configDrafts = reactive({});
const savingUuid = ref(null);
const pendingSave = ref(null);

onMounted(() => {
  loadProviders();
});

watch(
  () => route.query.type,
  () => loadProviders()
);

function resolvedProviderType() {
  return props.providerType || route.query.type || undefined;
}

function loadProviders() {
  store
    .fetchProviders(resolvedProviderType())
    .then((providers) => {
      initDrafts(providers);
      const focus = route.query.focus;
      if (focus) {
        requestAnimationFrame(() => {
          document.getElementById(`provider-${focus}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
        });
      }
    })
    .catch(() => {});
}

function initDrafts(providers) {
  for (const provider of providers) {
    configDrafts[provider.uuid] = draftFromProvider(provider);
  }
}

function providerLabel(providerType) {
  if (providerType === "arkesel_sms") return "Arkesel SMS";
  if (providerType === "moolre_sms") return "Moolre SMS";
  if (providerType === "smtp_email") return "SMTP Email";
  return providerType.replace(/_/g, " ");
}

function validateDraft(provider) {
  const draft = configDrafts[provider.uuid];
  const fields = getProviderConfigFields(provider.provider_type);
  for (const field of fields) {
    if (!field.required) continue;
    if (field.type === "password" && hasStoredProviderSecret(provider, field.key)) continue;
    if (!draft?.[field.key]) {
      toast.error(`${field.label} is required.`);
      return false;
    }
  }
  return true;
}

function saveProvider(provider) {
  if (!validateDraft(provider)) return;
  pendingSave.value = provider;
  stepUp.requireStepUp(performSave);
}

async function performSave() {
  const provider = pendingSave.value;
  if (!provider) return;

  savingUuid.value = provider.uuid;
  try {
    const config = buildProviderConfigPayload(
      provider.provider_type,
      configDrafts[provider.uuid],
      provider.config
    );
    await store.saveProvider(provider.uuid, {
      config,
    });
    toast.success(`${provider.name} configuration saved.`);
    const providers = await store.fetchProviders(resolvedProviderType());
    initDrafts(providers);
  } catch {
    // store.error surfaced below
  } finally {
    savingUuid.value = null;
    pendingSave.value = null;
  }
}

function testProvider(uuid) {
  store
    .testProvider(uuid)
    .then((result) => {
      toast.success(result.message || "Connection test completed.");
      loadProviders();
    })
    .catch(() => {});
}
</script>

<template>
  <div class="vb-page space-y-section">
    <PageHeader
      :title="title"
      subtitle="Configure Arkesel SMS credentials, SMTP settings, and test connectivity. Enable channels from Feature Flags."
      :breadcrumbs="[
        { label: 'Settings', to: r.overview },
        { label: 'Integrations', to: r.integrations.hub },
        { label: title },
      ]"
    />
    <ModuleNav :items="settingsNav" />
    <VAlert v-if="store.error" variant="error" dismissible @dismiss="store.clearError()">
      {{ store.error }}
    </VAlert>
    <LoadingSkeleton v-if="store.loading && !store.providers.length" variant="list" :rows="4" />

    <EmptyState
      v-else-if="!store.providers.length"
      icon="communications"
      title="No providers found"
      description="Run database migrations to seed default communication providers."
    />

    <div v-else class="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <VCard
        v-for="provider in store.providers"
        :id="`provider-${provider.provider_type}`"
        :key="provider.uuid"
        padding="sm"
        :title="provider.name || providerLabel(provider.provider_type)"
      >
        <template #header>
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold text-ink-primary">
                {{ provider.name || providerLabel(provider.provider_type) }}
              </h3>
              <p class="mt-1 text-sm text-ink-secondary">{{ providerLabel(provider.provider_type) }}</p>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <OpsHealthBadge
                :status="provider.connection_status === 'connected' ? 'healthy' : 'warning'"
              />
            </div>
          </div>
        </template>

        <ProviderConfigForm
          v-if="configDrafts[provider.uuid]"
          v-model="configDrafts[provider.uuid]"
          :provider-type="provider.provider_type"
          :provider="provider"
        />

        <p v-if="provider.last_error" class="mt-4 rounded-input border border-danger-200 bg-danger-50 px-3 py-2 text-xs text-danger-700">
          {{ provider.last_error }}
        </p>

        <div class="mt-4 flex flex-wrap gap-2">
          <VButton
            size="sm"
            :loading="savingUuid === provider.uuid"
            @click="saveProvider(provider)"
          >
            Save configuration
          </VButton>
          <VButton size="sm" variant="secondary" :loading="store.actionLoading" @click="testProvider(provider.uuid)">
            Test connection
          </VButton>
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
