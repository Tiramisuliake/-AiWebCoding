<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { useI18n } from "../composables/useI18n";
import {
  assignRoleMenus,
  assignRolePermissions,
  createRole,
  deleteRole,
  fetchMenuTree,
  fetchPermissions,
  fetchRoleMenus,
  fetchRolePermissions,
  fetchRoles,
  updateRole
} from "../api/rbac";

const { t } = useI18n();
const loading = ref(false);
const submitting = ref(false);
const items = ref([]);
const total = ref(0);
const pagination = reactive({
  page: 1,
  perPage: 100
});
const searchForm = reactive({
  name: []
});
const MAX_SEARCH_ITEMS = 5;
const permissionOptions = ref([]);
const menuOptions = ref([]);

const roleDialogVisible = ref(false);
const roleFormRef = ref();
const roleMode = ref("create");
const roleForm = reactive({
  id: null,
  name: "",
  description: ""
});

const permissionDialogVisible = ref(false);
const permissionSubmitting = ref(false);
const permissionTargetRole = ref(null);
const permissionSelection = ref([]);
const menuDialogVisible = ref(false);
const menuSubmitting = ref(false);
const menuTargetRole = ref(null);
const menuTreeRef = ref();

const roleRules = {
  name: [{ required: true, message: t("roles.roleNameRequired"), trigger: "blur" }]
};

function normalizeError(error, fallbackKey) {
  return error.response?.data?.msg || error.message || t(fallbackKey);
}

function showWarnings(payload) {
  const warnings = payload?.warnings;
  if (!Array.isArray(warnings)) {
    return;
  }
  for (const item of warnings) {
    if (item) {
      ElMessage.warning(String(item));
    }
  }
}

function getPermissionName(permission) {
  const codeKey = String(permission?.code || "").replaceAll(":", "_");
  if (!codeKey) {
    return permission?.name || "";
  }
  const i18nKey = `permissions.codeNames.${codeKey}`;
  const localized = t(i18nKey);
  return localized === i18nKey ? permission?.name || "" : localized;
}

function formatPermissionLabel(permission) {
  const permissionName = getPermissionName(permission);
  const permissionCode = permission?.code || "";
  if (!permissionCode) {
    return permissionName;
  }
  return `${permissionName}（${permissionCode}）`;
}

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

const roleNameCandidates = computed(() => {
  return uniqueStrings(items.value.map((item) => item.name));
});

async function loadData() {
  loading.value = true;
  try {
    const [roleResponse, permissionResponse, menuResponse] = await Promise.all([
      fetchRoles({
        page: pagination.page,
        per_page: pagination.perPage,
        name: encodeSearchTerms(searchForm.name)
      }),
      fetchPermissions(),
      fetchMenuTree()
    ]);

    if (roleResponse.code !== 0) {
      throw new Error(roleResponse.msg || t("roles.loadFailed"));
    }
    if (permissionResponse.code !== 0) {
      throw new Error(permissionResponse.msg || t("permissions.loadFailed"));
    }
    if (menuResponse.code !== 0) {
      throw new Error(menuResponse.msg || t("menus.loadFailed"));
    }

    items.value = roleResponse.data.items || [];
    total.value = roleResponse.data.total || 0;
    pagination.page = roleResponse.data.page || pagination.page;
    pagination.perPage = roleResponse.data.per_page || pagination.perPage;
    permissionOptions.value = permissionResponse.data.items || [];
    menuOptions.value = menuResponse.data.items || [];
  } catch (error) {
    ElMessage.error(normalizeError(error, "roles.loadFailed"));
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
  pagination.page = 1;
  loadData();
}

function onPageChange(page) {
  pagination.page = page;
  loadData();
}

function resetRoleForm() {
  roleForm.id = null;
  roleForm.name = "";
  roleForm.description = "";
}

function openCreateDialog() {
  roleMode.value = "create";
  resetRoleForm();
  roleDialogVisible.value = true;
}

function openEditDialog(row) {
  roleMode.value = "edit";
  roleForm.id = row.id;
  roleForm.name = row.name;
  roleForm.description = row.description || "";
  roleDialogVisible.value = true;
}

async function submitRole() {
  await roleFormRef.value.validate();
  submitting.value = true;
  try {
    if (roleMode.value === "create") {
      const response = await createRole({
        name: roleForm.name,
        description: roleForm.description
      });
      if (response.code !== 0) {
        throw new Error(response.msg || t("roles.saveFailed"));
      }
      ElMessage.success(t("roles.createSuccess"));
    } else {
      const response = await updateRole(roleForm.id, {
        name: roleForm.name,
        description: roleForm.description
      });
      if (response.code !== 0) {
        throw new Error(response.msg || t("roles.saveFailed"));
      }
      ElMessage.success(t("roles.updateSuccess"));
    }
    roleDialogVisible.value = false;
    await loadData();
  } catch (error) {
    ElMessage.error(normalizeError(error, "roles.saveFailed"));
  } finally {
    submitting.value = false;
  }
}

async function removeRole(row) {
  try {
    await ElMessageBox.confirm(
      t("roles.confirmDelete", { name: row.name }),
      t("common.confirm"),
      { type: "warning" }
    );
    const response = await deleteRole(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("roles.deleteFailed"));
    }
    ElMessage.success(t("roles.deleteSuccess"));
    await loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(normalizeError(error, "roles.deleteFailed"));
    }
  }
}

async function openPermissionDialog(row) {
  permissionTargetRole.value = row;
  permissionSelection.value = [];
  permissionDialogVisible.value = true;
  try {
    const response = await fetchRolePermissions(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("roles.assignFailed"));
    }
    permissionSelection.value = (response.data.permissions || []).map((item) => item.id);
  } catch (error) {
    permissionDialogVisible.value = false;
    ElMessage.error(normalizeError(error, "roles.assignFailed"));
  }
}

async function submitPermissionAssignment() {
  if (!permissionTargetRole.value) {
    return;
  }
  permissionSubmitting.value = true;
  try {
    const response = await assignRolePermissions(
      permissionTargetRole.value.id,
      permissionSelection.value
    );
    if (response.code !== 0) {
      throw new Error(response.msg || t("roles.assignFailed"));
    }
    showWarnings(response.data);
    permissionDialogVisible.value = false;
    ElMessage.success(t("roles.assignSuccess"));
    await loadData();
  } catch (error) {
    ElMessage.error(normalizeError(error, "roles.assignFailed"));
  } finally {
    permissionSubmitting.value = false;
  }
}

async function openMenuDialog(row) {
  menuTargetRole.value = row;
  menuDialogVisible.value = true;

  try {
    const response = await fetchRoleMenus(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("roles.assignMenuFailed"));
    }
    const checkedIds = (response.data.menus || []).map((item) => item.id);
    setTimeout(() => {
      menuTreeRef.value?.setCheckedKeys(checkedIds);
    });
  } catch (error) {
    menuDialogVisible.value = false;
    ElMessage.error(normalizeError(error, "roles.assignMenuFailed"));
  }
}

async function submitMenuAssignment() {
  if (!menuTargetRole.value) {
    return;
  }
  menuSubmitting.value = true;
  try {
    const checkedKeys = menuTreeRef.value?.getCheckedKeys(false) || [];
    const halfCheckedKeys = menuTreeRef.value?.getHalfCheckedKeys() || [];
    const menuIds = [...new Set([...checkedKeys, ...halfCheckedKeys])];

    const response = await assignRoleMenus(menuTargetRole.value.id, menuIds);
    if (response.code !== 0) {
      throw new Error(response.msg || t("roles.assignMenuFailed"));
    }
    showWarnings(response.data);
    menuDialogVisible.value = false;
    ElMessage.success(t("roles.assignMenuSuccess"));
  } catch (error) {
    ElMessage.error(normalizeError(error, "roles.assignMenuFailed"));
  } finally {
    menuSubmitting.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <section class="page-shell">
    <header class="panel-head">
      <h2>{{ t("roles.title") }}</h2>
      <div class="actions">
        <el-button :loading="loading" @click="loadData">{{ t("common.reload") }}</el-button>
        <el-button type="primary" @click="openCreateDialog">{{ t("roles.newRole") }}</el-button>
      </div>
    </header>

    <el-card class="table-card">
      <div class="search-toolbar" @keyup.enter="onSearch">
        <el-form class="search-fields" :inline="true">
          <el-form-item :label="t('roles.searchRoleName')">
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
              @change="(values) => enforceMaxSearchItems('name', values)"
              @keyup.enter="onSearch"
            >
              <el-option v-for="item in roleNameCandidates" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="search-actions">
          <el-button type="primary" @click="onSearch">{{ t("common.search") }}</el-button>
          <el-button @click="onReset">{{ t("common.reset") }}</el-button>
        </div>
      </div>

      <el-table :data="items" :loading="loading" border :empty-text="t('common.noData')">
        <el-table-column prop="id" :label="t('users.id')" width="80" />
        <el-table-column prop="name" :label="t('roles.roleName')" />
        <el-table-column prop="description" :label="t('roles.description')" />
        <el-table-column prop="permission_count" :label="t('roles.permissionCount')" width="120" />
        <el-table-column :label="t('common.actions')" width="420" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" @click="openEditDialog(row)">{{ t("common.edit") }}</el-button>
              <el-button link type="warning" @click="openPermissionDialog(row)">
                {{ t("common.assign") }}
              </el-button>
              <el-button link type="success" @click="openMenuDialog(row)">
                {{ t("roles.assignMenus") }}
              </el-button>
              <el-button link type="danger" @click="removeRole(row)">{{ t("common.delete") }}</el-button>
            </el-space>
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

    <el-dialog
      v-model="roleDialogVisible"
      :title="roleMode === 'create' ? t('roles.createRole') : t('roles.editRole')"
      width="520px"
    >
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-position="top">
        <el-form-item :label="t('roles.roleName')" prop="name">
          <el-input v-model="roleForm.name" />
        </el-form-item>
        <el-form-item :label="t('roles.description')">
          <el-input v-model="roleForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRole">{{ t("common.save") }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="permissionDialogVisible"
      :title="`${t('roles.assignPermissions')} - ${permissionTargetRole?.name || ''}`"
      width="620px"
    >
      <el-select
        v-model="permissionSelection"
        multiple
        filterable
        :placeholder="t('roles.selectPermissions')"
        style="width: 100%"
      >
        <el-option
          v-for="permission in permissionOptions"
          :key="permission.id"
          :label="formatPermissionLabel(permission)"
          :value="permission.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button
          type="primary"
          :loading="permissionSubmitting"
          @click="submitPermissionAssignment"
        >
          {{ t("common.save") }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="menuDialogVisible"
      :title="`${t('roles.assignMenus')} - ${menuTargetRole?.name || ''}`"
      width="620px"
    >
      <el-tree
        ref="menuTreeRef"
        :data="menuOptions"
        node-key="id"
        show-checkbox
        default-expand-all
        :props="{ label: 'name', children: 'children' }"
      />
      <template #footer>
        <el-button @click="menuDialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button
          type="primary"
          :loading="menuSubmitting"
          @click="submitMenuAssignment"
        >
          {{ t("common.save") }}
        </el-button>
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
  background: linear-gradient(145deg, rgba(30, 64, 175, 0.12), rgba(99, 102, 241, 0.06));
  border: 1px solid rgba(59, 130, 246, 0.25);
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

