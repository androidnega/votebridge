from django.urls import path

from apps.candidates.api.views import CandidateViewSet
from apps.elections.api.views import (
    ElectionViewSet,
    PositionViewSet,
    VoterEligibilityViewSet,
    VotingChannelViewSet,
)

app_name = "elections"

election_list = ElectionViewSet.as_view({"get": "list", "post": "create"})
election_detail = ElectionViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
election_schedule = ElectionViewSet.as_view({"post": "schedule"})
election_open = ElectionViewSet.as_view({"post": "open_election"})
election_pause = ElectionViewSet.as_view({"post": "pause"})
election_close = ElectionViewSet.as_view({"post": "close"})
election_archive = ElectionViewSet.as_view({"post": "archive"})

channel_list = VotingChannelViewSet.as_view({"get": "list", "post": "create"})
channel_detail = VotingChannelViewSet.as_view(
    {
        "get": "retrieve",
        "put": "partial_update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

position_list = PositionViewSet.as_view({"get": "list", "post": "create"})
position_detail = PositionViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

eligibility_list = VoterEligibilityViewSet.as_view({"get": "list", "post": "create"})
eligibility_detail = VoterEligibilityViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
eligibility_bulk = VoterEligibilityViewSet.as_view({"post": "bulk_manage"})

election_candidate_list = CandidateViewSet.as_view({"get": "list", "post": "create"})
election_candidate_detail = CandidateViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
election_candidate_approve = CandidateViewSet.as_view({"post": "approve"})
election_candidate_reject = CandidateViewSet.as_view({"post": "reject"})

urlpatterns = [
    path("", election_list, name="election-list"),
    path("channels/", channel_list, name="channel-list"),
    path("channels/<uuid:uuid>/", channel_detail, name="channel-detail"),
    path("<uuid:uuid>/", election_detail, name="election-detail"),
    path("<uuid:uuid>/schedule/", election_schedule, name="election-schedule"),
    path("<uuid:uuid>/open/", election_open, name="election-open"),
    path("<uuid:uuid>/pause/", election_pause, name="election-pause"),
    path("<uuid:uuid>/close/", election_close, name="election-close"),
    path("<uuid:uuid>/archive/", election_archive, name="election-archive"),
    path(
        "<uuid:election_uuid>/positions/",
        position_list,
        name="election-position-list",
    ),
    path(
        "<uuid:election_uuid>/positions/<uuid:uuid>/",
        position_detail,
        name="election-position-detail",
    ),
    path(
        "<uuid:election_uuid>/eligibility/",
        eligibility_list,
        name="election-eligibility-list",
    ),
    path(
        "<uuid:election_uuid>/eligibility/bulk/",
        eligibility_bulk,
        name="election-eligibility-bulk",
    ),
    path(
        "<uuid:election_uuid>/eligibility/<uuid:uuid>/",
        eligibility_detail,
        name="election-eligibility-detail",
    ),
    path(
        "<uuid:election_uuid>/candidates/",
        election_candidate_list,
        name="election-candidate-list",
    ),
    path(
        "<uuid:election_uuid>/candidates/<uuid:uuid>/",
        election_candidate_detail,
        name="election-candidate-detail",
    ),
    path(
        "<uuid:election_uuid>/candidates/<uuid:uuid>/approve/",
        election_candidate_approve,
        name="election-candidate-approve",
    ),
    path(
        "<uuid:election_uuid>/candidates/<uuid:uuid>/reject/",
        election_candidate_reject,
        name="election-candidate-reject",
    ),
]
