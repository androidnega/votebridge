<script setup>
import StudentProfileMenu from "@/components/navigation/StudentProfileMenu.vue";
import VIcon from "@/components/ui/VIcon.vue";

defineProps({
  title: { type: String, default: "Dashboard" },
});

defineEmits(["toggle-sidebar"]);
</script>

<template>
  <header class="student-topbar">
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="student-topbar-menu-btn"
        aria-label="Toggle sidebar"
        @click="$emit('toggle-sidebar')"
      >
        <VIcon name="panelLeft" class="h-5 w-5" />
      </button>
      <h1 class="truncate text-base font-semibold text-ink-primary lg:hidden">{{ title }}</h1>
    </div>

    <StudentProfileMenu />
  </header>
</template>
