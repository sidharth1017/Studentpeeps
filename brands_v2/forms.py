from django import forms
from .models import Offer, Brand
from django_summernote.widgets import SummernoteWidget

class OfferAdminForm(forms.ModelForm):
    about = forms.CharField(widget=SummernoteWidget(), required=False)
    tnc = forms.CharField(widget=SummernoteWidget(), required=False)
    redemption = forms.CharField(widget=SummernoteWidget(), required=False)
    codes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Enter codes separated by commas."
    )

    class Meta:
        model = Offer
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.codes:
            # Ensure codes display properly as CSV string
            if isinstance(self.instance.codes, list):
                self.initial['codes'] = ', '.join(self.instance.codes)
            elif isinstance(self.instance.codes, str):
                # Edge case: if codes saved incorrectly as a string
                import ast
                try:
                    parsed = ast.literal_eval(self.instance.codes)
                    if isinstance(parsed, list):
                        self.initial['codes'] = ', '.join(parsed)
                except Exception:
                    self.initial['codes'] = self.instance.codes  # fallback as is

    def clean_codes(self):
        codes_str = self.cleaned_data.get('codes', '')
        codes_list = [code.strip() for code in codes_str.split(',') if code.strip()]
        return codes_list  # ✅ Return a clean list, no nested lists




class BrandAdminForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget(), required=False)
    about = forms.CharField(widget=SummernoteWidget(), required=False)

    class Meta:
        model = Brand
        fields = '__all__'