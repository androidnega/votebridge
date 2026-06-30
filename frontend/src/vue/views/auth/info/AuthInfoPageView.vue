<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getAuthInfoContent } from "@/config/authInfoContent";

const route = useRoute();
const router = useRouter();

const page = computed(() => getAuthInfoContent(route.meta.infoSlug));

function backToLogin() {
  router.push({ name: "auth-login" });
}
</script>

<template>
  <article v-if="page" class="flex min-h-0 flex-1 flex-col">
    <header class="shrink-0 pb-4">
      <h1 class="text-lg font-semibold text-slate-800">{{ page.title }}</h1>
      <p class="mt-1 text-sm text-slate-600">{{ page.intro }}</p>
    </header>

    <div class="vb-auth-info-scroll">
      <dl class="divide-y divide-border">
        <div v-for="section in page.sections" :key="section.heading" class="py-3 first:pt-0 last:pb-0">
          <dt class="text-sm font-medium text-slate-800">{{ section.heading }}</dt>
          <dd class="mt-1 text-sm leading-relaxed text-slate-600">{{ section.body }}</dd>
        </div>
      </dl>
    </div>
  </article>

  <div v-else class="space-y-4 text-center">
    <p class="text-sm text-slate-600">This information page is not available.</p>
    <button
      type="button"
      class="text-sm font-medium text-brand-700 hover:underline"
      @click="backToLogin"
    >
      Back to sign in
    </button>
  </div>
</template>
