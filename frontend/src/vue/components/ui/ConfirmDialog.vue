<script setup>
import VButton from "./VButton.vue";
import VIcon from "./VIcon.vue";
import VModal from "./VModal.vue";

const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: "",
  },
  confirmLabel: {
    type: String,
    default: "Confirm",
  },
  cancelLabel: {
    type: String,
    default: "Cancel",
  },
  variant: {
    type: String,
    default: "primary",
    validator: (value) => ["primary", "danger"].includes(value),
  },
  loading: Boolean,
  icon: {
    type: String,
    default: "help",
  },
});

const emit = defineEmits(["update:modelValue", "confirm", "cancel"]);

function close() {
  emit("update:modelValue", false);
  emit("cancel");
}

function confirm() {
  emit("confirm");
}
</script>

<template>
  <VModal :model-value="modelValue" :title="title" size="sm" @update:model-value="emit('update:modelValue', $event)" @close="close">
    <div class="flex gap-4">
      <div
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full"
        :class="variant === 'danger' ? 'bg-danger-50 text-danger-600' : 'bg-brand-50 text-brand-700'"
        aria-hidden="true"
      >
        <VIcon :name="icon" size="md" />
      </div>
      <p class="text-sm leading-relaxed text-slate-600">{{ description }}</p>
    </div>
    <template #footer>
      <div class="flex flex-wrap justify-end gap-2">
        <VButton variant="secondary" :disabled="loading" @click="close">{{ cancelLabel }}</VButton>
        <VButton
          :variant="variant === 'danger' ? 'danger' : 'primary'"
          :loading="loading"
          @click="confirm"
        >
          {{ confirmLabel }}
        </VButton>
      </div>
    </template>
  </VModal>
</template>
