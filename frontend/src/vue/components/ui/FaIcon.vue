<script setup>
import { computed, useAttrs } from "vue";

const props = defineProps({
  icon: { type: String, required: true },
  fixedWidth: { type: Boolean, default: true },
});

defineOptions({ inheritAttrs: false });

const attrs = useAttrs();

const iconClass = computed(() => {
  const name = props.icon.startsWith("fa-") ? props.icon : `fa-${props.icon}`;
  return [
    "fa-solid",
    name,
    props.fixedWidth ? "fa-fw" : "",
    attrs.class,
  ].filter(Boolean);
});
</script>

<template>
  <i :class="iconClass" aria-hidden="true" />
</template>
