<script setup>
import { computed, ref, watch } from "vue";
import { VButton, VInput, VModal } from "@/components/ui";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  device: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "save"]);

const name = ref("");

const open = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.device) name.value = props.device.device_name || "";
  }
);

function close() {
  open.value = false;
}

function submit() {
  emit("save", name.value.trim());
}
</script>

<template>
  <VModal v-model="open" title="Rename device">
    <VInput v-model="name" label="Device name" placeholder="e.g. Office MacBook" />
    <div class="mt-4 flex justify-end gap-3">
      <VButton variant="secondary" @click="close">Cancel</VButton>
      <VButton variant="primary" :loading="loading" @click="submit">Save</VButton>
    </div>
  </VModal>
</template>
