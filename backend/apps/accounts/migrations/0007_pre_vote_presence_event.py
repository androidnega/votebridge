# Generated manually for pre-vote presence audit event

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_mfalog_event_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mfalog",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("login_success", "Login Success"),
                    ("login_failed", "Login Failed"),
                    ("otp_sent", "OTP Sent"),
                    ("otp_verified", "OTP Verified"),
                    ("otp_failed", "OTP Failed"),
                    ("mfa_required", "MFA Required"),
                    ("mfa_completed", "MFA Completed"),
                    ("logout", "Logout"),
                    ("session_revoked", "Session Revoked"),
                    ("token_refresh", "Token Refresh"),
                    ("ballot_viewed", "Ballot Viewed"),
                    ("vote_cast", "Vote Cast"),
                    ("vote_verified", "Vote Verified"),
                    ("vote_confirmation_viewed", "Vote Confirmation Viewed"),
                    ("svt_issued", "SVT Issued"),
                    ("svt_validated", "SVT Validated"),
                    ("ballot_started", "Ballot Started"),
                    ("ballot_submitted", "Ballot Submitted"),
                    ("svt_consumed", "SVT Consumed"),
                    ("svt_revoked", "SVT Revoked"),
                    ("svt_reissued", "SVT Reissued"),
                    ("svt_vote_verified", "SVT Vote Verified"),
                    ("pre_vote_presence_captured", "Pre-Vote Presence Captured"),
                    ("bio_enrollment", "Biometric Enrollment"),
                    ("bio_verify_pass", "Biometric Verification Passed"),
                    ("bio_verify_fail", "Biometric Verification Failed"),
                    ("bio_challenge_fail", "Biometric Challenge Failed"),
                    ("bio_spoof_attempt", "Biometric Spoof Attempt"),
                    ("bio_account_locked", "Biometric Account Locked"),
                    ("bio_strongroom", "Biometric Strongroom Verification"),
                    ("bio_step_up", "Biometric Step-Up"),
                    ("device_registered", "Device Registered"),
                    ("device_revoked", "Device Revoked"),
                    ("device_expired", "Device Expired"),
                    ("trusted_login", "Trusted Login"),
                    ("high_risk_login", "High Risk Login"),
                    ("new_country_login", "New Country Login"),
                    ("biometric_triggered", "Biometric Triggered"),
                    ("trust_level_changed", "Trust Level Changed"),
                    ("risk_score_changed", "Risk Score Changed"),
                    ("impossible_travel", "Impossible Travel"),
                    ("device_renewed", "Device Renewed"),
                    ("university_device_assigned", "University Device Assigned"),
                    ("device_renamed", "Device Renamed"),
                ],
                db_index=True,
                max_length=30,
            ),
        ),
    ]
