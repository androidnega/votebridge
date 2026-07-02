from apps.accounts.permissions import IsAdminOrSuperAdmin, IsSuperAdmin

CanAccessPlatformOperationsCenter = IsSuperAdmin
CanAccessElectionOperations = IsAdminOrSuperAdmin

# Backwards-compatible alias for platform-wide operations endpoints.
CanAccessOperationsCenter = CanAccessPlatformOperationsCenter
