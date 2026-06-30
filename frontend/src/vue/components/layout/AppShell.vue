<script setup>
import AppSidebar from "@/components/navigation/AppSidebar.vue";
import AppTopbar from "@/components/navigation/AppTopbar.vue";
import { branding } from "@/config/branding";
import { useSidebar } from "@/composables/useSidebar";

defineProps({
  title: {
    type: String,
    default: "Dashboard",
  },
  contentWidth: {
    type: String,
    default: "wide",
    validator: (v) => ["standard", "wide", "full"].includes(v),
  },
});

const { collapsed, mobileOpen, toggleSidebar, closeMobileSidebar } = useSidebar();

const contentClass = {
  standard: "max-w-content",
  wide: "max-w-wide",
  full: "max-w-monitor",
};
</script>

<template>
  <div class="min-h-screen bg-surface-muted">
    <!-- Mobile backdrop -->
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
        class="fixed inset-0 z-40 bg-slate-900/60 lg:hidden"
        aria-hidden="true"
        @click="closeMobileSidebar"
      />
    </Transition>

    <!-- Sidebar: fixed on all breakpoints; drawer on mobile -->
    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-navy-border bg-navy transition-all duration-200 lg:z-30"
      :class="[
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        collapsed ? 'w-sidebar-collapsed' : 'w-sidebar',
      ]"
      :aria-label="`${branding.systemName} navigation`"
    >
      <div
        class="flex h-topbar shrink-0 items-center border-b border-navy-border"
        :class="collapsed ? 'justify-center' : 'gap-3 px-5'"
      >
        <div
          class="flex shrink-0 items-center justify-center overflow-hidden"
          :class="
            collapsed
              ? 'h-11 w-11'
              : 'h-9 w-9 rounded-lg bg-brand-600 text-xs font-bold text-white'
          "
          aria-hidden="true"
        >
          <img
            v-if="branding.institutionLogoUrl"
            :src="branding.institutionLogoUrl"
            :alt="`${branding.institutionName} logo`"
            :class="collapsed ? 'h-9 w-9 object-contain' : 'h-full w-full object-contain p-1'"
          />
          <span v-else :class="collapsed ? 'text-xs font-bold text-white' : ''">VB</span>
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <p class="truncate text-sm font-semibold text-white">{{ branding.systemName }}</p>
          <p class="truncate text-xs text-slate-400">{{ branding.institutionName }}</p>
        </div>
      </div>

      <div
        class="flex flex-1 flex-col overflow-y-auto py-4"
        :class="collapsed ? '' : 'px-3'"
        @click="closeMobileSidebar"
      >
        <AppSidebar :collapsed="collapsed" />
      </div>
    </aside>

    <!-- Main column: padded on desktop so content never sits under the sidebar -->
    <div
      class="flex min-h-screen min-w-0 flex-col transition-[padding] duration-200"
      :class="collapsed ? 'lg:pl-sidebar-collapsed' : 'lg:pl-sidebar'"
    >
      <AppTopbar :title="title" @toggle-sidebar="toggleSidebar">
        <template #actions>
          <slot name="topbar-actions" />
        </template>
      </AppTopbar>

      <main class="w-full flex-1 px-4 py-6 sm:px-page sm:py-page">
        <div class="mx-auto w-full vb-fade-in" :class="contentClass[contentWidth]">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>
