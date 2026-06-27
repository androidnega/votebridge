from django.db import migrations


TEMPLATES = [
    {
        "code": "otp_sms",
        "name": "OTP SMS",
        "channel": "sms",
        "sms_body": "{message}",
        "placeholders": ["message"],
    },
    {
        "code": "otp_email",
        "name": "OTP Email",
        "channel": "email",
        "subject": "VoteBridge Verification Code",
        "body_text": "{message}",
        "body_html": "<p>{message}</p>",
        "placeholders": ["message"],
    },
    {
        "code": "welcome",
        "name": "Welcome",
        "channel": "email",
        "subject": "Welcome to VoteBridge, {first_name}",
        "body_text": "Hello {first_name}, welcome to VoteBridge.",
        "body_html": "<p>Hello <strong>{first_name}</strong>, welcome to VoteBridge.</p>",
        "in_app_title": "Welcome to VoteBridge",
        "in_app_body": "Hello {first_name}, your account is ready.",
        "placeholders": ["first_name"],
    },
    {
        "code": "election_opening",
        "name": "Election Opening",
        "channel": "multi",
        "subject": "{election_name} is now open",
        "body_text": "Hello {first_name}, {election_name} is now open for voting.",
        "sms_body": "VoteBridge: {election_name} is now open. Cast your vote before polls close.",
        "in_app_title": "{election_name} is open",
        "in_app_body": "You may now cast your ballot for {election_name}.",
        "placeholders": ["first_name", "election_name", "election_uuid"],
    },
    {
        "code": "election_closing",
        "name": "Election Closing",
        "channel": "multi",
        "subject": "{election_name} has closed",
        "body_text": "Hello {first_name}, voting for {election_name} has closed.",
        "sms_body": "VoteBridge: Voting for {election_name} has closed.",
        "in_app_title": "{election_name} closed",
        "in_app_body": "Voting for {election_name} has ended.",
        "placeholders": ["first_name", "election_name"],
    },
    {
        "code": "svt_issued",
        "name": "SVT Issued",
        "channel": "multi",
        "subject": "Your voting token for {election_name}",
        "body_text": "Hello {first_name}, your Secure Voting Token for {election_name} has been generated. Token: {svt}. Expires: {expiry_time}.",
        "sms_body": "VoteBridge SVT for {election_name}: {svt}. Expires {expiry_time}.",
        "in_app_title": "Voting token issued",
        "in_app_body": "Your SVT for {election_name} expires at {expiry_time}.",
        "placeholders": ["first_name", "election_name", "svt", "expiry_time"],
    },
    {
        "code": "vote_confirmation",
        "name": "Vote Confirmation",
        "channel": "multi",
        "subject": "Vote recorded — {election_name}",
        "body_text": "Hello {first_name}, your vote for {election_name} was recorded successfully.",
        "sms_body": "VoteBridge: Your vote for {election_name} was recorded successfully.",
        "in_app_title": "Vote recorded",
        "in_app_body": "Your ballot for {election_name} was submitted successfully.",
        "placeholders": ["first_name", "election_name"],
    },
    {
        "code": "results_published",
        "name": "Results Published",
        "channel": "multi",
        "subject": "Results published — {election_name}",
        "body_text": "Hello {first_name}, certified results for {election_name} are now available.",
        "sms_body": "VoteBridge: Results for {election_name} are now published.",
        "in_app_title": "Results published",
        "in_app_body": "Certified results for {election_name} are now available.",
        "placeholders": ["first_name", "election_name", "published_at"],
    },
    {
        "code": "security_alert",
        "name": "Security Alert",
        "channel": "multi",
        "subject": "Security alert: {alert_title}",
        "body_text": "Security alert ({severity}): {alert_title}",
        "in_app_title": "Security alert",
        "in_app_body": "{alert_title} ({severity})",
        "placeholders": ["alert_title", "severity", "alert_uuid"],
    },
    {
        "code": "fraud_alert",
        "name": "Fraud Alert",
        "channel": "multi",
        "subject": "Fraud case: {case_title}",
        "body_text": "Fraud case opened ({severity}): {case_title}",
        "in_app_title": "Fraud case opened",
        "in_app_body": "{case_title} — severity {severity}",
        "placeholders": ["case_title", "severity", "case_uuid"],
    },
    {
        "code": "test_message",
        "name": "Test Message",
        "channel": "email",
        "subject": "VoteBridge Test Message",
        "body_text": "This is a test message from VoteBridge Communication Center.",
        "body_html": "<p>This is a <strong>test message</strong> from VoteBridge Communication Center.</p>",
        "placeholders": [],
    },
]


def seed_providers_and_templates(apps, schema_editor):
    Provider = apps.get_model("notifications", "CommunicationProvider")
    Template = apps.get_model("notifications", "NotificationTemplate")

    Provider.objects.get_or_create(
        provider_type="arkesel_sms",
        name="Arkesel SMS",
        defaults={"is_active": True, "is_default": True, "config": {}},
    )
    Provider.objects.get_or_create(
        provider_type="smtp_email",
        name="SMTP Email",
        defaults={"is_active": True, "is_default": True, "config": {}},
    )

    for data in TEMPLATES:
        Template.objects.update_or_create(code=data["code"], defaults=data)


def unseed(apps, schema_editor):
    Template = apps.get_model("notifications", "NotificationTemplate")
    Provider = apps.get_model("notifications", "CommunicationProvider")
    Template.objects.filter(code__in=[t["code"] for t in TEMPLATES]).delete()
    Provider.objects.filter(provider_type__in=["arkesel_sms", "smtp_email"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_providers_and_templates, unseed),
    ]
