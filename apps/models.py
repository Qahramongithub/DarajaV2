from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '1 - Sklad Kategoriyasi'

    def __str__(self):
        return self.nomi


class Product(models.Model):
    soni = models.IntegerField()
    nomi = models.ForeignKey('apps.Category', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='products')
    narxi = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Sklad 1"

    def __str__(self):
        return self.nomi.nomi


# ================= Sklad 2 ===================================================================================

class FinishCategory(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '2 - Sklad Kategoriasi'

    def __str__(self):
        return self.nomi


class FinishProduct(models.Model):
    soni = models.IntegerField()
    nomi = models.ForeignKey('apps.FinishCategory', on_delete=models.CASCADE, null=True, blank=True, )
    narxi = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Sklad 2'

    def __str__(self):
        return self.nomi


class ProductHistory(models.Model):
    class StatusType(models.TextChoices):
        CHIQDI = 'chiqdi', 'Chiqdi'
        QABUL = 'qabul', 'Qabul'

    nomi = models.ForeignKey('apps.Category', on_delete=models.CASCADE, null=True, blank=True, )
    soni = models.IntegerField()
    status = models.CharField(choices=StatusType.choices, default=StatusType.CHIQDI, max_length=100,
                              verbose_name="Holat")
    created_at = models.DateField(auto_now_add=True, verbose_name="Sana")
    narxi = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = '1 - Sklad'


class FinishProductHistory(models.Model):
    class StatusType(models.TextChoices):
        CHIQDI = 'chiqdi', 'Chiqdi'
        QABUL = 'qabul', 'Qabul'

    nomi = models.ForeignKey('apps.FinishCategory', on_delete=models.CASCADE, null=True, blank=True, )
    soni = models.IntegerField()
    status = models.CharField(choices=StatusType.choices, default=StatusType.CHIQDI, max_length=100,
                              verbose_name="Holat")
    created_at = models.DateField(auto_now_add=True, verbose_name="Sana")
    narxi = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = '2 - Sklad'
