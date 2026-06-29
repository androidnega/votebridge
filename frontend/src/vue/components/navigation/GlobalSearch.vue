<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const query = ref("");
const open = ref(false);
const selectedIndex = ref(0);
const searchRef = ref(null);

const searchItems = computed(() => {
  const role = authStore.role;
  const items = [
    { label: "Overview", to: "/", keywords: "dashboard home" },
    { label: "Election workspace", to: "/elections", keywords: "vote ballot create positions candidates" },
    { label: "Results", to: "/results", keywords: "outcome standings certify publish" },
    { label: "Reports", to: "/reports", keywords: "turnout participation export" },
    { label: "Profile", to: "/profile", keywords: "account settings" },
    { label: "Notifications", to: "/notifications", keywords: "alerts messages" },
  ];

  if (role === "super_admin") {
    items.push(
      { label: "Strong room", to: "/strongroom", keywords: "integrity investigation fraud audit" },
      { label: "Certification", to: "/results/certification", keywords: "certify results" },
      { label: "Settings", to: "/settings", keywords: "configuration institution voting security" }
    );
  }

  return items;
});

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return searchItems.value.slice(0, 6);
  return searchItems.value.filter(
    (item) =>
      item.label.toLowerCase().includes(q) || item.keywords.toLowerCase().includes(q)
  );
});

function openSearch() {
  open.value = true;
  selectedIndex.value = 0;
}

function closeSearch() {
  open.value = false;
  query.value = "";
}

function onBlur() {
  window.setTimeout(() => closeSearch(), 150);
}

function navigate(item) {
  closeSearch();
  router.push(item.to);
}

function onKeydown(event) {
  if (!open.value) return;
  if (event.key === "ArrowDown") {
    event.preventDefault();
    selectedIndex.value = Math.min(selectedIndex.value + 1, filtered.value.length - 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0);
  } else if (event.key === "Enter" && filtered.value[selectedIndex.value]) {
    event.preventDefault();
    navigate(filtered.value[selectedIndex.value]);
  } else if (event.key === "Escape") {
    closeSearch();
  }
}

function onGlobalKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === "k") {
    event.preventDefault();
    openSearch();
    searchRef.value?.focus();
  }
}

onMounted(() => document.addEventListener("keydown", onGlobalKeydown));
onUnmounted(() => document.removeEventListener("keydown", onGlobalKeydown));
</script>

<template>
  <div class="relative hidden sm:block">
    <label class="sr-only" for="global-search">Search pages</label>
    <div class="relative">
      <VIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        id="global-search"
        ref="searchRef"
        v-model="query"
        type="search"
        placeholder="Search pages (⌘K)"
        class="w-64 rounded-input border border-border bg-surface py-2 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 lg:w-72"
        autocomplete="off"
        @focus="openSearch"
        @blur="onBlur"
        @keydown="onKeydown"
      />
    </div>
    <div
      v-if="open && filtered.length"
      class="absolute right-0 z-50 mt-2 w-72 overflow-hidden rounded-xl border border-border bg-surface shadow-lg lg:w-80"
    >
      <ul>
        <li v-for="(item, index) in filtered" :key="item.to">
          <button
            type="button"
            class="flex w-full items-center px-4 py-2.5 text-left text-sm transition"
            :class="index === selectedIndex ? 'bg-surface-muted text-slate-900' : 'text-slate-700 hover:bg-surface-muted'"
            @mousedown.prevent="navigate(item)"
          >
            {{ item.label }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
