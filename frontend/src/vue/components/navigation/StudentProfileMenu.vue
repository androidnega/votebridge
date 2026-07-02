<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import { branding } from "@/config/branding";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const open = ref(false);
const menuRef = ref(null);

const fullName = computed(() => authStore.fullName || authStore.user?.email || "Student");
const indexNumber = computed(() => authStore.user?.index_number || authStore.user?.student_id || "");
const email = computed(() => authStore.user?.email || "");
const phone = computed(() => authStore.user?.phone_number || "");
const initials = computed(() => {
  const parts = fullName.value.split(" ").filter(Boolean);
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return fullName.value.slice(0, 2).toUpperCase();
});

const profileRows = computed(() => {
  const rows = [
    { label: "Full name", value: fullName.value },
    { label: "Index number", value: indexNumber.value },
    { label: "Email", value: email.value },
  ];
  if (phone.value) {
    rows.push({ label: "Phone", value: phone.value });
  }
  return rows.filter((row) => row.value);
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
    <button
      type="button"
      class="student-profile-trigger ml-auto"
      :aria-expanded="open"
      aria-haspopup="menu"
      aria-label="Student profile menu"
      @click="toggle"
    >
      <div class="hidden min-w-0 text-right sm:block">
        <p class="truncate text-sm font-semibold text-ink-primary">{{ fullName }}</p>
        <p
          v-if="indexNumber"
          class="mt-0.5 flex items-center justify-end gap-1 truncate text-xs text-ink-secondary"
        >
          <span class="truncate">{{ indexNumber }}</span>
          <VIcon
            name="chevronDown"
            class="h-3.5 w-3.5 shrink-0 text-ink-secondary transition duration-150"
            :class="open ? 'rotate-180' : ''"
          />
        </p>
      </div>
      <div
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-sm font-semibold text-white"
        aria-hidden="true"
      >
        {{ initials }}
      </div>
      <VIcon
        v-if="indexNumber"
        name="chevronDown"
        class="h-4 w-4 shrink-0 text-ink-secondary transition duration-150 sm:hidden"
        :class="open ? 'rotate-180' : ''"
      />
    </button>

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
        class="absolute right-0 z-50 mt-2 w-64 origin-top-right rounded-card border border-border bg-surface py-1"
      >
        <div class="border-b border-border px-4 py-3 sm:hidden">
          <p class="truncate text-sm font-semibold text-ink-primary">{{ fullName }}</p>
          <p v-if="indexNumber" class="truncate text-xs text-ink-secondary">{{ indexNumber }}</p>
        </div>

        <div class="space-y-2 border-b border-border px-4 py-3">
          <div v-for="row in profileRows" :key="row.label">
            <p class="text-[11px] font-medium uppercase tracking-wide text-ink-secondary">
              {{ row.label }}
            </p>
            <p class="mt-0.5 truncate text-sm text-ink-primary">{{ row.value }}</p>
          </div>
        </div>

        <button
          type="button"
          role="menuitem"
          class="flex min-h-touch w-full items-center gap-3 px-4 text-left text-sm text-ink-primary transition duration-150 hover:bg-brand-50/60"
          @click="goProfile"
        >
          <VIcon name="profile" class="h-4 w-4 text-shell-sidebar-icon" />
          View profile
        </button>
        <button
          type="button"
          role="menuitem"
          class="flex min-h-touch w-full items-center gap-3 px-4 text-left text-sm text-danger-600 transition duration-150 hover:bg-danger-50"
          @click="handleLogout"
        >
          <VIcon name="logout" class="h-4 w-4" />
          Log out
        </button>
        <p class="border-t border-border px-4 py-2 text-xs text-ink-secondary">
          {{ branding.institutionName }}
        </p>
      </div>
    </Transition>
  </div>
</template>
