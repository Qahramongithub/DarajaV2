from django import forms

from apps.models import FinishProduct, Product


class FinishProductModelForm(forms.ModelForm):
    class Meta:
        model = FinishProduct
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)
