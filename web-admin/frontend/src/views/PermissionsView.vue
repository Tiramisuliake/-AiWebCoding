<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";

import { useI18n } from "../composables/useI18n";
import { fetchPermissions } from "../api/rbac";

const { t } = useI18n();
const loading = ref(false);
const items = ref([]);
const total = ref(0);

function getPermissionDescription(item) {
  const codeKey = String(item?.code || "").replaceAll(":", "_");
  if (!codeKey) {
    return item?.description || "";
  }
  const i18nKey = `permissions.codeDescriptions.${codeKey}`;
  const localized = t(i18nKey);
  return localized === i18nKey ? item?.description || "" : localized;
}

async function loadData() {
  loading.value = true;
  try {
    const response = await fetchPermissions();
    if (response.code !== 0) {
      throw new Error(response.msg || t("permissions.loadFailed"));
    }
    items.value = response.data.items || [];
    total.value = response.data.total || 0;
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.message || t("permissions.loadFailed"));
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <section class="page-shell">
    <header class="panel-head">
      <h2>{{ t("permissions.title") }}</h2>
      <el-button :loading="loading" @click="loadData">{{ t("common.reload") }}</el-button>
    </header>

    <el-card class="table-card">
      <el-table :data="items" :loading="loading">
        <el-table-column prop="id" :label="t('users.id')" width="80" />
        <el-table-column prop="name" :label="t('permissions.permissionName')" />
        <el-table-column prop="code" :label="t('permissions.code')" />
        <el-table-column :label="t('permissions.description')">
          <template #default="{ row }">
            {{ getPermissionDescription(row) }}
          </template>
        </el-table-column>
      </el-table>
      <div class="foot">{{ t("common.total") }}: {{ total }}</div>
    </el-card>
  </section>
</template>

<style scoped>
.page-shell {
  display: grid;
  gap: var(--space-2);
}

.panel-head {
  border-radius: 12px;
  padding: var(--space-2);
  background: linear-gradient(145deg, rgba(56, 189, 248, 0.14), rgba(37, 99, 235, 0.05));
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.panel-head h2 {
  margin: 0;
}

.table-card {
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.24);
}

.foot {
  margin-top: var(--space-2);
  color: var(--color-text-secondary);
}
</style>
