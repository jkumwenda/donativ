from fastapi import HTTPException
from models import Users, RolePermission, UserRole, Permission

class Security():
    def secureAccess(self, permission_code, user_id, db):
        permission = db.query(UserRole, Users, RolePermission, Permission).filter(
            Users.id == UserRole.user_id, Users.id == user_id).filter(
                UserRole.role_id == RolePermission.role_id).filter(
                    Permission.id == RolePermission.permission_id, Permission.permission_code == permission_code).first()
        if permission is None:
            raise HTTPException(
                status_code=403, detail=f"You don't have permission to access this service!")
        return permission