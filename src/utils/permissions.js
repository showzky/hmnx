export function getUserRoles(user) {
  return Array.isArray(user?.roles) ? user.roles : [];
}

export function getRoleNames(user) {
  return getUserRoles(user)
    .map((role) => role?.name?.toLowerCase?.())
    .filter(Boolean);
}

export function getUserPermissions(user) {
  return Array.isArray(user?.permissions)
    ? user.permissions.map((permission) => String(permission).toLowerCase())
    : [];
}

export function hasPermission(user, permissionKey) {
  return getUserPermissions(user).includes(String(permissionKey || '').toLowerCase());
}

export function hasAnyPermission(user, permissionKeys = []) {
  const effectivePermissions = new Set(getUserPermissions(user));
  return permissionKeys.some((permissionKey) => effectivePermissions.has(String(permissionKey || '').toLowerCase()));
}

export function getDashboardFlavor(user) {
  return user?.dashboard_flavor || 'default';
}
