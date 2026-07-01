<script setup>
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import AuthHelpFab from "@/components/auth/AuthHelpFab.vue";
import { VIcon } from "@/components/ui";

const route = useRoute();
const isInfoPage = computed(() => Boolean(route.meta.infoPage));
const isBiometricPage = computed(() => Boolean(route.meta.authBiometric));
</script>

<template>
  <div class="vb-public-screen">
    <div class="vb-public-frame">
      <div
        class="vb-public-card vb-auth-card"
        :class="
          isInfoPage
            ? 'vb-auth-info-card max-w-lg'
            : isBiometricPage
              ? 'vb-auth-biometric-card max-w-2xl'
              : 'max-w-md'
        "
      >
        <template v-if="isInfoPage">
          <RouterLink
            :to="{ name: 'auth-login' }"
            class="mb-4 inline-flex min-h-touch shrink-0 items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-hover"
          >
            <VIcon name="chevronLeft" size="sm" />
            Back to sign in
          </RouterLink>
          <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
            <RouterView />
          </div>
        </template>

        <RouterView v-else />
      </div>
    </div>

    <AuthHelpFab />
  </div>
</template>
