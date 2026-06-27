<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { VButton } from "@/components/ui";
import { getAuthInfoContent } from "@/config/authInfoContent";

const route = useRoute();
const router = useRouter();

const page = computed(() => getAuthInfoContent(route.meta.infoSlug));

function backToLogin() {
  router.push({ name: "auth-login" });
}
</script>

<template>
  <article v-if="page" class="space-y-section">
    <header class="space-y-2">
      <h1 class="text-xl font-semibold text-slate-800">{{ page.title }}</h1>
      <p class="text-sm leading-relaxed text-slate-600">{{ page.intro }}</p>
    </header>

    <section
      v-for="section in page.sections"
      :key="section.heading"
      class="rounded-card border border-border bg-white p-card"
    >
      <h2 class="text-sm font-semibold text-slate-800">{{ section.heading }}</h2>
      <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ section.body }}</p>
    </section>

    <VButton variant="secondary" @click="backToLogin">
      Back to sign in
    </VButton>
  </article>

  <div v-else class="space-y-4 text-center">
    <p class="text-sm text-slate-600">This information page is not available.</p>
    <VButton variant="secondary" @click="backToLogin">Back to sign in</VButton>
  </div>
</template>
