import { computed, ref } from "vue";
import { ussdApi } from "@/api/ussd";
import { normalizeHealthStatus } from "@/config/systemControlHub";
import { useSystemControlStore } from "@/stores/systemControl";

function formatTimestamp(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function useSettingsIntegrations() {
  const store = useSystemControlStore();
  const ussdIntegration = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const testingKey = ref(null);

  async function load() {
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([
        store.fetchOverview(),
        store.fetchProviders(),
        ussdApi.getIntegration().then((data) => {
          ussdIntegration.value = data;
        }),
      ]);
    } catch (err) {
      error.value = err?.message || "Could not load integration status.";
    } finally {
      loading.value = false;
    }
  }

  const smsProvider = computed(() =>
    store.providers.find((provider) => provider.provider_type === "sms")
  );

  const emailProvider = computed(() =>
    store.providers.find((provider) => provider.provider_type === "email")
  );

  const overviewIntegrations = computed(() => store.overview?.integrations || {});

  const integrations = computed(() => [
    {
      key: "sms",
      name: "Arkesel SMS",
      status: smsProvider.value?.connection_status || overviewIntegrations.value.sms?.status,
      lastSync: smsProvider.value?.last_success_at || overviewIntegrations.value.sms?.last_sync,
      lastError: smsProvider.value?.last_error || overviewIntegrations.value.sms?.last_error,
      configRoute: "/dashboard/settings/providers",
      providerUuid: smsProvider.value?.uuid,
    },
    {
      key: "ussd",
      name: "Arkesel USSD",
      status: ussdIntegration.value?.health_status || overviewIntegrations.value.ussd?.status,
      lastSync: ussdIntegration.value?.health?.checked_at || overviewIntegrations.value.ussd?.last_sync,
      lastError: ussdIntegration.value?.health?.message || overviewIntegrations.value.ussd?.last_error,
      configRoute: "/dashboard/settings/ussd",
      providerUuid: null,
    },
    {
      key: "email",
      name: "Email",
      status: emailProvider.value?.connection_status || overviewIntegrations.value.email?.status,
      lastSync: emailProvider.value?.last_success_at || overviewIntegrations.value.email?.last_sync,
      lastError: emailProvider.value?.last_error || overviewIntegrations.value.email?.last_error,
      configRoute: "/dashboard/settings/providers",
      providerUuid: emailProvider.value?.uuid,
    },
    {
      key: "redis",
      name: "Redis",
      status: overviewIntegrations.value.redis?.status || store.overview?.redis_status,
      lastSync: overviewIntegrations.value.redis?.last_sync,
      lastError: overviewIntegrations.value.redis?.last_error,
      configRoute: "/dashboard/settings/environment",
      providerUuid: null,
    },
    {
      key: "websockets",
      name: "WebSockets",
      status: overviewIntegrations.value.websockets?.status || store.overview?.websocket_status,
      lastSync: overviewIntegrations.value.websockets?.last_sync,
      lastError: overviewIntegrations.value.websockets?.last_error,
      configRoute: "/dashboard/settings/runtime",
      providerUuid: null,
    },
  ]);

  async function validateConnection(integration) {
    if (integration.key === "ussd") {
      ussdIntegration.value = await ussdApi.getIntegration();
      return { message: "USSD gateway health refreshed." };
    }
    if (!integration.providerUuid) {
      await store.fetchOverview();
      return { message: "Infrastructure health refreshed." };
    }
    testingKey.value = integration.key;
    try {
      return await store.testProvider(integration.providerUuid);
    } finally {
      testingKey.value = null;
    }
  }

  return {
    loading,
    error,
    testingKey,
    integrations,
    normalizeHealthStatus,
    formatTimestamp,
    load,
    validateConnection,
  };
}
