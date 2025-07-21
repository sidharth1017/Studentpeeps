from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from ..models import Register
from PIL import Image
import pytesseract
from rapidfuzz import fuzz
import requests
from io import BytesIO
from django.db.models import Q  
import fitz 
from account.tasks import send_email
from accounts_v2.communication import send_welcome_email
from django.template.loader import render_to_string

class IdCardVerificationMessageView(View):
    def get(self, request):
        # email = request.session.get('email')
        # phone = request.session.get('phone')
        # try:
        #     register = Register.objects.get(Q(user__username=email) | Q(user__email=email) | Q(phone=phone))
        #     if register.is_verified:
        #         msg = "You're already verified!"
        #     else:
        #         msg = "Your ID has been received. Please wait while we verify."
        # except Register.DoesNotExist:
        #     msg = "No registration found."

        return render(request, 'account/idCardVerificationMsg.html')

    def post(self, request):        
        email = request.session.get('email')
        phone = request.session.get('phone')
        firstname = request.session.get('fname')
        lastname = request.session.get('lname')
        full_name = f"{firstname} {lastname}".lower().strip()

        try:
            register = Register.objects.get(Q(user__username=email) | Q(user__email=email) | Q(phone=phone))
            url = register.collegeId.url
            response = requests.get(url)

            if response.status_code != 200:
                return render(request, 'account/idCardVerificationMsgFail.html', {
                    'msg': "Failed to fetch ID file from server."
                })

            content_type = response.headers.get('Content-Type', '')
            extracted_text = ""
            if 'pdf' in content_type:
                pdf_bytes = BytesIO(response.content)
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")

                for page in doc:
                    text = page.get_text().strip()
                    if text:
                        extracted_text += text.lower()
                    else:
                        pix = page.get_pixmap()
                        img = Image.open(BytesIO(pix.tobytes("png")))
                        extracted_text += pytesseract.image_to_string(img).lower()
                doc.close()
            else:
                image = Image.open(BytesIO(response.content))
                extracted_text = pytesseract.image_to_string(image).lower().strip()

            college_keywords = ['college', 'university', 'student id', 'roll no', 'institute', 'enrollment', 'admission', 'faculty']
            is_college_id = any(keyword in extracted_text for keyword in college_keywords)
            if not is_college_id:
                send_email(subject="Verify user with college id",
                    email=["sidharthv605@gmail.com"], message=f"Name: {firstname} <br> Email: {email} <br> Phone: {phone} <br>Id Card: {url}")
                return render(request, 'account/idCardVerificationMsgFail.html', {
                    'msg': "This does not appear to be a valid college/university ID card. Please upload your official student ID. Also if you think this id is valid our team will review and update your account status in 48 hours"
                })

            match_score = fuzz.partial_ratio(full_name, extracted_text)
            if match_score >= 70:
                user = User.objects.get(Q(email=email) | Q(username=phone))
                user.is_active = True
                user.save()
                register.is_verified = True
                register.save()

                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                try:
                    message = render_to_string('emailers/signup_email_body.html', {'fname': emailname})
                    send_welcome_email(subject=f"Welcome to Studentpeeps!", email=profile.email, message=message)
                except Exception as e:
                    print(f"Email sending failed: {e}")
                    
                request.session['user_id'] = register.id
                return redirect('/id-verification-message/')
            else:
                send_email(subject="Verify user with college id",
                    email=["sidharthv605@gmail.com"], message=f"Name: {firstname} <br> Email: {email} <br> Phone: {phone} <br>Id Card: {url}")
                return render(request, 'account/idCardVerificationMsgFail.html', {
                    'msg': "We could not verify your student identity. We have recived your college id, our team is reviewing it will verify within 48 hours."
                })

        except Register.DoesNotExist:
            return render(request, 'account/idCardVerificationMsgFail.html', {
                'msg': "No registration found."
            })