from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic.base import RedirectView
from brands_v2.views import BrandPageView


def discount_explore_redirect(category_id=None):
    """301 to the dynamic student-discount category explore page."""
    url = "/discounts/explore/"
    if category_id:
        url = f"{url}?category={category_id}"
    return RedirectView.as_view(url=url, permanent=True)


admin.site.site_header = "Student Peeps"
admin.site.site_title = "Student Peeps"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('', views.Home.as_view(), name="Home"),
    path('discounts/explore/', views.DiscountExploreView.as_view(), name='DiscountExplore'),
    path('discounts/', views.DiscountsPageView.as_view(), name='DiscountsPage'),
    path('coupons/', RedirectView.as_view(url='/discounts/', permanent=True)),
    path('category/<slug:category_id>/', views.CategoryPageView.as_view(), name='CategoryPage'),
    path('ourstory/', views.OurStory.as_view(), name="OurStory"),
    path(
        'verification-message/',
        RedirectView.as_view(url='/account/identify', permanent=True),
        name="Verificationmsg",
    ),
    path(
        'google-verification-message/',
        RedirectView.as_view(url='/account/identify', permanent=True),
        name="GoogleVerificationmsg",
    ),
    path('upload-message/', views.UploadMessage.as_view(), name="Uploadmsg"),
    path(
        'google-verified/',
        RedirectView.as_view(url='/account/identify', permanent=True),
        name="GoogleVerification",
    ),
    path('contactus/', views.ContactUs.as_view(), name="ContactUs"),
    path(
        'faq/',
        RedirectView.as_view(url='/help-center/frequently-asked-questions/', permanent=True),
        name="Faq",
    ),
    path(
        'privacypolicy/',
        RedirectView.as_view(url='/help-center/privacy-policy/', permanent=True),
        name="PrivacyPolicy",
    ),
    path('subscribe', views.SubscribeView.as_view(), name="SubscribeView"),
    path('unsubscribe', views.UnSubscribeView.as_view(), name="UnSubscribeView"),
    path('community/', views.Community.as_view(), name="Community"),
    path('id-verification-message/',
         views.IdVerificationMessage.as_view(), name="IdVerificationMessage"),

    path('brand/<slug:brand_slug>/', BrandPageView.as_view(), name='brand_page'),
    path('help-center/<slug:slug>/', views.HelpCenterPageView.as_view(), name='help_center_page'),
    
    path('giftcard-page/',
         views.GiftcardView.as_view(), name="GiftcardPage"),
    path('cart/',
         views.CartView.as_view(), name="CartPage"),

    # Legacy category hub paths → dynamic discount explore
    path("all/", discount_explore_redirect()),
    path("tech/", discount_explore_redirect("tech")),
    path("foodsanddrinks/", discount_explore_redirect("food_drink")),
    path("travel/", discount_explore_redirect("travel")),
    path("healthandbeauty/", discount_explore_redirect("health_beauty")),
    path("edtech/", discount_explore_redirect("education")),
    path("booksandstationary/", discount_explore_redirect("books_stationary")),
    path("homeandutilities/", discount_explore_redirect("home_utilities")),
    path("fashion/", discount_explore_redirect("fashion")),
    path("entertainment/", discount_explore_redirect("entertainment")),
    path("exclusive/", discount_explore_redirect("exclusive")),
    path("nonexclusive/", discount_explore_redirect("nonexclusive")),
    path('indigo/', RedirectView.as_view(url='/offer/indigo/spxindigo10/', permanent=True)),
    path('microsoft/', RedirectView.as_view(url='/offer/microsoft/spxmicrosoft365/', permanent=True)),
    path('spotify/', RedirectView.as_view(url='/offer/spotify/spxspotify50/', permanent=True)),
    path('notion/', RedirectView.as_view(url='/offer/notion/spxnotionfree/', permanent=True)),
    path("github/", discount_explore_redirect()),
    path('samsung/', RedirectView.as_view(url='/offer/samsung/spxsamsung30/', permanent=True)),
    path('adobe/', RedirectView.as_view(url='/offer/adobe/spxadobe65/', permanent=True)),
    path('apple/', RedirectView.as_view(url='/offer/apple/spxapple10/', permanent=True)),
    path('applemusic/', RedirectView.as_view(url='/offer/apple-music/spxapplemusic50/', permanent=True)),
    path('amazonprime/', RedirectView.as_view(url='/offer/amazon-prime/spxprime50/', permanent=True)),
    path('ytpremium/', RedirectView.as_view(url='/offer/youtube/spxyoutube40/', permanent=True)),
    path('oneplus/', RedirectView.as_view(url='/offer/oneplus/spxoneplus1500/', permanent=True)),
    path('wix/', RedirectView.as_view(url='/offer/wix/spxwix50/', permanent=True)),
    path("gofirst/", discount_explore_redirect()),
    path("easemytrip/", discount_explore_redirect()),
    path("vistara/", discount_explore_redirect()),
    path('lufthansa/', RedirectView.as_view(url='/offer/lufthansa/spxlufthansa10/', permanent=True)),
    path("spicejet/", discount_explore_redirect()),
    path("nestaway/", discount_explore_redirect()),
    path('whole-truth-food/', RedirectView.as_view(url='/offer/the-whole-truth-food/spxwtf25/', permanent=True)),
    path('student-discount-whole-truth-food/', RedirectView.as_view(url='/offer/the-whole-truth-food/spxwtf25/', permanent=True)),
    path("avni-by-giva/", discount_explore_redirect()),
    path("student-discount-avni/", discount_explore_redirect()),
    path("naagin/", discount_explore_redirect()),
    path("student-discount-naagin/", discount_explore_redirect()),
    path("pee-safe/", discount_explore_redirect()),
    path("student-discount-pee-safe/", discount_explore_redirect()),
    path("propshop/", discount_explore_redirect()),
    path("student-discount-propshop/", discount_explore_redirect()),
    path('to-be-honest/', RedirectView.as_view(url='/offer/to-be-honest/spxtbh15/', permanent=True)),
    path('student-discount-to-be-honest/', RedirectView.as_view(url='/offer/to-be-honest/spxtbh15/', permanent=True)),
    path("bitclass/", discount_explore_redirect()),
    path("student-discount-bitclass/", discount_explore_redirect()),
    path("sattviko/", discount_explore_redirect()),
    path("student-discount-sattviko/", discount_explore_redirect()),
    path('rapido/', RedirectView.as_view(url='/offer/rapido/spxrapido50/', permanent=True)),
    path('student-discount-rapido/', RedirectView.as_view(url='/offer/rapido/spxrapido50/', permanent=True)),
    path("the-womans-company/", discount_explore_redirect()),
    path("student-discount-the-womans-company/", discount_explore_redirect()),
    path("ptal/", discount_explore_redirect()),
    path("student-discount-ptal/", discount_explore_redirect()),
    path("bookchor/", discount_explore_redirect()),
    path("student-discount-bookchor/", discount_explore_redirect()),
    path("bewakoof/", discount_explore_redirect()),
    path("student-discount-bewakoof/", discount_explore_redirect()),
    path("inchpaper/", discount_explore_redirect()),
    path("student-discount-inchpaper/", discount_explore_redirect()),
    path('udemy/', RedirectView.as_view(url='/offer/udemy/spxudemy100/', permanent=True)),
    path('student-discount-udemy/', RedirectView.as_view(url='/offer/udemy/spxudemy100/', permanent=True)),
    path("ragecoffee/", discount_explore_redirect()),
    path("student-discount-ragecoffee/", discount_explore_redirect()),
    path('myntra/', RedirectView.as_view(url='/offer/myntra/spxmyntra300/', permanent=True)),
    path('student-discount-myntra/', RedirectView.as_view(url='/offer/myntra/spxmyntra300/', permanent=True)),
    path("beardo/", discount_explore_redirect()),
    path("student-discount-beardo/", discount_explore_redirect()),
    path("pharmeasy/", discount_explore_redirect()),
    path("student-discount-pharmeasy/", discount_explore_redirect()),
    path('lenovo-flat-5000-off/', RedirectView.as_view(url='/offer/lenovo/spxlenovo5000/', permanent=True)),
    path('student-discount-lenovo-flat-5000-off/', RedirectView.as_view(url='/offer/lenovo/spxlenovo5000/', permanent=True)),
    path('lenovo-flat-2000-off/', RedirectView.as_view(url='/offer/lenovo/spxlenovo2000/', permanent=True)),
    path('student-discount-lenovo-flat-2000-off/', RedirectView.as_view(url='/offer/lenovo/spxlenovo2000/', permanent=True)),
    path('etihad-10-percent-off/', RedirectView.as_view(url='/offer/etihad/spxetihad10/', permanent=True)),
    path('etihad-5-percent-off/', RedirectView.as_view(url='/offer/etihad/spxetihad5/', permanent=True)),
    path('free-two-night-stay-with-etihad/', RedirectView.as_view(url='/offer/etihad/spxetihadcomp/', permanent=True)),
    path('dailyobjects/', RedirectView.as_view(url='/offer/dailyobjects/spxdailyobjects15/', permanent=True)),
    path('student-discount-dailyobjects/', RedirectView.as_view(url='/offer/dailyobjects/spxdailyobjects15/', permanent=True)),

]

