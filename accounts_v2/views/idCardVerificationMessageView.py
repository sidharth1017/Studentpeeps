from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from ..models import Register, UnVerifiedIdUpload
from PIL import Image
import pytesseract
from rapidfuzz import fuzz
import requests
from io import BytesIO
from django.db.models import Q  
import fitz 
from account.tasks import send_email
from accounts_v2.communication import send_welcome_email, send_sms_via_fast2sms
from django.template.loader import render_to_string
import cv2
import numpy as np

class IdCardVerificationMessageView(View):
    def get(self, request):
        return render(request, 'account/idCardVerificationMsg.html')

    def post(self, request):        
        email = request.session.get('email')
        phone = request.session.get('phone')
        firstname = request.session.get('fname')
        lastname = request.session.get('lname')
        full_name = f"{firstname} {lastname}".lower().strip()

        try:
            filters = Q(user__username=email) | Q(user__email=email)
            if phone:
                filters |= Q(phone=phone)
            unVerifiedRegister = UnVerifiedIdUpload.objects.get(filters)

            result = self.verify_id_card_algorithm(
                unVerifiedRegister.collegeId.url,
                firstname,
                email,
                phone,
                full_name
            )

            match_score = result["score"]
            status_msg = result["message"]

            if match_score >= 70:
                user = User.objects.get(Q(email=email) | Q(username=phone))
                user.is_active = True
                user.save()
                register = Register(user=unVerifiedRegister.user, phone=unVerifiedRegister.phone, firstname=unVerifiedRegister.firstname, lastname=unVerifiedRegister.lastname, gender=unVerifiedRegister.gender, birthday=unVerifiedRegister.birthday, collegeId=unVerifiedRegister.collegeId)
                register.is_verified = True
                register.save()
                unVerifiedRegister.delete()

                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                if (email):
                    try:
                        message = render_to_string('emailers/signup_email_body.html', {'fname': register.firstname})
                        send_welcome_email(subject=f"Welcome to Studentpeeps!", email=register.user.email, message=message)
                    except Exception as e:
                        print(f"Email sending failed: {e}")
                elif (register.phone):
                    try:
                        send_sms_via_fast2sms(phone=register.phone, name=register.firstname, messageId=194947)
                    except Exception as e:
                        print(f"SMS sending failed: {e}")

                request.session['user_id'] = register.id
                return redirect('/id-verification-message/')
            else:
                send_email(subject="Verify user with college id",
                    email=["sidharthv605@gmail.com"], message=f"Name: {firstname} <br> Email: {email} <br> Phone: {phone} <br>Id Card: {unVerifiedRegister.collegeId.url.split('?')[0]} <br> Status: {status_msg}")
                return render(request, 'account/idCardVerificationMsgFail.html', {
                    'msg': "We could not verify your student identity. We have recived your college id, our team is reviewing it will verify within 48 hours."
                })

        except Register.DoesNotExist:
            return render(request, 'account/idCardVerificationMsgFail.html', {
                'msg': "No registration found."
            })

    def verify_id_card_algorithm(self, idCardUrl, firstname, email, phone, full_name):
        response = requests.get(idCardUrl)
        if response.status_code != 200:
            print("Failed to download ID card file.")
            return None

        content_type = response.headers.get('Content-Type', '')
        extracted_text = ""
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .'

        if 'pdf' in content_type:
            pdf_bytes = BytesIO(response.content)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                img = Image.open(BytesIO(pix.tobytes("png")))
                cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                ocr_text = pytesseract.image_to_string(gray, config=custom_config).lower().strip()
                extracted_text += " " + ocr_text

            doc.close()
        else:
            image = Image.open(BytesIO(response.content))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            extracted_text = pytesseract.image_to_string(gray, config=custom_config).lower().strip()

        college_keywords = [
            'college', 'university', 'student id', 'roll no', 'institute',
            'enrollment', 'admission', 'faculty', 'academic', 'department',
            'course', 'semester', 'batch', 'year'
        ]

        ocr_tokens = [word for word in extracted_text.split() if len(word) >= 5]
        is_college_id = False
        for token in ocr_tokens:
            for keyword in college_keywords:
                score = fuzz.partial_ratio(keyword, token)
                if score >= 80:
                    is_college_id = True
                    break
            if is_college_id:
                break

        # --- Name Matching ---
        name_parts = full_name.split()
        ocr_tokens = [word for word in extracted_text.split() if len(word) > 3]

        match_count = 0
        for name in name_parts:
            found_match = False
            for token in ocr_tokens:
                score = fuzz.partial_ratio(name, token)
                if score >= 70:
                    match_count += 1
                    found_match = True
                    break
            if not found_match:
                print(f"No good match found for '{name}'")

        # --- Final Decision ---
        if match_count >= len(name_parts) - 1 and is_college_id:
            msg = "✅ Verification Passed: ID card is valid and name matches."
            print(msg)
            return {"score": 100, "message": msg}
        elif is_college_id:
            msg = "⚠ Manual Review Required: Name mismatch, but ID card seems valid."
            print(msg)
            return {"score": 60, "message": msg}
        else:
            msg = "❌ Verification Failed: ID card is not a valid college/university ID."
            print(msg)
            return {"score": 0, "message": msg}

