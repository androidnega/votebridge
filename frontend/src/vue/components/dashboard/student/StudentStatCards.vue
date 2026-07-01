<script setup>
defineProps({
  activeCount: { type: Number, default: 0 },
  votesCast: { type: Number, default: 0 },
  closesIn: { type: String, default: "—" },
});
</script>

<template>
  <section class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3" aria-label="Election summary">
    <article class="student-stat-card">
      <p class="student-stat-label">Active elections</p>
      <p class="student-stat-value">{{ activeCount }}</p>
    </article>
    <article class="student-stat-card">
      <p class="student-stat-label">Votes cast this season</p>
      <p class="student-stat-value">{{ votesCast }}</p>
    </article>
    <article class="student-stat-card">
      <p class="student-stat-label">Voting closes in</p>
      <p class="student-stat-value text-brand-700">{{ closesIn }}</p>
    </article>
  </section>
</template>
