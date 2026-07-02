<script setup>
import { useRoute, useRouter } from "vue-router";
import VIcon from "@/components/ui/VIcon.vue";
import VTooltip from "@/components/ui/VTooltip.vue";
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
      <li v-for="item in studentPrimaryNav" :key="item.key" :class="collapsed ? 'flex justify-center' : ''">
        <VTooltip v-if="collapsed" :label="item.name" position="right">
          <router-link
            :to="item.to"
            :aria-label="item.name"
            class="student-nav-link student-nav-link--collapsed"
            :class="isActive(item) ? 'student-nav-link--active' : ''"
            @click="onNavigate?.()"
          >
            <VIcon
              :name="item.icon"
              class="student-nav-icon"
              :class="isActive(item) ? 'student-nav-icon--active' : ''"
            />
          </router-link>
        </VTooltip>
        <router-link
          v-else
          :to="item.to"
          class="student-nav-link"
          :class="isActive(item) ? 'student-nav-link--active' : ''"
          @click="onNavigate?.()"
        >
          <VIcon
            :name="item.icon"
            class="student-nav-icon"
            :class="isActive(item) ? 'student-nav-icon--active' : ''"
          />
          <span class="truncate">{{ item.name }}</span>
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
        <li v-for="item in studentSupportNav" :key="item.key" :class="collapsed ? 'flex justify-center' : ''">
          <VTooltip v-if="collapsed" :label="item.name" position="right">
            <router-link
              :to="item.to"
              :aria-label="item.name"
              class="student-nav-link student-nav-link--collapsed"
              @click="onNavigate?.()"
            >
              <VIcon :name="item.icon" class="student-nav-icon" />
            </router-link>
          </VTooltip>
          <router-link v-else :to="item.to" class="student-nav-link" @click="onNavigate?.()">
            <VIcon :name="item.icon" class="student-nav-icon" />
            <span class="truncate">{{ item.name }}</span>
          </router-link>
        </li>
        <li :class="collapsed ? 'flex justify-center' : ''">
          <VTooltip v-if="collapsed" label="Log out" position="right">
            <button
              type="button"
              class="student-nav-footer-btn student-nav-link--collapsed !justify-center"
              aria-label="Log out"
              @click="handleLogout"
            >
              <VIcon name="logout" class="student-nav-icon" />
            </button>
          </VTooltip>
          <button v-else type="button" class="student-nav-footer-btn w-full" @click="handleLogout">
            <VIcon name="logout" class="student-nav-icon" />
            <span>Log out</span>
          </button>
        </li>
      </ul>
    </div>
  </nav>
</template>
