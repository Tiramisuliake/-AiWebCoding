<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

import { useI18n } from "../composables/useI18n";

const router = useRouter();
const { t } = useI18n();

const cards = computed(() => [
  { title: t("dashboard.backendTitle"), desc: t("dashboard.backendDesc") },
  { title: t("dashboard.frontendTitle"), desc: t("dashboard.frontendDesc") },
  { title: t("dashboard.contractTitle"), desc: t("dashboard.contractDesc") }
]);

const quickActions = computed(() => [
  { label: t("common.users"), route: "/users" },
  { label: t("common.roles"), route: "/roles" },
  { label: t("common.permissions"), route: "/permissions" }
]);

function go(routePath) {
  router.push(routePath);
}
</script>

<template>
  <section class="dashboard">
    <header class="hero">
      <div>
        <h2>{{ t("dashboard.title") }}</h2>
        <p>{{ t("dashboard.description") }}</p>
      </div>
      <div class="hero-tag">RBAC</div>
    </header>

    <div class="stats">
      <article v-for="card in cards" :key="card.title" class="stat-card">
        <h3>{{ card.title }}</h3>
        <p>{{ card.desc }}</p>
      </article>
    </div>

    <section class="quick">
      <h3>{{ t("dashboard.quickTitle") }}</h3>
      <p>{{ t("dashboard.quickDesc") }}</p>
      <div class="quick-grid">
        <button
          v-for="action in quickActions"
          :key="action.route"
          class="quick-card"
          @click="go(action.route)"
        >
          {{ action.label }}
        </button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: var(--space-2);
}

.hero {
  border-radius: 14px;
  padding: var(--space-3);
  background: linear-gradient(140deg, #1e3a8a 0%, #2563eb 45%, #60a5fa 100%);
  color: #fff;
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: var(--space-2);
}

.hero h2 {
  margin: 0;
  font-size: clamp(24px, 3vw, 30px);
}

.hero p {
  margin: 8px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.88);
}

.hero-tag {
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.35);
  font-weight: 600;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-2);
}

.stat-card {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-left: var(--accent-border-width) solid var(--color-accent);
  border-radius: 12px;
  padding: var(--space-2);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(8px);
}

.stat-card h3 {
  margin: 0 0 6px;
}

.stat-card p {
  margin: 0;
  color: var(--color-text-secondary);
}

.quick {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 12px;
  padding: var(--space-3);
}

.quick h3 {
  margin: 0;
}

.quick p {
  margin: 6px 0 var(--space-2);
  color: var(--color-text-secondary);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-2);
}

.quick-card {
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  background: linear-gradient(145deg, #ffffff, #f1f5f9);
  padding: 14px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.quick-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(30, 64, 175, 0.18);
}
</style>
