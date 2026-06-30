<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VAlert, VButton } from "@/components/ui";
import { useStrongroomStore } from "@/stores/strongroom";

const TERMINAL_LABELS = {
  waiting_for_custodian_1: "Waiting for Custodian 1",
  waiting_for_custodian_2: "Waiting for Custodian 2",
  waiting_for_custodian_3: "Waiting for Custodian 3",
  waiting_for_custodian_4: "Waiting for Custodian 4",
  access_granted: "Access Granted",
  access_denied: "Access Denied",
  vault_resealed: "Vault Resealed",
  session_expired: "Session Expired",
};

const route = useRoute();
const router = useRouter();
const store = useStrongroomStore();

const sessionUuid = computed(() => route.params.sessionUuid);
const electionUuid = computed(() => route.params.uuid);
const identifier = ref("");
const password = ref("");
const statusLine = ref("Initializing secure channel…");
const pollTimer = ref(null);

const terminalState = computed(() => store.vaultSession?.terminal_state || "waiting_for_custodian_1");
const statusLabel = computed(() => TERMINAL_LABELS[terminalState.value] || terminalState.value);
const awaitingAuth = computed(() => terminalState.value.startsWith("waiting_for_custodian"));
const accessGranted = computed(() => store.vaultSession?.status === "active");

async function refreshSession() {
  await store.fetchVaultSession(sessionUuid.value);
  if (accessGranted.value) {
    statusLine.value = "Opening Strong Room…";
    router.replace({
      name: "election-vault-evidence",
      params: { uuid: electionUuid.value, sessionUuid: sessionUuid.value },
    });
  }
}

async function authenticate() {
  statusLine.value = "Verifying credentials…";
  try {
    await store.authenticateCustodian(sessionUuid.value, {
      identifier: identifier.value.trim(),
      password: password.value,
    });
    identifier.value = "";
    password.value = "";
    statusLine.value = statusLabel.value;
    if (accessGranted.value) {
      await refreshSession();
    }
  } catch {
    statusLine.value = "Access Denied";
  }
}

onMounted(async () => {
  await store.fetchVaultSession(sessionUuid.value).catch(() => {});
  statusLine.value = statusLabel.value;
  pollTimer.value = window.setInterval(() => {
    store.fetchVaultSession(sessionUuid.value).then(() => {
      if (accessGranted.value) refreshSession();
    }).catch(() => {});
  }, 30000);
});

onUnmounted(() => {
  if (pollTimer.value) window.clearInterval(pollTimer.value);
});
</script>

<template>
  <div class="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4">
    <div class="vb-vault-terminal w-full max-w-2xl">
      <p class="vb-vault-terminal-label">Secure electoral vault — authentication terminal</p>
      <p class="mt-2 font-mono text-sm text-green-400">{{ statusLine }}</p>
      <p class="mt-1 font-mono text-xs text-slate-500">{{ statusLabel }}</p>

      <VAlert v-if="store.error" class="mt-4" variant="error">{{ store.error }}</VAlert>

      <form v-if="awaitingAuth" class="mt-6 space-y-4" @submit.prevent="authenticate">
        <div>
          <label class="mb-1 block font-mono text-xs uppercase tracking-widest text-slate-500" for="vault-id">
            Custodian identity
          </label>
          <input
            id="vault-id"
            v-model="identifier"
            type="text"
            autocomplete="username"
            class="vb-vault-terminal-input"
            placeholder="Index number or email"
          />
        </div>
        <div>
          <label class="mb-1 block font-mono text-xs uppercase tracking-widest text-slate-500" for="vault-pass">
            Password
          </label>
          <input
            id="vault-pass"
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="vb-vault-terminal-input"
          />
        </div>
        <VButton type="submit" class="w-full" :loading="store.actionLoading">Authenticate custodian</VButton>
      </form>

      <p class="vb-vault-terminal-cursor mt-6 font-mono text-green-500">
        <span class="text-slate-600">&gt;</span> _
      </p>
    </div>
  </div>
</template>
