from django.urls import path

from apps.candidates.api.views import GlobalCandidateViewSet

app_name = "candidates"

global_candidate_detail = GlobalCandidateViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
global_candidate_approve = GlobalCandidateViewSet.as_view({"post": "approve"})
global_candidate_reject = GlobalCandidateViewSet.as_view({"post": "reject"})

urlpatterns = [
    path("<uuid:uuid>/", global_candidate_detail, name="candidate-detail"),
    path("<uuid:uuid>/approve/", global_candidate_approve, name="candidate-approve"),
    path("<uuid:uuid>/reject/", global_candidate_reject, name="candidate-reject"),
]
