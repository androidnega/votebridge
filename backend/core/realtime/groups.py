"""Redis channel layer group names for real-time events."""


def dashboard_admin() -> str:
    return "realtime.dashboard.admin"


def dashboard_student(user_uuid) -> str:
    return f"realtime.dashboard.student.{user_uuid}"


def election(election_uuid) -> str:
    return f"realtime.election.{election_uuid}"


def security() -> str:
    return "realtime.security"


def fraud() -> str:
    return "realtime.fraud"


def results() -> str:
    return "realtime.results"


def strongroom() -> str:
    return "realtime.strongroom"


def communications() -> str:
    return "realtime.communications"


def user_notifications(user_uuid) -> str:
    return f"realtime.notifications.{user_uuid}"


def ussd() -> str:
    return "realtime.ussd"


def operations() -> str:
    return "realtime.operations"


def analytics() -> str:
    return "realtime.analytics"
