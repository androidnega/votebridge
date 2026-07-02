<script setup>
import StudentMobileNav from "@/components/navigation/StudentMobileNav.vue";
import StudentSidebar from "@/components/navigation/StudentSidebar.vue";
import StudentTopbar from "@/components/navigation/StudentTopbar.vue";
import { branding } from "@/config/branding";
import { useSidebar } from "@/composables/useSidebar";

defineProps({
  title: { type: String, default: "Dashboard" },
});

const { collapsed, mobileOpen, toggleSidebar, closeMobileSidebar } = useSidebar();
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mobileOpen"
        class="fixed inset-0 z-40 bg-slate-900/40 lg:hidden"
        aria-hidden="true"
        @click="closeMobileSidebar"
      />
    </Transition>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-shell-sidebar-border bg-shell-sidebar transition-all duration-200 lg:z-30"
      :class="[
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        collapsed ? 'w-sidebar-collapsed' : 'w-sidebar',
      ]"
      :aria-label="`${branding.systemName} student navigation`"
    >
      <div
        class="flex h-topbar shrink-0 items-center border-b border-shell-sidebar-border bg-shell-sidebar"
        :class="collapsed ? 'justify-center' : 'gap-3 px-5'"
      >
        <div class="vb-sidebar-brand shrink-0" aria-hidden="true">VB</div>
        <div v-if="!collapsed" class="min-w-0">
          <p class="truncate text-sm font-semibold text-ink-primary">{{ branding.systemName }}</p>
          <p class="truncate text-xs text-ink-secondary">{{ branding.institutionName }}</p>
        </div>
      </div>

      <div
        class="flex flex-1 flex-col overflow-y-auto py-5"
        :class="collapsed ? '' : 'px-3'"
        @click="closeMobileSidebar"
      >
        <StudentSidebar :collapsed="collapsed" :on-navigate="closeMobileSidebar" />
      </div>
    </aside>

    <div
      class="flex min-h-screen min-w-0 flex-col bg-surface-muted transition-[padding] duration-200"
      :class="collapsed ? 'lg:pl-sidebar-collapsed' : 'lg:pl-sidebar'"
    >
      <StudentTopbar :title="title" @toggle-sidebar="toggleSidebar" />

      <main class="w-full flex-1 px-4 py-5 pb-24 sm:px-6 sm:py-6 lg:pb-6 lg:px-8">
        <div class="mx-auto w-full max-w-6xl vb-fade-in">
          <slot />
        </div>
      </main>
    </div>

    <StudentMobileNav />
  </div>
</template>
