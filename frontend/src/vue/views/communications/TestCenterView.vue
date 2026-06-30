<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { VAlert, VButton, VInput } from "@/components/ui";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const store = useNotificationsStore();

const channel = ref("email");
const recipient = ref("");
const templateCode = ref("test_message");
const result = ref(null);

async function handleSubmit() {
  store.error = null;
  result.value = null;
  try {
    result.value = await store.sendTestMessage({
      channel: channel.value,
      recipient: recipient.value,
      template_code: templateCode.value,
      context: { first_name: "Test User" },
    });
  } catch {
    // store.error set in action
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl space-y-8">
    <div>
      <VButton variant="ghost" size="sm" class="mb-2" @click="router.push('/dashboard/communications')">
        ← Back
      </VButton>
      <h2 class="text-2xl font-bold text-slate-900">Test center</h2>
      <p class="mt-1 text-sm text-slate-500">Send a test message through the communication service.</p>
    </div>

    <form class="space-y-4 rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5" @submit.prevent="handleSubmit">
      <VInput v-model="templateCode" label="Template code" required />
      <VInput v-model="channel" label="Channel (sms, email, in_app)" required />
      <VInput v-model="recipient" label="Recipient (email or phone)" required />
      <VButton type="submit" :loading="store.actionLoading" block>
        Send test message
      </VButton>
    </form>

    <VAlert v-if="store.error" variant="error">{{ store.error }}</VAlert>
    <VAlert v-if="result" variant="success" title="Message queued">
      Delivery {{ result.status }} via {{ result.channel }} to {{ result.recipient }}.
    </VAlert>
  </div>
</template>
