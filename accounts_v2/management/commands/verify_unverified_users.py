from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.loader import render_to_string

from accounts_v2.models import Register, UnVerifiedIdUpload
from accounts_v2.views import idCardVerificationMessageView
from accounts_v2.communication import send_welcome_email, send_sms_via_fast2sms

import os
from datetime import datetime


class Command(BaseCommand):
    help = "Re-run ID card verification algorithm on all unverified users."

    def handle(self, *args, **kwargs):
        verifier = idCardVerificationMessageView.IdCardVerificationMessageView()
        unverified_users = UnVerifiedIdUpload.objects.all()

        # Create log file
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(
            log_dir,
            f"id_verification_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(log_file, "w", encoding="utf-8") as log:
            log.write("===== ID Verification Batch Run =====\n\n")

            for unverified in unverified_users:
                email = unverified.user.email or unverified.user.username
                phone = getattr(unverified, "phone", None)
                firstname = getattr(unverified, "firstname", "")
                lastname = getattr(unverified, "lastname", "")
                full_name = f"{firstname} {lastname}".lower().strip()

                log.write(f"\n--- Processing User: {unverified.user.username} ({email}/{phone}) ---\n")

                try:
                    result = verifier.verify_id_card_algorithm(
                        unverified.collegeId.url,
                        firstname,
                        email,
                        phone,
                        full_name
                    )

                    if not result:
                        log.write("❌ Error: Could not extract ID card text\n")
                        continue

                    match_score = result["score"]
                    status_msg = result["message"]
                    log.write(f"Algorithm Result → Score: {match_score}, Message: {status_msg}\n")

                    if match_score >= 70:
                        # Activate Django user
                        user = User.objects.get(Q(email=email) | Q(username=phone))
                        user.is_active = True
                        user.save()

                        # Create new Register record
                        register = Register(
                            user=unverified.user,
                            phone=unverified.phone,
                            firstname=unverified.firstname,
                            lastname=unverified.lastname,
                            gender=unverified.gender,
                            birthday=unverified.birthday,
                            collegeId=unverified.collegeId,
                            is_verified=True
                        )
                        register.save()

                        # Remove unverified entry
                        unverified.delete()

                        # Send welcome message
                        notification_status = ""
                        try:
                            if phone:
                                res = send_sms_via_fast2sms(
                                    phone=phone,
                                    name=register.firstname,
                                    messageId=194947
                                )
                                notification_status = f"📱 SMS sent to {phone} | Response: {res}"
                            elif email:
                                message = render_to_string(
                                    'emailers/signup_email_body.html',
                                    {'fname': register.firstname}
                                )
                                send_welcome_email(
                                    subject="Welcome to Studentpeeps!",
                                    email=user.email,
                                    message=message
                                )
                                notification_status = f"📧 Welcome email sent to {user.email}"
                        except Exception as e:
                            notification_status = f"⚠ Notification failed: {e}"

                        log.write(f"✅ User Verified → User {user.id} activated, Register created.\n")
                        log.write(notification_status + "\n")

                    else:
                        # Just log failure
                        log.write(f"⚠ Verification Failed → {status_msg}\n")
                        log.write(f"ID Card URL: {unverified.collegeId.url.split('?')[0]}\n")

                except Exception as e:
                    log.write(f"❌ Exception: {e}\n")

            log.write("\n===== Verification Run Completed =====\n")

        self.stdout.write(self.style.SUCCESS(f"Verification completed. Log saved at {log_file}"))
