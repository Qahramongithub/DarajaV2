from django.contrib import admin
from django.contrib.auth.models import User, Group
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
    list_display = ('get_nomi', 'soni', 'status_button', 'narxi')
    list_filter = [
        ("created_at", DateRangeFilter),
        'status',
        'nomi',
    ]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        response = super().changelist_view(request, extra_context=extra_context)

        # response orqali queryset olish
        queryset = response.context_data['cl'].queryset
        total_price = update_total_price(queryset)

        # Umumiy narxni qo'shish
        extra_context['title'] = f"Umumiy mahsulotlar narxi: {total_price} so'm"

        # Agar response TemplateResponse bo'lsa, context_data ga o'zgartirish kiritamiz
        if isinstance(response, TemplateResponse):
            response.context_data.update(extra_context)

        return response

    def get_nomi(self, obj):
        return obj.nomi.nomi

    get_nomi.short_description = 'Nomi'

    def status_button(self, obj):
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
        return False  # Yangi mahsulot qo'shishni cheklash

    def has_delete_permission(self, request, obj=None):
        return False


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
        response = super().changelist_view(request, extra_context=extra_context)

        # Agar response TemplateResponse bo'lsa, context_data-ni yangilash
        if isinstance(response, TemplateResponse):
            queryset = response.context_data['cl'].queryset
            total_price = update_total_price(queryset)
            extra_context['title'] = f"Umumiy mahsulotlar narxi: {total_price} so'm"
            response.context_data.update(extra_context)

        return response

    def get_nomi(self, obj):
        return obj.nomi.nomi

    get_nomi.short_description = 'Nomi'

    def formatted_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')

    formatted_date.short_description = "Sana"

    def status_button(self, obj):
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
        return False  # Yangi mahsulot qo'shishni cheklash
    def has_delete_permission(self, request, obj=None):
        return False


# ===================== 3 - Category va FinishCategory =======================
@admin.register(Category, site=custom_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    pass  # Agar kerakli o'zgarishlar bo'lsa, bu yerda sozlash mumkin


@admin.register(FinishCategory, site=custom_admin_site)
class FinishCategoryAdmin(admin.ModelAdmin):
    pass  # Agar kerakli o'zgarishlar bo'lsa, bu yerda sozlash mumkin


# ===================== Unregister Django Default Users =======================
admin.site.unregister(User)
admin.site.unregister(Group)
