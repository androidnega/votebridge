<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { VIcon } from "@/components/ui";
import { authInfoPages } from "@/config/authInfoContent";

const open = ref(false);
const menuRef = ref(null);
const buttonRef = ref(null);

function toggleMenu() {
  open.value = !open.value;
}

function closeMenu() {
  open.value = false;
}

function onDocumentClick(event) {
  if (!open.value) return;
  const target = event.target;
  if (menuRef.value?.contains(target) || buttonRef.value?.contains(target)) return;
  closeMenu();
}

function onEscape(event) {
  if (event.key === "Escape") closeMenu();
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onEscape);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onEscape);
});
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-2 scale-95"
    >
      <div
        v-if="open"
        ref="menuRef"
        class="mb-3 w-72 overflow-hidden rounded-card border border-border bg-white shadow-card"
        role="menu"
        aria-label="Election information"
      >
        <p class="border-b border-border px-4 py-3 text-xs font-medium uppercase tracking-wide text-slate-500">
          Information
        </p>
        <ul class="py-1">
          <li v-for="item in authInfoPages" :key="item.slug">
            <RouterLink
              :to="{ name: item.routeName }"
              class="flex items-start gap-3 px-4 py-3 text-left transition hover:bg-slate-50"
              role="menuitem"
              @click="closeMenu"
            >
              <VIcon :name="item.icon" size="sm" class="mt-0.5 text-brand-600" />
              <span>
                <span class="block text-sm font-medium text-slate-800">{{ item.title }}</span>
                <span class="mt-0.5 block text-xs text-slate-500">{{ item.summary }}</span>
              </span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </Transition>

    <button
      ref="buttonRef"
      type="button"
      class="flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-white shadow-card transition hover:bg-brand-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
      :aria-expanded="open"
      aria-haspopup="menu"
      aria-label="Election information and help"
      @click="toggleMenu"
    >
      <VIcon name="help" size="lg" />
    </button>
  </div>
</template>
