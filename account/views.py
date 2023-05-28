import django
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from .serializers import *
import pandas as pd 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import uuid 
import razorpay
from django.views.decorators.csrf import csrf_exempt
from decouple import config

razorpay_client = razorpay.Client(auth=(config("RAZORPAY_KEY_ID"), config("RAZORPAY_KEY_SECRET")))

# Create your views here
def Register(request):
    register_objs = Registers.objects.all()
    serializer = RegistersSerializer(register_objs, many=True)
    df = pd.DataFrame(serializer.data)
    df.to_csv(f"/var/www/studentpeeps/media/data{uuid.uuid4()}.csv", encoding="UTF-8", index=False)
    return HttpResponse("Data Printed")


def Uploads(request):
    Uploads_objs = Upload.objects.all()
    serializer = UploadsSerializer(Uploads_objs, many=True)
    df = pd.DataFrame(serializer.data)
    df.to_csv(f"/var/www/studentpeeps/media/data{uuid.uuid4()}.csv", encoding="UTF-8", index=False)
    return HttpResponse("Data Printed")


def error_404_view(request, exception):
     return render(request, '404.html')


def SignUpView(request):
    return render(request, 'signupview.html', {'Institution': Institution})


# def CouponCode(request):
#     if request.method == "POST":
#         return JsonResponse({'coupon_code': config("COUPON_CODE")})
#     return HttpResponse("Not Found!")


# @login_required(login_url='/account/login')
# def Membership(request):
#     payment = Payment.objects.filter(user=request.user)
#     order_currency = "INR"
#     notes = {"order-type": "Membership Payment"}
    
#     if len(payment) != 0:
#         payment = payment[0]
#         order_id = payment.razorpay_order_id
#         if payment.payment_status == 1:
#             messages.success(request, "You are already a member!")
#             return HttpResponseRedirect("/")
#         elif payment.payment_status == 2:
#             razorpay_order = razorpay_client.order.create({"amount": 19900.00, "currency": order_currency, "notes": notes, "receipt": f"MEMBERSHIP_{payment.id}", "payment_capture": "0"})
#             order_id = razorpay_order["id"]
#             payment.razorpay_order_id = order_id
#             payment.save()
#         callback_url = "https://" + str(get_current_site(request)) + "/account/razorpay_callback/"
#         return render(request, 'membership.html', {"order_id": order_id, "razorpay_merchant_id": config("RAZORPAY_KEY_ID"), "callback_url": callback_url})
    
#     new_payment = Payment(user=request.user, amount=199.00)
#     new_payment.save()
#     callback_url = "https://" + str(get_current_site(request)) + "/account/razorpay_callback/"   
#     razorpay_order = razorpay_client.order.create({"amount": 19900.00, "currency": order_currency, "notes": notes, "receipt": f"MEMBERSHIP_{new_payment.id}", "payment_capture": "0"})
#     new_payment.razorpay_order_id = razorpay_order["id"]
#     new_payment.save()
        
#     return render(request, 'membership.html', {"order_id": razorpay_order["id"], "razorpay_merchant_id": config("RAZORPAY_KEY_ID"), "callback_url": callback_url})
	
 
# @csrf_exempt
# @login_required(login_url='/account/login')
# def RazorpayCallback(request):
#     if request.method == "POST":
#         try:
#             payment_id = request.POST.get("razorpay_payment_id", "")
#             order_id = request.POST.get("razorpay_order_id", "")
#             signature = request.POST.get("razorpay_signature", "")
            
#             params_dict = {
#                 "razorpay_payment_id": payment_id,
#                 "razorpay_order_id": order_id,
#                 "razorpay_signature": signature,
#             }
            
#             try:
#                 payment = Payment.objects.get(razorpay_order_id=order_id)
#             except:
#                 messages.error(request, "Payment Details Not Found!!")
#                 return render(request, 'membership.html')
            
#             payment.razorpay_payment_id = payment_id
#             payment.razorpay_signature = signature
#             payment.save()

#             result = razorpay_client.utility.verify_payment_signature(params_dict)
#             if result:
#                 amount = payment.amount * 100
#                 try:
#                     razorpay_client.payment.capture(payment_id, amount)
#                     payment.payment_status = 1
#                     payment.save()
#                     messages.success(request, "You are now member of Studentpeeps!!")
#                     return HttpResponseRedirect('/')
#                 except Exception as e:
#                     print(e)
#                     payment.payment_status = 2
#                     payment.save()
#                     messages.error(request, "Payment Failed, Please Try Again!!")
#                     return HttpResponseRedirect('/')
#         except:
#             messages.error(request, "Payment Failed, Please Try Again!!")
#             return HttpResponseRedirect('/')
#     messages.error(request, "Payment Failed, Please Try Again!!")
#     return render(request, 'membership.html')
