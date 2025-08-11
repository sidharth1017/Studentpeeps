from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts_v2.models import UnVerifiedIdUpload
from django.db.models import Q
from PIL import Image
import requests
from io import BytesIO
import pytesseract
import fitz
from rapidfuzz import fuzz
import cv2
import numpy as np

class Command(BaseCommand):
    help = 'Manually verify student ID card by email and debug verification reasons'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to verify ID card')

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        try:
            user = User.objects.get(Q(email=email) | Q(username=email))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No user found with email: {email}"))
            return

        try:
            unverified_entry = UnVerifiedIdUpload.objects.get(user=user)
        except UnVerifiedIdUpload.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No UnVerifiedIdUpload entry found for user: {email}"))
            return

        full_name = f"{unverified_entry.firstname} {unverified_entry.lastname}".lower().strip()
        url = unverified_entry.collegeId.url.split('?')[0]
        self.stdout.write(f"Name: {full_name}")
        self.stdout.write(f"ID Card URL: {url}")

        response = requests.get(unverified_entry.collegeId.url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to download ID card file."))
            return

        content_type = response.headers.get('Content-Type', '')
        self.stdout.write(f"Downloaded file type: {content_type}")

        extracted_text = ""
        if 'pdf' in content_type:
            pdf_bytes = BytesIO(response.content)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                img = Image.open(BytesIO(pix.tobytes("png")))
                cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                # Pre-processing (same as image)
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                # OCR Configs
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .'
                ocr_text = pytesseract.image_to_string(gray, config=custom_config).lower().strip()

                self.stdout.write(f"OCR result from PDF page {page_num}: {ocr_text[:100]}...")
                extracted_text += " " + ocr_text  # Append with space to avoid token merging

            doc.close()
        else:
            image = Image.open(BytesIO(response.content))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .'
            extracted_text = pytesseract.image_to_string(gray, config=custom_config).lower().strip()
            self.stdout.write(f"OCR result from image: {extracted_text[:100]}...")

        # Keyword Check
        college_keywords = ['college', 'university', 'student id', 'roll no', 'institute', 'enrollment', 'admission', 'faculty', 'academic', 'department', 'course', 'semester', 'batch', 'year']

        # Split OCR text into tokens to scan (filter very small/noisy tokens)
        ocr_tokens = [word for word in extracted_text.split() if len(word) >= 5]

        is_college_id = False
        for token in ocr_tokens:
            for keyword in college_keywords:
                score = fuzz.partial_ratio(keyword, token)
                if score >= 80:
                    self.stdout.write(self.style.SUCCESS(f"Matched keyword '{keyword}' with '{token}' (Score: {score})"))
                    is_college_id = True
                    break  # Found keyword match, no need to check further
            if is_college_id:
                break  # No need to check other tokens if already matched

        if is_college_id:
            self.stdout.write(self.style.SUCCESS("College-related keywords found in ID card."))
        else:
            self.stdout.write(self.style.WARNING("No college-related keywords found in ID card."))


        # Name Matching
        name_parts = full_name.split()
        ocr_tokens = [word for word in extracted_text.split() if len(word) > 3]

        match_count = 0
        for name in name_parts:
            found_match = False
            for token in ocr_tokens:
                score = fuzz.partial_ratio(name, token)
                if score >= 70:
                    self.stdout.write(f"Matched '{name}' with '{token}' (Score: {score})")
                    match_count += 1
                    found_match = True
                    break  # Move to next name part
            if not found_match:
                self.stdout.write(f"No good match found for '{name}'")

        # Final Decision based on number of matched name parts
        if match_count >= len(name_parts) - 1:  # Allow 1 part mismatch
            self.stdout.write(self.style.SUCCESS(f"Verification Passed: {match_count}/{len(name_parts)} name parts matched."))
            # Proceed with verification success actions...
        else:
            self.stdout.write(self.style.ERROR(f"Verification Failed: Only {match_count}/{len(name_parts)} name parts matched."))
            # Proceed with verification failure actions...

        # Final Decision Logic
        if not is_college_id:
            self.stdout.write(self.style.ERROR("Verification Failed: No college/university keywords found."))

        if match_count >= len(name_parts) - 1 and is_college_id:
            self.stdout.write(self.style.SUCCESS("Verification Passed: ID card is valid and name matches."))
            # You can place actions like verifying user here
        elif is_college_id:
            self.stdout.write(self.style.WARNING("Manual Review Required: Name mismatch, but ID card seems valid."))
        else:
            self.stdout.write(self.style.ERROR("Verification Failed: ID card is not a valid college/university ID."))

