from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.views.generic.base import View
from django.contrib import messages
from .models import Contact, RequestBrand, Foundation, Resource, Brand, Subscribe
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.tasks import send_brand_mail, send_course_mail, send_subscribe_email, send_contact_mail
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from account.models import Payment, UnVerified
from account.tasks import send_email
from brands.models import BrandCode, BrandSearch
import json
from django.contrib.auth.models import User
from brands_v2.models import Offer, Category
import random

# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class Home(View):
    def get(self, request):
        recommended_offer_ids = ['spxdailyobjects15', 'spxnilkamal5', 'spxblissclub10', 'spxbb6', 'spxwtf25']
        recommended_offers = Offer.objects.filter(custom_id__in=recommended_offer_ids)
        offers_dict = {offer.custom_id: offer for offer in recommended_offers}
        ordered_recommended = [offers_dict[oid] for oid in recommended_offer_ids if oid in offers_dict]

        recommended_with_flags = []
        for idx, offer in enumerate(ordered_recommended):
            block_pos = idx % 10
            is_large = block_pos == 0 or block_pos == 6
            recommended_with_flags.append({
                'offer': offer,
                'is_large': is_large
            })

        all_offers = list(Offer.objects.all())
        featured_sample = random.sample(all_offers, min(15, len(all_offers)))

        featured_with_flags = []
        for idx, offer in enumerate(featured_sample):
            block_pos = idx % 10
            is_large = block_pos == 0 or block_pos == 6
            featured_with_flags.append({
                'offer': offer,
                'is_large': is_large
            })

        return render(request, 'index.html', {
            'recommended_offers': recommended_with_flags,
            'featured_offers': featured_with_flags
        })

    def post(self, request):
        body = json.loads(request.body)
        if body.get("free"):
            payment = Payment.objects.filter(user=request.user)[0]
            payment.payment_status = 1
            payment.amount = 0.0
            payment.save()
            messages.success(request, "You are now member of Studentpeeps!!")
        return JsonResponse({"message": "Done!"})
        
class OurStory(View):
    def get(self, request):
        return render(request,'ourstory.html')

class VerificationMessage(View):
    def get(self, request):        
        messages = request.session.get('institution_email')
        return render(request,'verificationmsg.html', {'msg': messages})

    def post(self, request):
        return render(request,'verificationmsg.html')

class GoogleVerifyMessage(View):
    def get(self, request):
        return render(request,'googleverifymessage.html')

    def post(self, request):
        messages = None
        Email = request.POST.get('verify')        
        unverifiedUsers = UnVerified.objects.all()
        for unverifiedUser in unverifiedUsers:
            if unverifiedUser.email == Email or unverifiedUser.institution_email == Email:
                message = render_to_string('mail_body_unverified.html', {'fname': unverifiedUser.firstname, 'lname': unverifiedUser.lastname, 'activate_url': unverifiedUser.verification_url})
                send_email(subject="Sign up karke verify na karna, is not funny!", email=[unverifiedUser.institution_email], message=message)  
                messages = "We've sent you mail on your university email verify yourself!"              
                return render(request,'googleverifymessage.html',{'messages' : messages})

        messages = "You have not signed up yet please do signup!"
        return render(request,'googleverifymessage.html',{'messages' : messages})

class UploadMessage(View):
    def get(self, request):
        return render(request,'uploadmsg.html')

class GoogleVerification(View):
    def get(self, request):
        return render(request,'verified.html')

class UnSubscribe(View):
    def get(self, request):
        return render(request,'unsubscribe.html')

class ContactUs(View):
    def get(self, request):
        messages = None
        return render(request,'contactus.html',{'message' : messages})

    def post(self, request):
        messages = None
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, message=message)
        contact.save()

        try:
            subject = f"Somebody Contacted Us"
            send_contact_mail(subject, name, email, message, ["ayush@studentpeeps.club"])
        except Exception as e:
            print(f"Email sending failed: {e}")

        messages = "Thanks for contacting us, we'll reach out you soon."
        return render(request,'contactus.html',{'message' : messages})

class Community(View):
    def get(self, request):
        return render(request,'community.html')

class FAQ(View):
    def get(self, request):
        return render(request,'faq.html')

class Privacy(View):
    def get(self, request):
        return render(request,'privacy.html')

class SubscribeView(View):
    def post(self, request):
        email = request.POST.get('subscribe_email')
        if Subscribe.objects.filter(email=email).exists():
            messages.success(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
        else:
            subscribe = Subscribe(email=email)
            subscribe.save()
            messages.success(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
            try:
                message = render_to_string('mail_body_subscribe.html')
                send_subscribe_email(subject="your community access😎", email=email, message=message)
            except Exception as e:
                print(f"Email sending failed: {e}")

        return HttpResponseRedirect('/')

class UnSubscribeView(View):
    def get(self, request):
        return render(request,'unsubscribe.html')
    def post(self, request):
        email = request.POST.get('unsubscribe_email')
        if Subscribe.objects.filter(email=email).exists():
            Subscribe.objects.filter(email=email).delete()
            messages.info(request, "You are UnSubscribed to our Newsletters!")
        else:
            messages.info(request, "You are not our Subscriber!")
        return HttpResponseRedirect('/')
        
class Error_404_View(View):
    def get(self, request):
        return render(request, '404.html')

class Favorite(View):
    def get(self, request):
        messages = None
        return render(request,'request.html',{'message' : messages})

    def post(self, request):
        messages = None
        name = request.POST.get('name')
        email = request.POST.get('email')
        brandname = request.POST.get('BrandName')
        brandsite = request.POST.get('BrandSite')
        want = request.POST.get('want')
        requestbrand = RequestBrand(name=name, email=email, brandname=brandname, brandsite=brandsite, want=want)
        requestbrand.save()
        messages = "Thanks for coming this far. We'll let you know when we speak to them."
        send_brand_mail.delay(subject="Somebody requested a brand!", name=name, email=email, brandname=brandname, brandsite=brandsite, want=want, emailList=["sidharthv1017@gmail.com","mittalayush740@gmail.com"])
        return render(request,'request.html',{'message' : messages})

class Course(View):
    def get(self, request):
        messages = None
        return render(request,'foundation.html',{'message' : messages})

    def post(self, request):
        messages = None
        name = request.POST.get('name')
        collegename = request.POST.get('collegename')
        email = request.POST.get('email')
        linkedinurl = request.POST.get('likedin')
        coursename = request.POST.get('coursename')
        courselink = request.POST.get('courselink')
        desc = request.POST.get('desc')
        foundation = Foundation(name=name, collegename=collegename, email=email, linkedinurl=linkedinurl, coursename=coursename, courselink=courselink, desc=desc)
        foundation.save()
        messages = "Thanks for filling this form."
        send_course_mail(subject="Somebody requested a course!", name=name, collegename=collegename, email=email, linkedinurl=linkedinurl, coursename=coursename, courselink=courselink, desc=desc, emailList=["sidharthv1017@gmail.com","mittalayush740@gmail.com"])
        return render(request,'foundation.html',{'message' : messages})


class Tools(View):
    def get(self, request):
        messages = None
        return render(request,'resource.html',{'message' : messages})    

    def post(self, request):
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        college = request.POST.get('college')
        resource = Resource(email=email, phone=phone, college=college)
        resource.save()
        messages = "Thanks for filling this form."
        return render(request,'resource.html',{'message' : messages})

class IdVerificationMessage(View):
    def get(self, request):        
        return render(request,'account/idCardVerification.html')


# Categories for Offers
class CategoryPageView(View):
    def get(self, request, category_id):
        categoryTitle = ""
        if category_id == "exclusive":
            offers = Offer.objects.filter(isExclusive=True).order_by('-sorting')
            categoryTitle = "Exclusive Discounts"
        elif category_id == "nonexclusive":
            offers = Offer.objects.filter(isExclusive=False).order_by('-sorting')
            categoryTitle = "Non-Exclusive Discounts"
        elif category_id == "all":
            offers = Offer.objects.filter().order_by('-sorting')
            categoryTitle = "All Discounts"
        else:
            offers = Offer.objects.filter(category__category_id=category_id).order_by('-sorting')
            category = get_object_or_404(Category, category_id=category_id)
            categoryTitle = category.title


        offers_with_flags = []

        for idx, offer in enumerate(offers):
            block_pos = idx % 10 
            is_large = block_pos == 0 or block_pos == 6
            offers_with_flags.append({
                'offer': offer,
                'is_large': is_large
            })
        context = {
            'offers': offers_with_flags,
            'heading': categoryTitle,
            'pattern_img': 'images/pattern9.png',
            'category': category
        }
        return render(request, 'pages/category_page.html', context)


