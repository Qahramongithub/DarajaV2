from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.template.response import TemplateResponse  # TemplateResponse import qilish
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from .models import ProductHistory, FinishProductHistory, Category, FinishCategory


# ===================== Custom Admin Site =======================
class CustomAdminSite(admin.AdminSite):
    site_header = "Custom Admin Panel"
    site_title = "Admin Panel"
    index_title = "Dashboard"

    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = ['/static/admin/css/custom_admin.css']
        return context


custom_admin_site = CustomAdminSite(name='custom_admin')


# ===================== Common Methods for Price Calculation =======================
def update_total_price(queryset):
    """
    Mahsulotlar narxini hisoblash va umumiy qiymatni qaytarish
    """
    return queryset.annotate(total_item_narxi=F('narxi') * F('soni')).aggregate(total=Sum('total_item_narxi'))[
        'total'] or 0


# ===================== 1 - Product History =======================
@admin.register(ProductHistory, site=custom_admin_site)
class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('get_nomi', 'soni', 'status_button', 'narxi', 'status',)
    list_filter = [
        ("created_at", DateRangeFilter),
        'status',
        'nomi',
    ]
    list_editable = ('status',)
    search_fields = ('nomi__nomi',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        response = super().changelist_view(request, extra_context=extra_context)

        if not isinstance(response, TemplateResponse):
            return response  # Redirect bo‘lsa, bevosita response qaytaramiz

        # 🔹 `cl` obyekt mavjudligini tekshiramiz
        cl = response.context_data.get('cl', None)
        if cl is not None:
            queryset = cl.queryset
            total_price = update_total_price(queryset)
            extra_context['title'] = f"Umumiy mahsulotlar narxi: {total_price:,} so'm"

            # 🔹 `context_data` ni yangilaymiz
            response.context_data.update(extra_context)

        return response

    def get_nomi(self, obj):
        return obj.nomi.nomi

    get_nomi.short_description = 'Nomi'

    def status_button(self, obj):
        color = {
            "qabul": "blue",
            "chiqdi": "green",
        }.get(obj.status.lower(), "gray")

        return format_html(
            '<button style="background-color: {}; color: white; border: none; padding: 5px 10px;">{}</button>',
            color,
            obj.status.capitalize(),
        )

    status_button.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(nomi__user=request.user)


# ===================== 2 - Finish Product History =======================
@admin.register(FinishProductHistory, site=custom_admin_site)
class FinishProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('get_nomi', 'soni', 'status_button', 'formatted_date', 'narxi')
    list_filter = (
        ('created_at', DateRangeFilter),
        'status',
        'nomi',
    )
    search_fields = ('nomi__nomi',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # 🔹 Super klassdan chaqiramiz
        response = super().changelist_view(request, extra_context=extra_context)

        # 🔥 HttpResponseRedirect bo‘lsa, context_data mavjud emas
        if not isinstance(response, TemplateResponse):
            return response  # Redirect bo‘lsa, bevosita response qaytaramiz

        # 🔹 `cl` obyekt mavjudligini tekshiramiz
        cl = response.context_data.get('cl', None)
        if cl is not None:
            queryset = cl.queryset
            total_price = update_total_price(queryset)
            extra_context['title'] = f"Umumiy mahsulotlar narxi: {total_price:,} so'm"

            # 🔹 `context_data` ni yangilaymiz
            response.context_data.update(extra_context)

        return response

    def get_nomi(self, obj):
        return obj.nomi.nomi

    get_nomi.short_description = 'Nomi'

    def formatted_date(self, obj):  # sanani formatlash
        return obj.created_at.strftime('%Y-%m-%d')

    formatted_date.short_description = "Sana"

    def status_button(self, obj):  # statuslarga rang berilgan
        color = {
            "qabul": "blue",
            "chiqdi": "green",
        }.get(obj.status.lower(), "gray")  # Default rang - gray

        return format_html(
            '<button style="background-color: {}; color: white; border: none; padding: 5px 10px;">{}</button>',
            color,
            obj.status.capitalize(),
        )

    status_button.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(nomi__user=request.user)


# ===================== 3 - Category va FinishCategory =======================
@admin.register(Category, site=custom_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(user=request.user)


@admin.register(FinishCategory, site=custom_admin_site)
class FinishCategoryAdmin(admin.ModelAdmin):
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(user=request.user)

    # ===================== Unregister Django Default Users =======================


admin.site.unregister(User)
admin.site.unregister(Group)
