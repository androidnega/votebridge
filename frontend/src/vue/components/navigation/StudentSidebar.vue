<script setup>
import { useRoute, useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import { studentPrimaryNav, studentSupportNav } from "@/config/studentPortalNav";
import { useAuthStore } from "@/stores/auth";

defineProps({
  collapsed: { type: Boolean, default: false },
  onNavigate: { type: Function, default: null },
});

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

function isActive(item) {
  if (item.key === "home") return route.path === item.to;
  return route.path === item.to || route.path.startsWith(`${item.to}/`);
}

async function handleLogout() {
  await authStore.logout();
  router.push({ name: "auth-login" });
}
</script>

<template>
  <nav class="flex flex-1 flex-col" aria-label="Student navigation">
    <ul role="list" class="flex flex-1 flex-col gap-y-1">
      <li v-for="item in studentPrimaryNav" :key="item.key">
        <router-link
          :to="item.to"
          class="vb-sidebar-link"
          :class="isActive(item) ? 'vb-sidebar-link--active' : ''"
          @click="onNavigate?.()"
        >
          <VIcon
            :name="item.icon"
            class="vb-sidebar-icon"
            :class="isActive(item) ? 'vb-sidebar-icon--active' : ''"
          />
          <span v-if="!collapsed" class="truncate">{{ item.name }}</span>
        </router-link>
      </li>
    </ul>

    <div class="mt-8 border-t border-shell-sidebar-border pt-5">
      <p
        v-if="!collapsed"
        class="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-ink-secondary"
      >
        Support
      </p>
      <ul role="list" class="space-y-1">
        <li v-for="item in studentSupportNav" :key="item.key">
          <router-link :to="item.to" class="vb-sidebar-link" @click="onNavigate?.()">
            <VIcon :name="item.icon" class="vb-sidebar-icon" />
            <span v-if="!collapsed" class="truncate">{{ item.name }}</span>
          </router-link>
        </li>
        <li>
          <button type="button" class="vb-sidebar-footer-btn w-full" @click="handleLogout">
            <VIcon name="logout" class="vb-sidebar-icon" />
            <span v-if="!collapsed">Log out</span>
          </button>
        </li>
      </ul>
    </div>
  </nav>
</template>
