<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import { VButton } from "@/components/ui";
import { getAdminSoftPalette } from "@/config/adminWorkspace";

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  value: { type: [String, Number], default: null },
  meta: { type: String, default: "" },
  to: { type: String, default: "" },
  actionLabel: { type: String, default: "Manage" },
  paletteKey: { type: String, default: "neutral" },
  icon: { type: String, default: "elections" },
  disabled: Boolean,
});

const router = useRouter();

const palette = computed(() => getAdminSoftPalette(props.paletteKey));

function open() {
  if (props.disabled || !props.to) return;
  router.push(props.to);
}
</script>

<template>
  <article
    class="flex min-h-[9.5rem] flex-col rounded-card border p-4 shadow-card transition"
    :class="disabled ? 'opacity-60' : 'hover:brightness-[0.98]'"
    :style="{ backgroundColor: palette.bg, borderColor: palette.border }"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <h3 class="text-sm font-semibold text-slate-900">{{ title }}</h3>
        <p v-if="description" class="mt-1 text-xs leading-relaxed text-slate-600">{{ description }}</p>
      </div>
      <span
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border"
        :style="{ backgroundColor: palette.iconBg, borderColor: palette.border, color: palette.icon }"
        aria-hidden="true"
      >
        <VIcon :name="icon" size="sm" />
      </span>
    </div>

    <div v-if="value !== null || meta" class="mt-3">
      <p v-if="value !== null" class="text-2xl font-semibold text-slate-900">{{ value }}</p>
      <p v-if="meta" class="mt-0.5 text-xs text-slate-500">{{ meta }}</p>
    </div>

    <div class="mt-auto pt-4">
      <VButton
        size="sm"
        variant="secondary"
        class="!border-slate-300 !bg-white/80"
        :disabled="disabled || !to"
        @click="open"
      >
        {{ actionLabel }}
      </VButton>
    </div>
  </article>
</template>
