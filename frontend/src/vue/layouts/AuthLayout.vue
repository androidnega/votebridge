<script setup>
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import AuthHelpFab from "@/components/auth/AuthHelpFab.vue";
import PublicBrandHeader from "@/components/public/PublicBrandHeader.vue";
import { VIcon } from "@/components/ui";
import { branding } from "@/config/branding";

const route = useRoute();
const isInfoPage = computed(() => Boolean(route.meta.infoPage));

const supportHref = computed(
  () => `mailto:${branding.electionOfficeEmail}?subject=VoteBridge%20support`
);
</script>

<template>
  <div class="vb-public-screen">
    <div class="vb-public-frame">
      <div class="vb-public-card" :class="isInfoPage ? 'max-w-lg' : 'max-w-md'">
        <RouterLink
          v-if="isInfoPage"
          :to="{ name: 'auth-login' }"
          class="mb-5 inline-flex min-h-touch items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-hover"
        >
          <VIcon name="chevronLeft" size="sm" />
          Back to sign in
        </RouterLink>

        <PublicBrandHeader v-else compact />

        <RouterView />
      </div>

      <a
        v-if="!isInfoPage"
        :href="supportHref"
        class="vb-public-support-link mt-4"
      >
        Help &amp; support
      </a>
    </div>

    <AuthHelpFab />
  </div>
</template>
