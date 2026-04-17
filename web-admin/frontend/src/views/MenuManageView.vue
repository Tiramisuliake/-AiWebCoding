<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { createMenu, deleteMenu, fetchMenuTree, updateMenu } from "../api/rbac";
import { useI18n } from "../composables/useI18n";
import { useMenuStore } from "../stores/menu";

const { t } = useI18n();
const menuStore = useMenuStore();
const loading = ref(false);
const submitting = ref(false);
const items = ref([]);
const dialogVisible = ref(false);
const mode = ref("create");
const searchForm = reactive({
  name: []
});
const MAX_SEARCH_ITEMS = 5;

const formRef = ref();
const form = reactive({
  id: null,
  name: "",
  parent_id: null,
  route_path: "",
  icon: "",
  sort: 0,
  is_visible: true,
  is_enabled: true,
  permission_code: ""
});

const rules = {
  name: [{ required: true, message: "Menu name is required", trigger: "blur" }]
};

function normalizeError(error, fallbackKey) {
  return error.response?.data?.msg || error.message || t(fallbackKey);
}

function uniqueStrings(values) {
  return [...new Set((values || []).map((item) => String(item || "").trim()).filter(Boolean))];
}

function encodeSearchTerms(values) {
  const uniqueValues = uniqueStrings(values);
  return uniqueValues.length ? uniqueValues.join(",") : undefined;
}

function enforceMaxSearchItems(values) {
  const uniqueValues = uniqueStrings(values);
  if (uniqueValues.length <= MAX_SEARCH_ITEMS) {
    searchForm.name = uniqueValues;
    return;
  }
  searchForm.name = uniqueValues.slice(0, MAX_SEARCH_ITEMS);
  ElMessage.warning(t("common.maxSearchItems", { count: MAX_SEARCH_ITEMS }));
}

function walkTree(nodes, level = 0, acc = []) {
  for (const node of nodes || []) {
    acc.push({ id: node.id, name: node.name, level });
    if (node.children?.length) {
      walkTree(node.children, level + 1, acc);
    }
  }
  return acc;
}

const parentOptions = computed(() => {
  const all = walkTree(items.value);
  return all.filter((item) => item.id !== form.id);
});

const menuNameCandidates = computed(() => {
  const all = walkTree(items.value).map((item) => item.name);
  return uniqueStrings(all);
});

function resetForm() {
  form.id = null;
  form.name = "";
  form.parent_id = null;
  form.route_path = "";
  form.icon = "";
  form.sort = 0;
  form.is_visible = true;
  form.is_enabled = true;
  form.permission_code = "";
}

function openCreate(row = null) {
  mode.value = "create";
  resetForm();
  if (row) {
    form.parent_id = row.id;
  }
  dialogVisible.value = true;
}

function openEdit(row) {
  mode.value = "edit";
  form.id = row.id;
  form.name = row.name;
  form.parent_id = row.parent_id ?? null;
  form.route_path = row.route_path || "";
  form.icon = row.icon || "";
  form.sort = row.sort ?? 0;
  form.is_visible = Boolean(row.is_visible);
  form.is_enabled = Boolean(row.is_enabled);
  form.permission_code = row.permission_code || "";
  dialogVisible.value = true;
}

async function loadData() {
  loading.value = true;
  try {
    const response = await fetchMenuTree({
      name: encodeSearchTerms(searchForm.name)
    });
    if (response.code !== 0) {
      throw new Error(response.msg || t("menus.loadFailed"));
    }
    items.value = response.data.items || [];
  } catch (error) {
    ElMessage.error(normalizeError(error, "menus.loadFailed"));
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  loadData();
}

function onReset() {
  searchForm.name = [];
  loadData();
}

async function submit() {
  await formRef.value.validate();
  submitting.value = true;
  try {
    const payload = {
      name: form.name,
      parent_id: form.parent_id,
      route_path: form.route_path || null,
      icon: form.icon || null,
      sort: form.sort,
      is_visible: form.is_visible,
      is_enabled: form.is_enabled,
      permission_code: form.permission_code || null
    };
    if (mode.value === "create") {
      const response = await createMenu(payload);
      if (response.code !== 0) {
        throw new Error(response.msg || t("menus.saveFailed"));
      }
      ElMessage.success(t("menus.createSuccess"));
    } else {
      const response = await updateMenu(form.id, payload);
      if (response.code !== 0) {
        throw new Error(response.msg || t("menus.saveFailed"));
      }
      ElMessage.success(t("menus.updateSuccess"));
    }
    dialogVisible.value = false;
    await Promise.all([loadData(), menuStore.loadMyMenus()]);
  } catch (error) {
    ElMessage.error(normalizeError(error, "menus.saveFailed"));
  } finally {
    submitting.value = false;
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(
      t("menus.confirmDelete", { name: row.name }),
      t("common.confirm"),
      { type: "warning" }
    );
    const response = await deleteMenu(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("menus.deleteFailed"));
    }
    ElMessage.success(t("menus.deleteSuccess"));
    await Promise.all([loadData(), menuStore.loadMyMenus()]);
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(normalizeError(error, "menus.deleteFailed"));
    }
  }
}

onMounted(loadData);
</script>

<template>
  <section class="page-shell">
    <header class="panel-head">
      <h2>{{ t("menus.title") }}</h2>
      <div class="actions">
        <el-button :loading="loading" @click="loadData">{{ t("common.reload") }}</el-button>
        <el-button type="primary" @click="openCreate()">{{ t("menus.newMenu") }}</el-button>
      </div>
    </header>

    <el-card class="table-card">
      <div class="search-toolbar" @keyup.enter="onSearch">
        <el-form class="search-fields" :inline="true">
          <el-form-item :label="t('menus.searchName')">
            <el-select
              v-model="searchForm.name"
              multiple
              filterable
              allow-create
              default-first-option
              clearable
              collapse-tags
              collapse-tags-tooltip
              style="width: 280px"
              :no-match-text="t('common.noData')"
              :no-data-text="t('common.noData')"
              @change="enforceMaxSearchItems"
              @keyup.enter="onSearch"
            >
              <el-option v-for="item in menuNameCandidates" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="search-actions">
          <el-button type="primary" @click="onSearch">{{ t("common.search") }}</el-button>
          <el-button @click="onReset">{{ t("common.reset") }}</el-button>
        </div>
      </div>

      <el-table
        :data="items"
        :loading="loading"
        :empty-text="t('common.noData')"
        border
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children' }"
      >
        <el-table-column prop="name" :label="t('menus.name')" min-width="180" />
        <el-table-column prop="route_path" :label="t('menus.route')" min-width="160" />
        <el-table-column prop="icon" :label="t('menus.icon')" width="120" />
        <el-table-column prop="sort" :label="t('menus.sort')" width="90" />
        <el-table-column :label="t('menus.visible')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_visible ? 'success' : 'info'">
              {{ row.is_visible ? t("common.yes") : t("common.no") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('menus.enabled')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'">
              {{ row.is_enabled ? t("common.yes") : t("common.no") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_code" :label="t('menus.permissionCode')" min-width="150" />
        <el-table-column :label="t('common.actions')" width="280" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="success" @click="openCreate(row)">{{ t("menus.newChild") }}</el-button>
              <el-button link type="primary" @click="openEdit(row)">{{ t("common.edit") }}</el-button>
              <el-button link type="danger" @click="remove(row)">{{ t("common.delete") }}</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="mode === 'create' ? t('menus.createMenu') : t('menus.editMenu')"
      width="560px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('menus.name')" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="t('menus.parent')">
          <el-select v-model="form.parent_id" clearable style="width: 100%">
            <el-option
              v-for="option in parentOptions"
              :key="option.id"
              :label="`${'--'.repeat(option.level)} ${option.name}`"
              :value="option.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('menus.route')">
          <el-input v-model="form.route_path" />
        </el-form-item>
        <el-form-item :label="t('menus.icon')">
          <el-input v-model="form.icon" />
        </el-form-item>
        <el-form-item :label="t('menus.sort')">
          <el-input-number v-model="form.sort" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item :label="t('menus.permissionCode')">
          <el-input v-model="form.permission_code" />
        </el-form-item>
        <el-form-item :label="t('menus.visible')">
          <el-switch v-model="form.is_visible" />
        </el-form-item>
        <el-form-item :label="t('menus.enabled')">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">{{ t("common.save") }}</el-button>
      </template>
    </el-dialog>
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
  background: linear-gradient(145deg, rgba(20, 184, 166, 0.12), rgba(6, 182, 212, 0.08));
  border: 1px solid rgba(8, 145, 178, 0.25);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.panel-head h2 {
  margin: 0;
}

.actions {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
  justify-content: flex-end;
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

@media (max-width: 900px) {
  .panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-toolbar {
    grid-template-columns: 1fr;
  }

  .search-actions {
    justify-content: flex-start;
  }
}
</style>

