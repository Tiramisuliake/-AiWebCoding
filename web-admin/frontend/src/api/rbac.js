import http from "./http";

export async function fetchUsers(params = {}) {
  const { data } = await http.get("/users", { params });
  return data;
}

export async function createUser(payload) {
  const { data } = await http.post("/users", payload);
  return data;
}

export async function updateUser(userId, payload) {
  const { data } = await http.put(`/users/${userId}`, payload);
  return data;
}

export async function deleteUser(userId) {
  const { data } = await http.delete(`/users/${userId}`);
  return data;
}

export async function fetchUserRoles(userId) {
  const { data } = await http.get(`/users/${userId}/roles`);
  return data;
}

export async function assignUserRoles(userId, roleIds) {
  const { data } = await http.post(`/users/${userId}/roles`, { role_ids: roleIds });
  return data;
}

export async function removeUserRole(userId, roleId) {
  const { data } = await http.delete(`/users/${userId}/roles/${roleId}`);
  return data;
}

export async function fetchRoles(params = {}) {
  const { data } = await http.get("/roles", { params });
  return data;
}

export async function createRole(payload) {
  const { data } = await http.post("/roles", payload);
  return data;
}

export async function updateRole(roleId, payload) {
  const { data } = await http.put(`/roles/${roleId}`, payload);
  return data;
}

export async function deleteRole(roleId) {
  const { data } = await http.delete(`/roles/${roleId}`);
  return data;
}

export async function fetchRolePermissions(roleId) {
  const { data } = await http.get(`/roles/${roleId}/permissions`);
  return data;
}

export async function assignRolePermissions(roleId, permissionIds) {
  const { data } = await http.post(`/roles/${roleId}/permissions`, {
    permission_ids: permissionIds
  });
  return data;
}

export async function fetchRoleMenus(roleId) {
  const { data } = await http.get(`/roles/${roleId}/menus`);
  return data;
}

export async function assignRoleMenus(roleId, menuIds, permissionIds) {
  const payload = {
    menu_ids: menuIds
  };
  if (Array.isArray(permissionIds)) {
    payload.permission_ids = permissionIds;
  }
  const { data } = await http.post(`/roles/${roleId}/menus`, payload);
  return data;
}

export async function fetchPermissions(params = {}) {
  const { data } = await http.get("/permissions", { params });
  return data;
}

export async function fetchMenuTree(params = {}) {
  const { data } = await http.get("/menus", { params });
  return data;
}

export async function fetchMyMenuTree() {
  const { data } = await http.get("/menus/my-tree");
  return data;
}

export async function createMenu(payload) {
  const { data } = await http.post("/menus", payload);
  return data;
}

export async function updateMenu(menuId, payload) {
  const { data } = await http.put(`/menus/${menuId}`, payload);
  return data;
}

export async function deleteMenu(menuId) {
  const { data } = await http.delete(`/menus/${menuId}`);
  return data;
}
