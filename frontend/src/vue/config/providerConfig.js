/** Communication provider configuration fields (Settings → Providers). */

export const ARKESEL_SMS_DEFAULT_URL = "https://sms.arkesel.com/api/v2/sms/send";

export const providerConfigFields = {
  arkesel_sms: [
    {
      key: "api_key",
      label: "API key",
      type: "password",
      required: true,
      placeholder: "Enter your Arkesel API key",
      help: "Leave blank when saving to keep the existing key.",
    },
    {
      key: "sender_id",
      label: "Sender ID",
      type: "text",
      required: true,
      placeholder: "e.g. VoteBridge",
    },
    {
      key: "url",
      label: "API URL",
      type: "url",
      required: false,
      placeholder: ARKESEL_SMS_DEFAULT_URL,
    },
  ],
  moolre_sms: [
    {
      key: "vas_key",
      label: "VAS key",
      type: "password",
      required: true,
      placeholder: "Enter your Moolre VAS key",
      help: "Leave blank when saving to keep the existing key.",
    },
    {
      key: "sender_id",
      label: "Sender ID",
      type: "text",
      required: true,
      placeholder: "e.g. VoteBridge",
      help: "Max 11 characters. Must be registered with Moolre.",
    },
    {
      key: "environment",
      label: "Environment",
      type: "select",
      required: true,
      options: [
        { value: "live", label: "Live" },
        { value: "sandbox", label: "Sandbox" },
      ],
    },
  ],
  smtp_email: [
    {
      key: "from_email",
      label: "From email",
      type: "email",
      required: false,
      placeholder: "noreply@institution.edu.gh",
    },
  ],
};

export function getProviderConfigFields(providerType) {
  return providerConfigFields[providerType] || [];
}

export function getProviderSecretKeys(providerType) {
  return getProviderConfigFields(providerType)
    .filter((field) => field.type === "password")
    .map((field) => field.key);
}

export function defaultProviderConfig(providerType) {
  if (providerType === "arkesel_sms") {
    return { api_key: "", sender_id: "", url: ARKESEL_SMS_DEFAULT_URL };
  }
  if (providerType === "moolre_sms") {
    return { vas_key: "", sender_id: "", environment: "live" };
  }
  if (providerType === "smtp_email") {
    return { from_email: "" };
  }
  return {};
}

export function buildProviderConfigPayload(providerType, draft, existingConfig = {}) {
  const fields = getProviderConfigFields(providerType);
  const config = {};

  for (const field of fields) {
    const value = draft[field.key];
    if (field.type === "password") {
      if (value && value !== "***") {
        config[field.key] = value;
      }
      continue;
    }
    if (value !== undefined && value !== "") {
      config[field.key] = value;
    } else if (existingConfig[field.key] && field.type !== "password") {
      config[field.key] = existingConfig[field.key];
    }
  }

  return config;
}

export function draftFromProvider(provider) {
  const base = defaultProviderConfig(provider.provider_type);
  const config = provider.config || {};
  const secretKeys = getProviderSecretKeys(provider.provider_type);
  return {
    ...base,
    ...Object.fromEntries(
      Object.entries(config).filter(([key]) => !secretKeys.includes(key))
    ),
    ...Object.fromEntries(secretKeys.map((key) => [key, ""])),
  };
}

export function hasStoredProviderSecret(provider, fieldKey) {
  return provider.config?.[fieldKey] === "***";
}
