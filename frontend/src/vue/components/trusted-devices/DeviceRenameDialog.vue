<script setup>
import { ref, watch } from "vue";
import { VButton, VInput, VModal } from "@/components/ui";

const props = defineProps({
  open: { type: Boolean, default: false },
  device: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["close", "save"]);

const name = ref("");

watch(
  () => props.open,
  (val) => {
    if (val && props.device) name.value = props.device.device_name || "";
  }
);

function submit() {
  emit("save", name.value.trim());
}
</script>

<template>
  <VModal :open="open" title="Rename device" @close="emit('close')">
    <VInput v-model="name" label="Device name" placeholder="e.g. Office MacBook" />
    <div class="mt-4 flex justify-end gap-3">
      <VButton variant="secondary" @click="emit('close')">Cancel</VButton>
      <VButton variant="primary" :loading="loading" @click="submit">Save</VButton>
    </div>
  </VModal>
</template>
