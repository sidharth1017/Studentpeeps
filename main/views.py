from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic.base import View
from django.contrib import messages
from .models import Contact, RequestBrand, Foundation, Resource, Brand, Subscribe
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.tasks import send_brand_mail, send_course_mail, send_subscribe_email
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from account.models import Payment, UnVerified
from account.tasks import send_email
from brands.models import BrandCode, BrandSearch
import json
from django.contrib.auth.models import User

# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class Home(View):
    def get(self, request):
        brandsearch = BrandSearch.objects.all()
        return render(request,'index.html', {'brandsearch': brandsearch})
    
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
                send_email(subject="Sign up karke verify na karna, is not funny!", email=unverifiedUser.institution_email, message=message)  
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


class Exclusive(View):
    def get(self, request):
        return render(request,'exclusive.html')

class NonExclusive(View):
    def get(self, request):
        return render(request,'nonexclusive.html')

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
        messages = "Thanks for contacting us, we'll reach out you soon."
        return render(request,'contactus.html',{'message' : messages})

class Community(View):
    def get(self, request):
        return render(request,'community.html')

class All(View):
    def get(self, request):
        return render(request,'all.html')

class Tech(View):
    def get(self, request):
        return render(request,'tech.html')

# class Entertainment(View):
#     def get(self, request):
#         return render(request,'entertainment.html')

class FoodsAndDrinks(View):
    def get(self, request):
        return render(request,'foodsanddrinks.html')

class Travel(View):
    def get(self, request):
        return render(request,'travel.html')

class HealthAndBeauty(View):
    def get(self, request):
        return render(request,'healthandbeauty.html')

class Edtech(View):
    def get(self, request):
        return render(request,'edtech.html')

class BooksAndStationary(View):
    def get(self, request):
        return render(request,'booksandstationary.html')

class HomeAndUtilities(View):
    def get(self, request):
        return render(request,'homeandutilities.html')

class Fashion(View):
    def get(self, request):
        return render(request,'fashion.html')

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
            messages.info(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
        else:
            subscribe = Subscribe(email=email)
            subscribe.save()
            messages.info(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
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

class Indigo(View):
    def get(self, request):
        return render(request,'indigo.html')

class Microsoft(View):
    def get(self, request):
        return render(request,'microsoft.html')
        
class Spotify(View):
    def get(self, request):
        return render(request,'spotify.html')

class Notion(View):
    def get(self, request):
        return render(request,'notion.html')

class Github(View):
    def get(self, request):
        return render(request,'github.html')
        
class Samsung(View):
    def get(self, request):
        return render(request,'samsung.html')

class Adobe(View):
    def get(self, request):
        return render(request,'adobe.html')

class Apple(View):
    def get(self, request):
        return render(request,'apple.html')
        
class AppleMusic(View):
    def get(self, request):
        return render(request,'applemusic.html')

class Wix(View):
    def get(self, request):
        return render(request,'wix.html')
class OnePlus(View):
    def get(self, request):
        return render(request,'oneplus.html')
class YTPremium(View):
    def get(self, request):
        return render(request,'ytpremium.html')
class AmazonPrime(View):
    def get(self, request):
        return render(request,'amazonprime.html')
class GoFirst(View):
    def get(self, request):
        return render(request,'gofirst.html')
class SpiceJet(View):
    def get(self, request):
        return render(request,'spicejet.html')
class EaseMyTrip(View):
    def get(self, request):
        return render(request,'easemytrip.html')
class Vistara(View):
    def get(self, request):
        return render(request,'vistara.html')
class Lufthansa(View):
    def get(self, request):
        return render(request,'lufthansa.html')



class WTF(View):
    def get(self, request):
        return render(request,'wtf.html')

class CodeWTF(View):
    def get(self, request):
        return render(request,'codeWtf.html')
        

class Avni(View):
    def get(self, request):
        return render(request,'avni.html')

class CodeAvni(View):
    def get(self, request):
        avniBrand = Brand.objects.get(name="Avni")
        avniBrand.count += 1
        avniBrand.save()
        return render(request,'codeAvni.html')
        

class Peesafe(View):
    def get(self, request):
        return render(request,'PEESAFE.html')    

class CodePeesafe(View):
    def get(self, request):
        peesafeBrand = Brand.objects.get(name="Peesafe")
        peesafeBrand.count += 1
        peesafeBrand.save()
        return render(request,'codePEESAFE.html')
        

class Naagin(View):
    def get(self, request):
        return render(request,'Naagin.html')

class CodeNaagin(View):
    def get(self, request):
        naaginBrand = Brand.objects.get(name="Naagin")
        naaginBrand.count += 1
        naaginBrand.save()
        return render(request,'codeNaagin.html')
        

class TBH(View):
    def get(self, request):
        return render(request,'TBH.html')

class CodeTBH(View):
    def get(self, request):
        TBHBrand = Brand.objects.get(name="ToBeHonestFoods")
        TBHBrand.count += 1
        TBHBrand.save()
        return render(request,'codeTBH.html')


class PropShop(View):
    def get(self, request):
        return render(request,'propshop.html')

class CodePropShop(View):
    def get(self, request):
        propShopBrand = Brand.objects.get(name="PropShop24")
        propShopBrand.count += 1
        propShopBrand.save()
        return render(request,'codePropshop.html')

class Bitclass(View):
    def get(self, request):
        return render(request,'bitclass.html')

class CodeBitclass(View):
    def get(self, request):
        bitClassBrand = Brand.objects.get(name="BitClass")
        bitClassBrand.count += 1
        bitClassBrand.save()
        return render(request,'codebitclass.html')

class SattViko(View):
    def get(self, request):
        return render(request,'sattviko.html')

class CodeSattViko(View):
    def get(self, request):
        sattVikoBrand = Brand.objects.get(name="SattViko")
        sattVikoBrand.count += 1
        sattVikoBrand.save()
        return render(request,'codesattviko.html')


class Rapido(View):
    def get(self, request):
        return render(request,'rapido.html')

class CodeRapido(View):
    def get(self, request):
        rapidoBrand = Brand.objects.get(name="Rapido")
        rapidoBrand.count += 1
        rapidoBrand.save()
        return render(request,'coderapido.html')
        

class TWC(View):
    def get(self, request):
        return render(request,'TWC.html')

class CodeTWC(View):
    def get(self, request):
        TWCBrand = Brand.objects.get(name="TheWomensCompany")
        TWCBrand.count += 1
        TWCBrand.save()
        return render(request,'codeTWC.html')


class Ptal(View):
    def get(self, request):
        return render(request,'ptal.html')

class CodePtal(View):
    def get(self, request):
        ptalBrand = Brand.objects.get(name="PTAL")
        ptalBrand.count += 1
        ptalBrand.save()
        return render(request,'codeptal.html')
        

class Bookchor(View):
    def get(self, request):
        return render(request,'bookchor.html')

class CodeBookchor(View):
    def get(self, request):
        bookchorBrand = Brand.objects.get(name="BookChor")
        bookchorBrand.count += 1
        bookchorBrand.save()

        brand = BrandCode.objects.get(brandname="Bookchor")
        codes = brand.codes
        code = codes[0]
        del codes[0]
        
        BrandCode.objects.filter(brandname="Bookchor").delete()
        brandcode = BrandCode(brandname="Bookchor", codes=codes)
        brandcode.save() 

        return render(request,'codebookchor.html', {'code': code})


class Bewakoof(View):
    def get(self, request):
        return render(request,'bewakoof.html')

class CodeBewakoof(View):
    def get(self, request):
        bewakoofBrand = Brand.objects.get(name="Bewakoof")
        bewakoofBrand.count += 1
        bewakoofBrand.save()
        return render(request,'codebewakoof.html')
            

class Inchpaper(View):
    def get(self, request):
        return render(request,'inchpaper.html')

class CodeInchpaper(View):
    def get(self, request):
        inchpaperBrand = Brand.objects.get(name="Inchpaper")
        inchpaperBrand.count += 1
        inchpaperBrand.save()
        return render(request,'codeinchpaper.html')
        

class Udemy(View):
    def get(self, request):
        return render(request,'udemy.html')

class CodeUdemy(View):
    def get(self, request):
        udemyBrand = Brand.objects.get(name="Udemy")
        udemyBrand.count += 1
        udemyBrand.save()

        brand = BrandCode.objects.get(brandname="Udemy")
        codes = brand.codes
        code = codes[0]
        del codes[0]
        
        BrandCode.objects.filter(brandname="Udemy").delete()
        brandcode = BrandCode(brandname="Udemy", codes=codes)
        brandcode.save() 

        return render(request,'codeudemy.html', {'code': code})


class RageCoffee(View):
    def get(self, request):
        return render(request,'ragecoffee.html')

class CodeRageCoffee(View):
    def get(self, request):
        RagecoffeeBrand = Brand.objects.get(name="Ragecoffee")
        RagecoffeeBrand.count += 1
        RagecoffeeBrand.save()
        return render(request,'coderagecoffee.html')


class Myntra(View):
    def get(self, request):
        return render(request,'myntra.html')

class CodeMyntra(View):
    def get(self, request):
        MyntraBrand = Brand.objects.get(name="Myntra")
        MyntraBrand.count += 1
        MyntraBrand.save()

        brand = BrandCode.objects.get(brandname="Myntra")
        codes = brand.codes
        code = codes[0]
        del codes[0]
        
        BrandCode.objects.filter(brandname="Myntra").delete()
        brandcode = BrandCode(brandname="Myntra", codes=codes)
        brandcode.save()  
        return render(request,'codemyntra.html', {'code': code})
         

class Beardo(View):
    def get(self, request):
        return render(request,'beardo.html')

class CodeBeardo(View):
    def get(self, request):
        BeardoBrand = Brand.objects.get(name="Beardo")
        BeardoBrand.count += 1
        BeardoBrand.save()

        brand100 = BrandCode.objects.get(brandname="Beardo 100")
        codes100 = brand100.codes
        code100 = codes100[0]
        del codes100[0]
        
        BrandCode.objects.filter(brandname="Beardo 100").delete()
        brandcode100 = BrandCode(brandname="Beardo 100", codes=codes100)
        brandcode100.save()  

        brand500 = BrandCode.objects.get(brandname="Beardo 500")
        codes500 = brand500.codes
        code500 = codes500[0]
        del codes500[0]
        
        BrandCode.objects.filter(brandname="Beardo 500").delete()
        brandcode500 = BrandCode(brandname="Beardo 500", codes=codes500)
        brandcode500.save()  

        return render(request,'codebeardo.html', {'code100': code100, 'code500': code500})
        

class Nestaway(View):
    def get(self, request):
        return render(request,'nestaway.html')
            
        
class PharmEasy(View):
    def get(self, request):
        return render(request,'pharmeasy.html')


class CodePharmEasy(View):
    def get(self, request):
        PharmEasyBrand = Brand.objects.get(name="Pharmeasy")
        PharmEasyBrand.count += 1
        PharmEasyBrand.save()
        return render(request,'codepharmeasy.html')


# def paymentuser(request):
#     for user in User.objects.all():
#         payment = Payment(user=user, payment_status=1, amount=0.0)
#         payment.save()
#     return HttpResponse("Done")
    
