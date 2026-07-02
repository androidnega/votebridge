"""
Seed development users for all VoteBridge roles.

Run: python manage.py seed_demo_users

DEV ONLY — passwords below must never be used in production.
"""

from django.core.management.base import BaseCommand

from apps.accounts.models import Role, User
from apps.system.dev_credentials import require_dev_bootstrap_password

DEMO_USERS = [
    {
        "role": Role.Name.SUPER_ADMIN,
        "email": "superadmin@ttu.edu.gh",
        "username": "superadmin",
        "first_name": "Akua",
        "last_name": "Mensah",
        "is_verified": True,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "role": Role.Name.ADMIN,
        "email": "admin@ttu.edu.gh",
        "username": "admin",
        "first_name": "Kofi",
        "last_name": "Asante",
        "is_verified": True,
        "is_staff": True,
    },
    {
        "role": Role.Name.ADMIN,
        "email": "registrar@ttu.edu.gh",
        "username": "registrar",
        "first_name": "Abena",
        "last_name": "Owusu",
        "is_verified": True,
        "is_staff": True,
    },
    {
        "role": Role.Name.ADMIN,
        "email": "electionofficer@ttu.edu.gh",
        "username": "electionofficer",
        "first_name": "Yaw",
        "last_name": "Mensah",
        "is_verified": True,
        "is_staff": True,
    },
    {
        "role": Role.Name.STUDENT,
        "email": "kwame.mensah@ttu.edu.gh",
        "username": "kwame.mensah",
        "first_name": "Kwame",
        "last_name": "Mensah",
        "index_number": "BC/ITS/24/047",
        "student_id": "BC/ITS/24/047",
        "is_verified": True,
    },
    {
        "role": Role.Name.STUDENT,
        "email": "ama.osei@ttu.edu.gh",
        "username": "ama.osei",
        "first_name": "Ama",
        "last_name": "Osei",
        "index_number": "BC/ITD/24/031",
        "student_id": "BC/ITD/24/031",
        "is_verified": True,
    },
    {
        "role": Role.Name.CANDIDATE,
        "email": "kofi.boateng@ttu.edu.gh",
        "username": "kofi.boateng",
        "first_name": "Kofi",
        "last_name": "Boateng",
        "index_number": "BC/ITN/24/112",
        "student_id": "BC/ITN/24/112",
        "is_verified": True,
    },
]


class Command(BaseCommand):
    help = "Create demo users for all roles (development only)."

    def handle(self, *args, **options):
        created = updated = 0
        demo_password = require_dev_bootstrap_password()

        for spec in DEMO_USERS:
            role = Role.objects.filter(name=spec["role"]).first()
            if not role:
                self.stdout.write(self.style.ERROR(f"Role '{spec['role']}' not found. Run migrations first."))
                return

            user, was_created = User.objects.update_or_create(
                email=spec["email"],
                defaults={
                    "role": role,
                    "username": spec.get("username", spec["email"]),
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "index_number": spec.get("index_number", ""),
                    "student_id": spec.get("student_id", ""),
                    "phone_number": spec.get("phone_number", ""),
                    "is_verified": spec.get("is_verified", True),
                    "is_staff": spec.get("is_staff", False),
                    "is_superuser": spec.get("is_superuser", False),
                    "is_active": True,
                },
            )
            user.set_password(demo_password)
            user.save()
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Demo users ready ({created} created, {updated} updated)."))
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("DEV PASSWORD (all accounts): DEV_BOOTSTRAP_PASSWORD in your local .env"))
        self.stdout.write("")
        self.stdout.write("Universal login at http://localhost:5173/auth/login")
        self.stdout.write("")
        self.stdout.write("Identity examples (no role selection):")
        self.stdout.write("  superadmin / superadmin@ttu.edu.gh")
        self.stdout.write("  admin / admin@ttu.edu.gh")
        self.stdout.write("  registrar / registrar@ttu.edu.gh")
        self.stdout.write("  electionofficer / electionofficer@ttu.edu.gh")
        self.stdout.write("  BC/ITS/24/047  (student)")
        self.stdout.write("  BC/ITD/24/031  (student)")
        self.stdout.write("  BC/ITN/24/112  (candidate)")
        self.stdout.write("")
        self.stdout.write("OTP: After login, check the backend terminal for the 6-digit code (console email).")
