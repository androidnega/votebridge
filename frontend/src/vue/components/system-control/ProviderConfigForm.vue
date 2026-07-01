<script setup>
import { computed } from "vue";
import { getProviderConfigFields } from "@/config/providerConfig";
import { VInput } from "@/components/ui";

const props = defineProps({
  providerType: { type: String, required: true },
  modelValue: { type: Object, required: true },
  hasStoredSecret: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

const fields = computed(() => getProviderConfigFields(props.providerType));

function updateField(key, value) {
  emit("update:modelValue", { ...props.modelValue, [key]: value });
}
</script>

<template>
  <div v-if="fields.length" class="space-y-4">
    <div v-for="field in fields" :key="field.key">
      <VInput
        :model-value="modelValue[field.key]"
        :label="field.label"
        :type="field.type"
        :placeholder="field.placeholder"
        :autocomplete="field.type === 'password' ? 'off' : undefined"
        @update:model-value="updateField(field.key, $event)"
      />
      <p v-if="field.type === 'password' && hasStoredSecret" class="mt-1 text-xs text-slate-500">
        A key is already saved. Enter a new value only to replace it.
      </p>
      <p v-else-if="field.help" class="mt-1 text-xs text-slate-500">{{ field.help }}</p>
    </div>
  </div>
  <p v-else class="text-sm text-slate-500">No configurable fields for this provider type.</p>
</template>
