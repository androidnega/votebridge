from django.urls import path

from apps.voting.api.views import (
    BallotView,
    MyVotesView,
    SubmitBallotView,
    VerifyVoteView,
)

app_name = "voting"

urlpatterns = [
    path(
        "elections/<uuid:election_uuid>/ballot/",
        BallotView.as_view(),
        name="ballot",
    ),
    path(
        "elections/<uuid:election_uuid>/submit/",
        SubmitBallotView.as_view(),
        name="submit-ballot",
    ),
    path(
        "elections/<uuid:election_uuid>/my-votes/",
        MyVotesView.as_view(),
        name="my-votes",
    ),
    path(
        "votes/<uuid:vote_id>/verify/",
        VerifyVoteView.as_view(),
        name="verify-vote",
    ),
]
