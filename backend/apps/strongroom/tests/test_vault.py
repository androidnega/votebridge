from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.elections.models import Election
from apps.strongroom.models import StrongroomCommittee, VaultAccessRequest, VaultSession
from apps.strongroom.repositories.vault_repository import VaultSessionRepository
from apps.strongroom.services.vault_access_service import vault_access_service
from apps.strongroom.services.vault_committee_service import vault_committee_service
from apps.strongroom.services.vault_session_service import vault_session_service
from core.exceptions import AuthenticationError, PermissionDeniedError


class VaultGovernanceTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(
            name=Role.Name.ADMIN, defaults={"description": "Admin"}
        )
        self.super_role, _ = Role.objects.get_or_create(
            name=Role.Name.SUPER_ADMIN, defaults={"description": "Super Admin"}
        )
        self.admin = User.objects.create_user(
            email="vault-admin@test.ttu.edu.gh",
            password="VaultAdmin123!",
            role=self.admin_role,
            first_name="Vault",
            last_name="Admin",
        )
        self.super_admin = User.objects.create_user(
            email="vault-super@test.ttu.edu.gh",
            password="VaultSuper123!",
            role=self.super_role,
            first_name="Vault",
            last_name="Super",
        )
        self.custodian_one = User.objects.create_user(
            email="custodian1@test.ttu.edu.gh",
            password="Custodian1Pass!",
            role=self.super_role,
            first_name="Custodian",
            last_name="One",
        )
        self.custodian_two = User.objects.create_user(
            email="custodian2@test.ttu.edu.gh",
            password="Custodian2Pass!",
            role=self.admin_role,
            first_name="Custodian",
            last_name="Two",
        )
        now = timezone.now()
        self.election = Election.objects.create(
            title="Vault Test Election",
            status=Election.Status.SCHEDULED,
            created_by=self.admin,
            election_type=Election.ElectionType.GENERAL,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
        )

    def test_committee_configuration_and_approval(self):
        committee = vault_committee_service.configure_committee(
            self.election,
            actor=self.admin,
            member_user_uuids=[str(self.custodian_one.uuid), str(self.custodian_two.uuid)],
            session_duration_hours=2,
        )
        self.assertEqual(committee["status"], StrongroomCommittee.Status.DRAFT)

        submitted = vault_committee_service.submit_for_approval(self.election, actor=self.admin)
        self.assertEqual(submitted["status"], StrongroomCommittee.Status.PENDING_APPROVAL)

        approved = vault_committee_service.approve_committee(self.election, actor=self.super_admin)
        self.assertEqual(approved["status"], StrongroomCommittee.Status.APPROVED)

    def test_committee_locks_when_election_opens(self):
        vault_committee_service.configure_committee(
            self.election,
            actor=self.admin,
            member_user_uuids=[str(self.custodian_one.uuid), str(self.custodian_two.uuid)],
            session_duration_hours=1,
        )
        vault_committee_service.submit_for_approval(self.election, actor=self.admin)
        vault_committee_service.approve_committee(self.election, actor=self.super_admin)

        self.election.status = Election.Status.OPEN
        self.election.save()
        vault_committee_service.lock_committee_on_election_open(self.election)

        committee = vault_committee_service.get_committee(self.election)
        self.assertEqual(committee["status"], StrongroomCommittee.Status.LOCKED)

    def test_vault_session_requires_multi_custodian_auth(self):
        self.election.status = Election.Status.CLOSED
        self.election.save()
        self._approve_committee()

        access_request = vault_access_service.create_request(
            self.election,
            actor=self.super_admin,
            reason=VaultAccessRequest.Reason.INTEGRITY_VERIFICATION,
            justification="Audit review",
        )
        approved = vault_access_service.approve_request(
            vault_access_service.get_request(access_request["uuid"]),
            actor=self.super_admin,
        )
        self.assertEqual(approved["status"], VaultAccessRequest.Status.APPROVED)

        session = vault_session_service.start_session(
            vault_access_service.get_request(approved["uuid"]),
            actor=self.super_admin,
        )
        self.assertEqual(session["status"], VaultSession.Status.AWAITING_CUSTODIANS)

        session_repo = VaultSessionRepository()
        session_obj = session_repo.get_by_uuid(session["uuid"])

        with self.assertRaises(AuthenticationError):
            vault_session_service.authenticate_custodian(
                session_obj,
                identifier=self.custodian_one.email,
                password="wrong-password",
            )

        first = vault_session_service.authenticate_custodian(
            session_obj,
            identifier=self.custodian_one.email,
            password="Custodian1Pass!",
        )
        self.assertEqual(first["terminal_state"], "waiting_for_custodian_2")

        second = vault_session_service.authenticate_custodian(
            session_repo.get_by_uuid(session["uuid"]),
            identifier=self.custodian_two.email,
            password="Custodian2Pass!",
        )
        self.assertEqual(second["status"], VaultSession.Status.ACTIVE)
        self.assertEqual(second["terminal_state"], "access_granted")

    def test_access_request_blocked_before_election_complete(self):
        with self.assertRaises(PermissionDeniedError):
            vault_access_service.create_request(
                self.election,
                actor=self.super_admin,
                reason=VaultAccessRequest.Reason.INTERNAL_AUDIT,
            )

    def _approve_committee(self):
        vault_committee_service.configure_committee(
            self.election,
            actor=self.admin,
            member_user_uuids=[str(self.custodian_one.uuid), str(self.custodian_two.uuid)],
            session_duration_hours=1,
        )
        vault_committee_service.submit_for_approval(self.election, actor=self.admin)
        vault_committee_service.approve_committee(self.election, actor=self.super_admin)
        vault_committee_service.lock_committee_on_election_open(self.election)
