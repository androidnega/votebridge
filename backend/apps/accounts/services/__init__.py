from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.mfa_service import MFAService
from apps.accounts.services.otp_service import OTPService
from apps.accounts.services.role_service import RoleService
from apps.accounts.services.session_service import SessionService
from apps.accounts.services.user_service import UserService

auth_service = AuthService()
mfa_service = MFAService()
otp_service = OTPService()
session_service = SessionService()
user_service = UserService()
role_service = RoleService()
