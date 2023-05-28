from django.contrib import admin
from django.urls import path
from . import views

admin.site.site_header = "Login to Student Peeps"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Welcome to Student Peeps Dashboard"

urlpatterns = [
    path('', views.Home.as_view(), name="Home"),
    path('ourstory/', views.OurStory.as_view(), name="OurStory"),
    path('verification-message/',
         views.VerificationMessage.as_view(), name="Verificationmsg"),
    path('google-verification-message/',
         views.GoogleVerifyMessage.as_view(), name="GoogleVerificationmsg"),
    path('upload-message/', views.UploadMessage.as_view(), name="Uploadmsg"),
    path('google-verified/', views.GoogleVerification.as_view(), name="GoogleVerification"),
    path('contactus/', views.ContactUs.as_view(), name="ContactUs"),
    path('faq/', views.FAQ.as_view(), name="Faq"),
    path('privacypolicy/', views.Privacy.as_view(), name="PrivacyPolicy"),
    path('request-your-fav-brand/', views.Favorite.as_view(), name="Favroiute"),
    path('course-application/', views.Course.as_view(), name="Course"),
    path('resource/', views.Tools.as_view(), name="Resource"),
    path('subscribe/', views.SubscribeView.as_view(), name="SubscribeView"),
    path('unsubscribe/', views.UnSubscribeView.as_view(), name="UnSubscribeView"),
    path('community/', views.Community.as_view(), name="Community"),
    path('all/', views.All.as_view(), name="All"),
    path('tech/', views.Tech.as_view(), name="Tech"),
    path('entertainment/', views.Entertainment.as_view(), name="Entertainment"),
    path('foodsanddrinks/', views.FoodsAndDrinks.as_view(), name="FoodsAndDrinks"),
    path('travel/', views.Travel.as_view(), name="Travel"),
    path('healthandbeauty/', views.HealthAndBeauty.as_view(), name="HealthAndBeauty"),
    path('edtech/', views.Edtech.as_view(), name="Edtech"),
    path('booksandstationary/', views.BooksAndStationary.as_view(), name="BooksAndStationary"),
    path('homeandutilities/', views.HomeAndUtilities.as_view(), name="HomeAndUtilities"),
    path('fashion/', views.Fashion.as_view(), name="Fashion"),
    path('exclusive/', views.Exclusive.as_view(), name="Exclusive"),
    path('nonexclusive/', views.NonExclusive.as_view(), name="NonExclusive"),

    path('indigo/', views.Indigo.as_view(), name='Indigo'),
    path('microsoft/', views.Microsoft.as_view(), name='Microsoft'),
    path('spotify/', views.Spotify.as_view(), name='Spotify'),
    path('notion/', views.Notion.as_view(), name='Notion'),
    path('github/', views.Github.as_view(), name='Github'),
    path('samsung/', views.Samsung.as_view(), name='Samsung'),
    path('adobe/', views.Adobe.as_view(), name='Adobe'),
    path('apple/', views.Apple.as_view(), name='Apple'),
    path('applemusic/', views.AppleMusic.as_view(), name='AppleMusic'),
    path('amazonprime/', views.AmazonPrime.as_view(), name='AmazonPrime'),
    path('ytpremium/', views.YTPremium.as_view(), name='YTPremium'),
    path('oneplus/', views.OnePlus.as_view(), name='OnePlus'),
    path('wix/', views.Wix.as_view(), name='Wix'),
    path('gofirst/', views.GoFirst.as_view(), name='GoFirst'),
    path('easemytrip/', views.EaseMyTrip.as_view(), name='EaseMyTrip'),
    path('vistara/', views.Vistara.as_view(), name='Vistara'),
    path('lufthansa/', views.Lufthansa.as_view(), name='Lufthansa'),
    path('spicejet/', views.SpiceJet.as_view(), name='SpiceJet'),
    path('nestaway/', views.Nestaway.as_view(), name='Nestaway'),

    path('whole-truth-food/', views.WTF.as_view(), name='Wtf'),
    path('student-discount-whole-truth-food/', views.CodeWTF.as_view(), name='CodeWtf'),

    path('avni-by-giva/', views.Avni.as_view(), name='Avni'),
    path('student-discount-avni/', views.CodeAvni.as_view(), name='CodeAvni'),

    path('naagin/', views.Naagin.as_view(), name='Naagin'),
    path('student-discount-naagin/', views.CodeNaagin.as_view(), name='CodeNaagin'),

    path('pee-safe/', views.Peesafe.as_view(), name='PEESAFE'),
    path('student-discount-pee-safe/', views.CodePeesafe.as_view(), name='CodePEESAFE'),

    path('propshop/', views.PropShop.as_view(), name='Propshop'),
    path('student-discount-propshop/', views.CodePropShop.as_view(), name='CodePropshop'),

    path('trib/', views.Trib.as_view(), name='TRIB'),
    path('student-discount-trib/', views.CodeTrib.as_view(), name='CodeTRIB'),

    path('to-be-honest/', views.TBH.as_view(), name='TBH'),
    path('student-discount-to-be-honest/', views.CodeTBH.as_view(), name='CodeTBH'),

    path('unlu-class/', views.Unlu.as_view(), name='Unlu'),
    path('student-discount-unlu-class/', views.CodeUnlu.as_view(), name='CodeUnlu'),

    path('unlu-shoutout/', views.Unlu2.as_view(), name='Unlu2'),
    path('student-discount-unlu-shoutout/', views.CodeUnlu2.as_view(), name='CodeUnlu2'),

    path('bitclass/', views.Bitclass.as_view(), name='bitclass'),
    path('student-discount-bitclass/', views.CodeBitclass.as_view(), name='Codebitclass'),

    path('mypaperclip/', views.MyPaperClip.as_view(), name='MyPaperClip'),
    path('student-discount-mypaperclip/', views.CodeMyPaperClip.as_view(), name='CodeMyPaperClip'),

    path('mittihub/', views.MittiHub.as_view(), name='Mittihub'),
    path('student-discount-mittihub/', views.CodeMittiHub.as_view(), name='CodeMittihub'),

    path('sattviko/', views.SattViko.as_view(), name='Sattviko'),
    path('student-discount-sattviko/', views.CodeSattViko.as_view(), name='CodeSattviko'),

    path('rapido/', views.Rapido.as_view(), name='Rapido'),
    path('student-discount-rapido/', views.CodeRapido.as_view(), name='StudentDiscountRapido'),

    path('the-womans-company/', views.TWC.as_view(), name='TWC'),
    path('student-discount-the-womans-company/', views.CodeTWC.as_view(), name='StudentDiscountTWC'),

    path('ptal/', views.Ptal.as_view(), name='Ptal'),
    path('student-discount-ptal/', views.CodePtal.as_view(), name='StudentDiscountPtal'),

    path('bookchor/', views.Bookchor.as_view(), name='Bookchor'),
    path('student-discount-bookchor/', views.CodeBookchor.as_view(), name='StudentDiscountBookchor'),

    path('bewakoof/', views.Bewakoof.as_view(), name='Bewakoof'),
    path('student-discount-bewakoof/', views.CodeBewakoof.as_view(), name='StudentDiscountBewakoof'),

    path('inchpaper/', views.Inchpaper.as_view(), name='Inchpaper'),
    path('student-discount-inchpaper/', views.CodeInchpaper.as_view(), name='StudentDiscountInchpaper'),

    path('udemy/', views.Udemy.as_view(), name='Udemy'),
    path('student-discount-udemy/', views.CodeUdemy.as_view(), name='CodeUdemy'),

    path('ragecoffee/', views.RageCoffee.as_view(), name='RageCoffee'),
    path('student-discount-ragecoffee/', views.CodeRageCoffee.as_view(), name='CodeRageCoffee'),

    path('myntra/', views.Myntra.as_view(), name='Myntra'),
    path('student-discount-myntra/', views.CodeMyntra.as_view(), name='CodeMnytra'),

    path('beardo/', views.Beardo.as_view(), name='Beardo'),
    path('student-discount-beardo/', views.CodeBeardo.as_view(), name='CodeBeardo'),

    path('pharmeasy/', views.PharmEasy.as_view(), name='PharmEasy'),
    path('student-discount-pharmeasy/', views.CodePharmEasy.as_view(), name='CodePharmEasy'),

#     path('paymentuser/', views.paymentuser, name='paymentuser'),
]

