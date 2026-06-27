import { onMounted, ref, watch } from "vue";

const STORAGE_KEY = "vb-sidebar-collapsed";
const EXPANDED_GROUPS_KEY = "vb-sidebar-expanded-groups";

function readCollapsed() {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

function readExpandedGroups() {
  try {
    const raw = localStorage.getItem(EXPANDED_GROUPS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

const collapsed = ref(readCollapsed());
const mobileOpen = ref(false);
const expandedGroups = ref(readExpandedGroups());

watch(collapsed, (value) => {
  try {
    localStorage.setItem(STORAGE_KEY, String(value));
  } catch {
    /* ignore */
  }
});

watch(
  expandedGroups,
  (value) => {
    try {
      localStorage.setItem(EXPANDED_GROUPS_KEY, JSON.stringify(value));
    } catch {
      /* ignore */
    }
  },
  { deep: true }
);

function handleResize() {
  if (window.innerWidth >= 1024) {
    mobileOpen.value = false;
  }
}

let resizeListenerBound = false;

function ensureResizeListener() {
  if (resizeListenerBound) return;
  resizeListenerBound = true;
  window.addEventListener("resize", handleResize);
}

export function useSidebar() {
  onMounted(ensureResizeListener);

  function toggleSidebar() {
    if (window.innerWidth >= 1024) {
      collapsed.value = !collapsed.value;
    } else {
      mobileOpen.value = !mobileOpen.value;
    }
  }

  function closeMobileSidebar() {
    mobileOpen.value = false;
  }

  function toggleGroup(groupKey) {
    expandedGroups.value = {
      ...expandedGroups.value,
      [groupKey]: !expandedGroups.value[groupKey],
    };
  }

  function isGroupExpanded(groupKey) {
    return expandedGroups.value[groupKey] !== false;
  }

  return {
    collapsed,
    mobileOpen,
    expandedGroups,
    toggleSidebar,
    closeMobileSidebar,
    toggleGroup,
    isGroupExpanded,
  };
}
