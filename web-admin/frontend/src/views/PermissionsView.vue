<script setup>
import { computed, onMounted, reactive, ref } from "vue";
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
  name: [],
  code: [],
  description: []
});
const MAX_SEARCH_ITEMS = 5;

function uniqueStrings(values) {
  return [...new Set((values || []).map((item) => String(item || "").trim()).filter(Boolean))];
}

function encodeSearchTerms(values) {
  const uniqueValues = uniqueStrings(values);
  return uniqueValues.length ? uniqueValues.join(",") : undefined;
}

function enforceMaxSearchItems(field, values) {
  const uniqueValues = uniqueStrings(values);
  if (uniqueValues.length <= MAX_SEARCH_ITEMS) {
    searchForm[field] = uniqueValues;
    return;
  }
  searchForm[field] = uniqueValues.slice(0, MAX_SEARCH_ITEMS);
  ElMessage.warning(t("common.maxSearchItems", { count: MAX_SEARCH_ITEMS }));
}

const permissionNameCandidates = computed(() => {
  return uniqueStrings(items.value.map((item) => item.name));
});

const permissionCodeCandidates = computed(() => {
  return uniqueStrings(items.value.map((item) => item.code));
});

const permissionDescriptionCandidates = computed(() => {
  return uniqueStrings(items.value.map((item) => item.description));
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
      name: encodeSearchTerms(searchForm.name),
      code: encodeSearchTerms(searchForm.code),
      description: encodeSearchTerms(searchForm.description)
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
  searchForm.name = [];
  searchForm.code = [];
  searchForm.description = [];
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
      <div class="search-toolbar" @keyup.enter="onSearch">
        <el-form class="search-fields" :inline="true">
          <el-form-item :label="t('permissions.searchPermissionName')">
            <el-select
              v-model="searchForm.name"
              multiple
              filterable
              allow-create
              default-first-option
              clearable
              collapse-tags
              collapse-tags-tooltip
              style="width: 240px"
              :no-match-text="t('common.noData')"
              :no-data-text="t('common.noData')"
              @change="(values) => enforceMaxSearchItems('name', values)"
              @keyup.enter="onSearch"
            >
              <el-option
                v-for="item in permissionNameCandidates"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('permissions.searchPermissionCode')">
            <el-select
              v-model="searchForm.code"
              multiple
              filterable
              allow-create
              default-first-option
              clearable
              collapse-tags
              collapse-tags-tooltip
              style="width: 240px"
              :no-match-text="t('common.noData')"
              :no-data-text="t('common.noData')"
              @change="(values) => enforceMaxSearchItems('code', values)"
              @keyup.enter="onSearch"
            >
              <el-option
                v-for="item in permissionCodeCandidates"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('permissions.searchDescription')">
            <el-select
              v-model="searchForm.description"
              multiple
              filterable
              allow-create
              default-first-option
              clearable
              collapse-tags
              collapse-tags-tooltip
              style="width: 240px"
              :no-match-text="t('common.noData')"
              :no-data-text="t('common.noData')"
              @change="(values) => enforceMaxSearchItems('description', values)"
              @keyup.enter="onSearch"
            >
              <el-option
                v-for="item in permissionDescriptionCandidates"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="search-actions">
          <el-button type="primary" @click="onSearch">{{ t("common.search") }}</el-button>
          <el-button @click="onReset">{{ t("common.reset") }}</el-button>
        </div>
      </div>

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

.search-toolbar {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: start;
  gap: 12px;
  margin-bottom: var(--space-2);
}

.search-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.search-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  white-space: nowrap;
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

@media (max-width: 900px) {
  .search-toolbar {
    grid-template-columns: 1fr;
  }

  .search-actions {
    justify-content: flex-start;
  }
}
</style>

