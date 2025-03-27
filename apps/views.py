import json
import os

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, FormView
import telebot
from .form import ProductForm, FinishProductModelForm, AdminLoginForm
from .models import Product, Category, FinishProduct, FinishCategory, ProductHistory, FinishProductHistory
from dotenv import load_dotenv

load_dotenv()


class AdminFormView(FormView):
    form_class = AdminLoginForm
    template_name = 'admin/admin.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        request = self.request
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        admin = authenticate(request, username=username, password=password)

        if admin is not None:
            login(request, admin)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Foydalanuvchi nomi yoki parol noto‘g‘ri')
            return self.form_invalid(form)


class ProductListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(soni__gt=0, nomi__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['finish_product'] = FinishProduct.objects.filter(soni__gt=0, nomi__user=self.request.user)
        return context


@csrf_exempt
def sell_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')  # Mahsulot ID
            decrease_amount = int(data.get('decrease_amount'))  # Kamaytirish miqdori

            product = Product.objects.get(id=product_id)

            if decrease_amount > product.soni:
                return JsonResponse({'success': False, 'error': 'Kiritilgan miqdor mavjuddan oshib ketdi!'})

            product.soni -= decrease_amount
            product.save()

            text = (f"🛒 *1-Sklad Maxsulot Chiqdi* \n"
                    f"📦 Nomi: {product.nomi.nomi}\n"
                    f"💸 Narxi : {product.narxi}\n"
                    f"↗️ Chiqib ketdi: {decrease_amount}\n"
                    f"🔢 Qoldi: {product.soni}")

            bot = telebot.TeleBot(os.getenv('TOKEN'))
            try:
                bot.send_message(chat_id=os.getenv('ID'), text=text, parse_mode="Markdown")
            except Exception as e:
                return JsonResponse({'success': False, 'error': f"Telegramga ulanishda xatolik: {str(e)}"})

            ProductHistory.objects.create(
                nomi=product.nomi,
                soni=decrease_amount,
                status=ProductHistory.StatusType.CHIQDI,
                narxi=product.narxi
            )

            return JsonResponse({'success': True, 'new_quantity': product.soni})

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi!'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Yaroqsiz JSON maʼlumot!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Serverdagi xato: {str(e)}"})

    return JsonResponse({'success': False, 'error': 'Faqat POST so‘rov qabul qilinadi!'})


class ProductFormView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    template_name = 'product_add.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(
            user=self.request.user)
        return context

    def form_valid(self, form):
        nomi_id = form.cleaned_data['nomi']
        soni = form.cleaned_data['soni']
        narxi = form.cleaned_data['narxi']

        product = Product.objects.filter(nomi_id=nomi_id, narxi=narxi).first()

        if product:
            product.soni += soni
            product.save()
            text = (f"🛒 *1 - Sklat Maxsulot qushildi \n"
                    f"🅿️Nomi : {product.nomi.nomi}\n"
                    f"💸Narxi : {product.narxi}\n"
                    f"↘️Qushildi : {soni}\n"
                    f"🔢Jami : {product.soni}")
        else:
            category = Category.objects.filter(id=nomi_id.pk).first()
            if category:
                text = (f"🛒 *1 - Sklad Maxsulot qushildi \n"
                        f"🅿️Nomi : {category.nomi}\n"
                        f"💸Narxi: {narxi}\n"
                        f"↘️Qushildi : {soni}\n"
                        f"🔢Jami : {soni}")
            else:
                text = "Kategoriya topilmadi."
            form.save()
        TOKEN = os.getenv('TOKEN')
        bot = telebot.TeleBot(TOKEN)
        ProductHistory.objects.create(nomi=nomi_id, soni=soni, status=ProductHistory.StatusType.QABUL, narxi=narxi)

        try:
            bot.send_message(chat_id=(os.getenv('ID')), text=text)
        except Exception as e:
            pass

        form.instance.user = self.request.user  # Foydalanuvchining ma'lumotlarini formaga qo'shish

        return super().form_valid(form)


@csrf_exempt
def sell_finish_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # JSON ma'lumotlarni olish
            product_id = data.get('product_id')  # Mahsulot ID
            decrease_amount = int(data.get('decrease_amount'))  # Kamaytirish miqdori

            product = FinishProduct.objects.get(id=product_id)

            if decrease_amount > product.soni:
                return JsonResponse({'success': False, 'error': 'Kiritilgan miqdor mavjuddan oshib ketdi!'})

            product.soni -= decrease_amount
            product.save()
            text = (f"🛒 *2 - Skald Maxsulot Chiqdi \n"
                    f"🅿️Nomi : {product.nomi.nomi}\n"
                    f"💸Narxi : {product.narxi}\n"
                    f"↗️Chiqib ketdi : {decrease_amount}\n"
                    f"🔢Qoldi : {product.soni}\n")

            bot = telebot.TeleBot(os.getenv('TOKEN'))
            FinishProductHistory.objects.create(nomi=product.nomi, soni=decrease_amount,
                                                status=FinishProductHistory.StatusType.CHIQDI, narxi=product.narxi)

            try:
                bot.send_message(chat_id=(os.getenv('ID')), text=text)
            except Exception as e:
                return e

            return JsonResponse({'success': True, 'new_quantity': product.soni})  # Yangi miqdorni qaytarish
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Noto‘g‘ri so‘rov turi.'})


class FinishProductFormView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    template_name = 'finish_product_add.html'
    form_class = FinishProductModelForm
    success_url = reverse_lazy('product_list')

    def get_queryset(self):
        return FinishCategory.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_queryset()  # get_queryset metodidan foydalanish
        return context

    def form_valid(self, form):
        # Formadan to'plangan ma'lumotlarni olish
        nomi_id = form.cleaned_data['nomi']
        soni = form.cleaned_data['soni']
        narxi = form.cleaned_data['narxi']

        product = FinishProduct.objects.filter(nomi_id=nomi_id, narxi=narxi).first()

        if product:
            product.soni += soni
            product.save()
            text = (f"🛒 *2 - Sklad Maxsulot qushildi \n"
                    f"🅿️Nomi : {product.nomi.nomi}\n"
                    f"💸Narxi : {narxi}\n"
                    f"↘️Qushildi : {soni}\n"
                    f"🔢Jami : {product.soni}\n"
                    )
        else:
            finish_category = FinishCategory.objects.filter(id=nomi_id.id).first()  # .id ni to'g'riladik
            text = (f"🛒 *2 - Sklad Maxsulot qushildi \n"
                    f"🅿️Nomi : {finish_category.nomi}\n"
                    f"💸Narxi : {narxi}\n"
                    f"↘️Qushildi : {soni}\n"
                    f"🔢Jami : {soni}\n")
            form.save()

        FinishProductHistory.objects.create(
            nomi=nomi_id,
            soni=soni,
            status=FinishProductHistory.StatusType.QABUL,
            narxi=narxi
        )

        bot = telebot.TeleBot(os.getenv('TOKEN'))
        try:
            bot.send_message(chat_id=os.getenv('ID'), text=text)
        except Exception as e:
            pass

        return super().form_valid(form)
