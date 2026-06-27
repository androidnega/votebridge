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
    { label: "Elections", to: "/elections", keywords: "vote ballot" },
    { label: "Results", to: "/results", keywords: "outcome standings" },
    { label: "Profile", to: "/profile", keywords: "account settings" },
    { label: "Notifications", to: "/notifications", keywords: "alerts messages" },
  ];

  if (["admin", "super_admin"].includes(role)) {
    items.push(
      { label: "Strongroom", to: "/strongroom", keywords: "integrity seal custody" },
      { label: "Communications", to: "/communications", keywords: "sms email" },
      { label: "Delivery logs", to: "/communications/logs", keywords: "messages" },
      { label: "USSD", to: "/ussd", keywords: "mobile phone" },
      { label: "Fraud dashboard", to: "/fraud", keywords: "integrity cases" },
      { label: "Security center", to: "/security", keywords: "alerts monitoring" }
    );
  }

  if (role === "super_admin") {
    items.push(
      { label: "Certification queue", to: "/results/certification", keywords: "results certify" },
      { label: "Publication center", to: "/results/publication", keywords: "publish results" },
      { label: "Archive manager", to: "/results/archive", keywords: "archive results" }
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

onMounted(() => {
  document.addEventListener("keydown", onGlobalKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", onGlobalKeydown);
});
</script>

<template>
  <div class="relative hidden sm:block">
    <label class="sr-only" for="global-search">Search pages</label>
    <div class="relative">
      <VIcon
        name="search"
        class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
      />
      <input
        id="global-search"
        ref="searchRef"
        v-model="query"
        type="search"
        placeholder="Search…"
        class="h-10 w-36 rounded-input border border-border bg-surface-muted pl-9 pr-3 text-sm text-slate-800 transition-all duration-200 placeholder:text-slate-400 focus:w-52 focus:border-brand-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-600/20 lg:w-44 lg:focus:w-64"
        autocomplete="off"
        @focus="openSearch"
        @keydown="onKeydown"
        @blur="onBlur"
      />
      <kbd
        class="pointer-events-none absolute right-2 top-1/2 hidden -translate-y-1/2 rounded border border-border bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400 lg:inline"
      >
        ⌘K
      </kbd>
    </div>

    <div
      v-if="open && filtered.length"
      class="absolute right-0 z-50 mt-2 w-72 overflow-hidden rounded-card border border-border bg-white shadow-card"
      role="listbox"
    >
      <ul>
        <li
          v-for="(item, index) in filtered"
          :key="item.to"
          role="option"
          :aria-selected="index === selectedIndex"
        >
          <button
            type="button"
            class="flex min-h-touch w-full items-center px-4 text-left text-sm transition duration-200"
            :class="
              index === selectedIndex
                ? 'bg-brand-50 text-brand-700'
                : 'text-slate-700 hover:bg-surface-muted'
            "
            @mousedown.prevent="navigate(item)"
          >
            {{ item.label }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
