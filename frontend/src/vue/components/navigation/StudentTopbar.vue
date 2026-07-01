<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";
import { useAuthStore } from "@/stores/auth";

defineProps({
  title: { type: String, default: "Dashboard" },
});

defineEmits(["toggle-sidebar"]);

const authStore = useAuthStore();

const fullName = computed(() => authStore.fullName || authStore.user?.email || "Student");
const indexNumber = computed(() => authStore.user?.index_number || authStore.user?.student_id || "");
const initials = computed(() => {
  const parts = fullName.value.split(" ").filter(Boolean);
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return fullName.value.slice(0, 2).toUpperCase();
});
</script>

<template>
  <header class="student-topbar">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="student-topbar-menu-btn lg:hidden"
        aria-label="Open menu"
        @click="$emit('toggle-sidebar')"
      >
        <VIcon name="panelLeft" class="h-5 w-5" />
      </button>
      <h1 class="truncate text-base font-semibold text-ink-primary lg:hidden">{{ title }}</h1>
    </div>

    <div class="flex min-w-0 items-center gap-3 sm:gap-4">
      <div class="hidden min-w-0 text-right sm:block">
        <p class="truncate text-sm font-semibold text-ink-primary">{{ fullName }}</p>
        <p v-if="indexNumber" class="truncate text-xs text-ink-secondary">{{ indexNumber }}</p>
      </div>
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-sm font-semibold text-white"
        aria-hidden="true"
      >
        {{ initials }}
      </div>
    </div>
  </header>
</template>
