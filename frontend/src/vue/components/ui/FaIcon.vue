<script setup>
defineProps({
  icon: { type: String, required: true },
  fixedWidth: { type: Boolean, default: true },
});
</script>

<template>
  <i
    class="fa-solid"
    :class="[icon, fixedWidth ? 'fa-fw' : '']"
    aria-hidden="true"
  />
</template>
