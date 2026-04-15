<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { useI18n } from "../composables/useI18n";
import { fetchPermissions } from "../api/rbac";

const { t } = useI18n();
const loading = ref(false);
const items = ref([]);
const total = ref(0);
const pagination = reactive({
  page: 1,
  perPage: 100
});
const searchForm = reactive({
  name: "",
  code: "",
  description: ""
});

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
    const response = await fetchPermissions({
      page: pagination.page,
      per_page: pagination.perPage,
      name: searchForm.name || undefined,
      code: searchForm.code || undefined,
      description: searchForm.description || undefined
    });
    if (response.code !== 0) {
      throw new Error(response.msg || t("permissions.loadFailed"));
    }
    items.value = response.data.items || [];
    total.value = response.data.total || 0;
    pagination.page = response.data.page || pagination.page;
    pagination.perPage = response.data.per_page || pagination.perPage;
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.message || t("permissions.loadFailed"));
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  pagination.page = 1;
  loadData();
}

function onReset() {
  searchForm.name = "";
  searchForm.code = "";
  searchForm.description = "";
  pagination.page = 1;
  loadData();
}

function onPageChange(page) {
  pagination.page = page;
  loadData();
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
      <el-form class="search-bar" :inline="true">
        <el-form-item :label="t('permissions.searchPermissionName')">
          <el-input v-model="searchForm.name" clearable @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item :label="t('permissions.searchPermissionCode')">
          <el-input v-model="searchForm.code" clearable @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item :label="t('permissions.searchDescription')">
          <el-input v-model="searchForm.description" clearable @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSearch">{{ t("common.search") }}</el-button>
          <el-button @click="onReset">{{ t("common.reset") }}</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="items" :loading="loading" :empty-text="t('common.noData')">
        <el-table-column prop="id" :label="t('users.id')" width="80" />
        <el-table-column prop="name" :label="t('permissions.permissionName')" />
        <el-table-column prop="code" :label="t('permissions.code')" />
        <el-table-column :label="t('permissions.description')">
          <template #default="{ row }">
            {{ getPermissionDescription(row) }}
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.perPage"
          :total="total"
          @current-change="onPageChange"
        />
      </div>
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

.search-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-bottom: var(--space-2);
}

.pager {
  margin-top: var(--space-2);
  display: flex;
  justify-content: flex-end;
}

.foot {
  margin-top: var(--space-2);
  color: var(--color-text-secondary);
}
</style>
