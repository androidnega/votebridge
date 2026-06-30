<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import VButton from "@/components/ui/VButton.vue";
import VIcon from "@/components/ui/VIcon.vue";
import { branding } from "@/config/branding";
import { useAuthStore } from "@/stores/auth";

defineProps({
  compact: { type: Boolean, default: false },
});

const router = useRouter();
const authStore = useAuthStore();
const open = ref(false);
const menuRef = ref(null);

const userLabel = computed(() => {
  if (authStore.fullName) return authStore.fullName;
  return authStore.user?.email || authStore.user?.index_number || "Account";
});

const roleLabel = computed(() => authStore.roleDisplay || "");
const initials = computed(() => {
  const parts = userLabel.value.split(" ").filter(Boolean);
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return userLabel.value.slice(0, 2).toUpperCase();
});

function toggle() {
  open.value = !open.value;
}

function close() {
  open.value = false;
}

async function goProfile() {
  close();
  await router.push({ name: "profile" });
}

async function handleLogout() {
  close();
  await authStore.logout();
  router.push({ name: "auth-login" });
}

function onDocumentClick(event) {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    close();
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
});
</script>

<template>
  <div ref="menuRef" class="relative">
    <VButton
      variant="ghost"
      size="sm"
      :class="compact ? '!min-h-touch !px-1.5' : '!min-h-touch gap-2 !px-2'"
      :aria-expanded="open"
      aria-haspopup="menu"
      aria-label="User menu"
      @click="toggle"
    >
      <span
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700"
        aria-hidden="true"
      >
        {{ initials }}
      </span>
      <template v-if="!compact">
        <span class="hidden min-w-0 text-left md:block">
          <span class="block max-w-[10rem] truncate text-sm font-medium text-slate-800">
            {{ userLabel }}
          </span>
          <span v-if="roleLabel" class="block truncate text-xs text-slate-500">{{ roleLabel }}</span>
        </span>
        <VIcon name="chevronDown" class="hidden h-4 w-4 text-slate-400 md:block" />
      </template>
    </VButton>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="open"
        role="menu"
        class="absolute right-0 z-50 mt-2 w-56 origin-top-right rounded-card border border-border bg-white py-1 shadow-card"
      >
        <div class="border-b border-border px-4 py-3" :class="compact ? '' : 'md:hidden'">
          <p class="truncate text-sm font-medium text-slate-800">{{ userLabel }}</p>
          <p v-if="roleLabel" class="truncate text-xs text-slate-500">{{ roleLabel }}</p>
        </div>
        <button
          type="button"
          role="menuitem"
          class="flex min-h-touch w-full items-center gap-3 px-4 text-left text-sm text-slate-700 transition hover:bg-surface-muted"
          @click="goProfile"
        >
          <VIcon name="profile" class="h-4 w-4" />
          Profile
        </button>
        <button
          type="button"
          role="menuitem"
          class="flex min-h-touch w-full items-center gap-3 px-4 text-left text-sm text-danger-600 transition hover:bg-danger-50"
          @click="handleLogout"
        >
          <VIcon name="logout" class="h-4 w-4" />
          Sign out
        </button>
        <p class="border-t border-border px-4 py-2 text-xs text-slate-400">
          {{ branding.institutionName }}
        </p>
      </div>
    </Transition>
  </div>
</template>
