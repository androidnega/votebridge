<script setup>
import { computed, reactive, watch } from "vue";
import { VButton, VInput } from "@/components/ui";

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
  sensitive: Boolean,
});

const emit = defineEmits(["save"]);

const form = reactive({});

watch(
  () => props.items,
  (items) => {
    items.forEach((item) => {
      const shortKey = item.key.includes(".") ? item.key.split(".").slice(1).join(".") : item.key;
      const val = item.value;
      form[shortKey] = item.is_sensitive && val === "***" ? "" : val;
    });
  },
  { immediate: true }
);

const fields = computed(() =>
  props.items.map((item) => ({
    ...item,
    shortKey: item.key.includes(".") ? item.key.split(".").slice(1).join(".") : item.key,
  }))
);

function submit() {
  const updates = {};
  fields.value.forEach((field) => {
    updates[field.shortKey] = form[field.shortKey];
  });
  emit("save", updates);
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div
      v-for="field in fields"
      :key="field.key"
      class="grid gap-2 border-b border-border pb-4 last:border-0"
    >
      <label v-if="typeof field.value === 'boolean'" class="flex items-center gap-3 text-sm">
        <input v-model="form[field.shortKey]" type="checkbox" class="h-4 w-4 rounded border-border" />
        <span>{{ field.description || field.shortKey }}</span>
      </label>
      <VInput
        v-else
        v-model="form[field.shortKey]"
        :label="field.description || field.shortKey"
        :type="field.is_sensitive ? 'password' : 'text'"
        :hint="field.is_sensitive ? 'Leave blank to keep current value' : undefined"
      />
      <p class="text-xs text-slate-500">Version {{ field.version }} · Updated {{ new Date(field.updated_at).toLocaleString() }}</p>
    </div>
    <div class="flex justify-end">
      <VButton type="submit" variant="primary" :loading="loading">
        {{ sensitive ? "Save (requires verification)" : "Save changes" }}
      </VButton>
    </div>
  </form>
</template>
