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
