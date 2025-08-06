import csv
from django.core.files.storage import default_storage
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from ..models import Brand, Offer, OfferSEO, OfferCodeForUser, Category

class BulkUploadView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'admin/bulkUpload.html')

    def post(self, request):
        upload_type = request.POST.get('upload_type')
        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            messages.error(request, 'No file selected.')
            return redirect(request.path)

        file_data = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(file_data)

        if upload_type == 'brand':
            self.handle_brand_upload(reader)
            messages.success(request, 'Brands imported successfully!')

        elif upload_type == 'offer':
            self.handle_offer_upload(reader)
            messages.success(request, 'Offers imported successfully!')

        elif upload_type == 'seo':
            self.handle_seo_upload(reader)
            messages.success(request, 'Offer SEO imported successfully!')

        else:
            messages.error(request, 'Invalid upload type.')

        return redirect(request.path)

    def handle_brand_upload(self, reader):
        for row in reader:
            brand, created = Brand.objects.update_or_create(
                name=row['name'],
                defaults={
                    'slug': row.get('slug') or '',
                    'description': row.get('description', ''),
                    'website': row.get('website', ''),
                    'about': row.get('about', '')
                }
            )

            logo_path = 'brand_logos/' + row.get('logo', '')
            thumbnail_path = 'brand_thumbnails/' + row.get('thumbnail_image', '')

            if default_storage.exists(logo_path):
                brand.logo.name = logo_path

            if default_storage.exists(thumbnail_path):
                brand.thumbnail_image.name = thumbnail_path

            brand.save()

    def handle_offer_upload(self, reader):
        for row in reader:
            try:
                brand = Brand.objects.get(slug=row['brand_slug'])
            except Brand.DoesNotExist:
                continue

            category_slug_or_name = row.get('category', '').strip()
            category_instance = None
            if category_slug_or_name:
                try:
                    category_instance = Category.objects.get(category_id=category_slug_or_name)
                except Category.DoesNotExist:
                    category_instance = Category.objects.get(category_id="uncategorized")
                    continue

            offer, created = Offer.objects.update_or_create(
                custom_id=row['custom_id'],
                defaults={
                    'brand': brand,
                    'title': row['title'],
                    'subtitle': row.get('subtitle', ''),
                    'category': category_instance,
                    'thumbnail_image': 'exclusive_thumbnails/' + row.get('thumbnail_image', ''),
                    'about': row.get('about', ''),
                    'tnc': row.get('tnc', ''),
                    'redemption': row.get('redemption', ''),
                    'background_color': row.get('background_color', '#ffffff'),
                    'codes': [code.strip() for code in row.get('codes', '').split(',') if code.strip()],
                    'offer_link': row.get('offer_link', ''),
                    'isStaticCode': row.get('isStaticCode', 'True').lower() == 'true',
                    'isExclusive': row.get('isExclusive', 'True').lower() == 'true',
                    'isLoginRequired': row.get('isLoginRequired', 'False').lower() == 'true'
                }
            )

            offer.save()

    def handle_seo_upload(self, reader):
        for row in reader:
            try:
                offer = Offer.objects.get(custom_id=row['offer_custom_id'])
            except Offer.DoesNotExist:
                continue 

            seo_obj, created = OfferSEO.objects.update_or_create(
                offer=offer,
                defaults={
                    'title': row['title'],
                    'description': row['description'],
                    'keywords': [kw.strip() for kw in row.get('keywords', '').split(',') if kw.strip()]
                }
            )

            og_image_path = 'seo_og_images/' + row.get('og_image', '')
            if default_storage.exists(og_image_path):
                seo_obj.og_image.name = og_image_path

            seo_obj.save()