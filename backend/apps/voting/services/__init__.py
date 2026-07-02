from apps.voting.services.vote_service import BallotService, VoteAuditService, VoteService
from apps.voting.services.presence_service import pre_vote_presence_service

ballot_service = BallotService()
vote_service = VoteService()
vote_audit_service = VoteAuditService()
