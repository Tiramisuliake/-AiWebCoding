<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { useI18n } from "../composables/useI18n";
import {
  assignUserRoles,
  createUser,
  deleteUser,
  fetchRoles,
  fetchUserRoles,
  fetchUsers,
  removeUserRole,
  updateUser
} from "../api/rbac";

const { t } = useI18n();
const loading = ref(false);
const submitting = ref(false);
const items = ref([]);
const roleOptions = ref([]);
const total = ref(0);

const userDialogVisible = ref(false);
const userFormRef = ref();
const userMode = ref("create");
const userForm = reactive({
  id: null,
  username: "",
  email: "",
  password: "",
  is_active: true
});

const roleDialogVisible = ref(false);
const roleSubmitting = ref(false);
const roleTargetUser = ref(null);
const roleSelection = ref([]);
const originalRoleIds = ref([]);

const userRules = {
  username: [{ required: true, message: t("users.usernameRequired"), trigger: "blur" }],
  email: [{ required: true, message: t("users.emailRequired"), trigger: "blur" }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (userMode.value === "create" && (!value || value.length < 8)) {
          callback(new Error(t("users.passwordMin")));
          return;
        }
        if (value && value.length < 8) {
          callback(new Error(t("users.passwordMin")));
          return;
        }
        callback();
      },
      trigger: "blur"
    }
  ]
};

function normalizeError(error, fallbackKey) {
  return error.response?.data?.msg || error.message || t(fallbackKey);
}

async function loadData() {
  loading.value = true;
  try {
    const [userResponse, roleResponse] = await Promise.all([
      fetchUsers({ page: 1, per_page: 100 }),
      fetchRoles({ page: 1, per_page: 100 })
    ]);

    if (userResponse.code !== 0) {
      throw new Error(userResponse.msg || t("users.loadFailed"));
    }
    if (roleResponse.code !== 0) {
      throw new Error(roleResponse.msg || t("roles.loadFailed"));
    }

    items.value = userResponse.data.items || [];
    total.value = userResponse.data.total || 0;
    roleOptions.value = roleResponse.data.items || [];
  } catch (error) {
    ElMessage.error(normalizeError(error, "users.loadFailed"));
  } finally {
    loading.value = false;
  }
}

function resetUserForm() {
  userForm.id = null;
  userForm.username = "";
  userForm.email = "";
  userForm.password = "";
  userForm.is_active = true;
}

function openCreateDialog() {
  userMode.value = "create";
  resetUserForm();
  userDialogVisible.value = true;
}

function openEditDialog(row) {
  userMode.value = "edit";
  userForm.id = row.id;
  userForm.username = row.username;
  userForm.email = row.email;
  userForm.password = "";
  userForm.is_active = row.is_active;
  userDialogVisible.value = true;
}

async function submitUser() {
  await userFormRef.value.validate();
  submitting.value = true;
  try {
    if (userMode.value === "create") {
      const response = await createUser({
        username: userForm.username,
        email: userForm.email,
        password: userForm.password,
        is_active: userForm.is_active
      });
      if (response.code !== 0) {
        throw new Error(response.msg || t("users.submitFailed"));
      }
      ElMessage.success(t("users.createSuccess"));
    } else {
      const payload = {
        email: userForm.email,
        is_active: userForm.is_active
      };
      if (userForm.password) {
        payload.password = userForm.password;
      }
      const response = await updateUser(userForm.id, payload);
      if (response.code !== 0) {
        throw new Error(response.msg || t("users.submitFailed"));
      }
      ElMessage.success(t("users.updateSuccess"));
    }

    userDialogVisible.value = false;
    await loadData();
  } catch (error) {
    ElMessage.error(normalizeError(error, "users.submitFailed"));
  } finally {
    submitting.value = false;
  }
}

async function removeUser(row) {
  try {
    await ElMessageBox.confirm(
      t("users.confirmDelete", { name: row.username }),
      t("common.confirm"),
      { type: "warning" }
    );
    const response = await deleteUser(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("users.deleteFailed"));
    }
    ElMessage.success(t("users.deleteSuccess"));
    await loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(normalizeError(error, "users.deleteFailed"));
    }
  }
}

async function openRoleDialog(row) {
  roleTargetUser.value = row;
  roleSelection.value = [];
  originalRoleIds.value = [];
  roleDialogVisible.value = true;

  try {
    const response = await fetchUserRoles(row.id);
    if (response.code !== 0) {
      throw new Error(response.msg || t("users.loadFailed"));
    }
    const roleIds = (response.data.roles || []).map((item) => item.id);
    roleSelection.value = [...roleIds];
    originalRoleIds.value = [...roleIds];
  } catch (error) {
    roleDialogVisible.value = false;
    ElMessage.error(normalizeError(error, "users.loadFailed"));
  }
}

async function submitRoleAssignment() {
  if (!roleTargetUser.value) {
    return;
  }
  roleSubmitting.value = true;
  try {
    const userId = roleTargetUser.value.id;
    const current = new Set(originalRoleIds.value);
    const target = new Set(roleSelection.value);

    const toAdd = [...target].filter((roleId) => !current.has(roleId));
    const toRemove = [...current].filter((roleId) => !target.has(roleId));

    if (toAdd.length) {
      const addResponse = await assignUserRoles(userId, toAdd);
      if (addResponse.code !== 0) {
        throw new Error(addResponse.msg || t("users.submitFailed"));
      }
    }

    for (const roleId of toRemove) {
      const removeResponse = await removeUserRole(userId, roleId);
      if (removeResponse.code !== 0) {
        throw new Error(removeResponse.msg || t("users.submitFailed"));
      }
    }

    roleDialogVisible.value = false;
    ElMessage.success(t("users.roleUpdateSuccess"));
    await loadData();
  } catch (error) {
    ElMessage.error(normalizeError(error, "users.submitFailed"));
  } finally {
    roleSubmitting.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <section class="page-shell">
    <header class="panel-head">
      <h2>{{ t("users.title") }}</h2>
      <div class="actions">
        <el-button :loading="loading" @click="loadData">{{ t("common.reload") }}</el-button>
        <el-button type="primary" @click="openCreateDialog">{{ t("users.newUser") }}</el-button>
      </div>
    </header>

    <el-card class="table-card">
      <el-table :data="items" :loading="loading" border>
        <el-table-column prop="id" :label="t('users.id')" width="80" />
        <el-table-column prop="username" :label="t('users.username')" />
        <el-table-column prop="email" :label="t('users.email')" />
        <el-table-column :label="t('users.active')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? t("common.yes") : t("common.no") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="roles" :label="t('users.roles')">
          <template #default="{ row }">
            {{ row.roles?.join(", ") || "-" }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="320" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" @click="openEditDialog(row)">{{ t("common.edit") }}</el-button>
              <el-button link type="warning" @click="openRoleDialog(row)">{{ t("common.assign") }}</el-button>
              <el-button link type="danger" @click="removeUser(row)">{{ t("common.delete") }}</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      <div class="foot">{{ t("common.total") }}: {{ total }}</div>
    </el-card>

    <el-dialog
      v-model="userDialogVisible"
      :title="userMode === 'create' ? t('users.createUser') : t('users.editUser')"
      width="520px"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-position="top">
        <el-form-item :label="t('users.username')" prop="username">
          <el-input v-model="userForm.username" :disabled="userMode === 'edit'" />
        </el-form-item>
        <el-form-item :label="t('users.email')" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item :label="t('users.password')" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            show-password
            :placeholder="userMode === 'edit' ? t('users.keepPassword') : ''"
          />
        </el-form-item>
        <el-form-item :label="t('users.active')">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitUser">{{ t("common.save") }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="roleDialogVisible"
      :title="`${t('users.assignRoles')} - ${roleTargetUser?.username || ''}`"
      width="520px"
    >
      <el-select
        v-model="roleSelection"
        multiple
        filterable
        :placeholder="t('users.selectRoles')"
        style="width: 100%"
      >
        <el-option
          v-for="role in roleOptions"
          :key="role.id"
          :label="role.name"
          :value="role.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="roleDialogVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button type="primary" :loading="roleSubmitting" @click="submitRoleAssignment">
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
  background: linear-gradient(145deg, rgba(37, 99, 235, 0.12), rgba(30, 64, 175, 0.06));
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

.foot {
  margin-top: var(--space-2);
  color: var(--color-text-secondary);
}

@media (max-width: 900px) {
  .panel-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
