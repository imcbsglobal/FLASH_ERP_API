"""
models.py  ─  Django ORM models for FLASH_ERP_DB (PostgreSQL)
==============================================================
Place this file at:  FLASH_ERP_API/api/models.py

These models map directly to tables in the PostgreSQL database.
Run after any change:
    python manage.py makemigrations
    python manage.py migrate
"""

from django.db import models


# ── Departments ───────────────────────────────────────────────────────────

class Department(models.Model):
    department_id = models.CharField(max_length=30, primary_key=True)
    department    = models.CharField(max_length=30)

    class Meta:
        db_table = 'acc_departments'
        ordering = ['department_id']

    def __str__(self):
        return f"{self.department_id} — {self.department}"


# ── Debtors (acc_master WHERE super_code = DEBTO) ─────────────────────────

class Debtor(models.Model):
    code               = models.CharField(max_length=30, primary_key=True)
    name               = models.CharField(max_length=250)
    opening_balance    = models.FloatField(null=True, blank=True)
    debit              = models.FloatField(null=True, blank=True)
    credit             = models.FloatField(null=True, blank=True)
    place              = models.CharField(max_length=60,  blank=True, default='')
    phone              = models.CharField(max_length=60,  blank=True, default='')
    phone2             = models.CharField(max_length=60,  blank=True, default='')
    openingdepartment  = models.CharField(max_length=30,  blank=True, default='')
    area               = models.CharField(max_length=30,  blank=True, default='')
    super_code         = models.CharField(max_length=5,   default='DEBTO')
    address            = models.CharField(max_length=100, blank=True, default='')
    city               = models.CharField(max_length=80,  blank=True, default='')
    gstin              = models.CharField(max_length=30,  blank=True, default='')
    remarkcolumntitle  = models.CharField(max_length=20,  blank=True, default='')

    class Meta:
        db_table = 'acc_master'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"


# ── Products (acc_product) ────────────────────────────────────────────────

class Product(models.Model):
    code         = models.CharField(max_length=30,  primary_key=True)
    name         = models.CharField(max_length=200, blank=True, default='')
    size         = models.CharField(max_length=60,  blank=True, default='')   # <- text3
    sub_category = models.CharField(max_length=60,  blank=True, default='')   # <- text5
    unit         = models.CharField(max_length=10,  blank=True, default='')
    taxcode      = models.CharField(max_length=5,   blank=True, default='')
    company      = models.CharField(max_length=30,  blank=True, default='')
    product      = models.CharField(max_length=30,  blank=True, default='')
    brand        = models.CharField(max_length=30,  blank=True, default='')
    text6        = models.CharField(max_length=40,  blank=True, default='')
    nameinsl     = models.CharField(max_length=350, blank=True, default='')

    class Meta:
        db_table = 'acc_product'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"


# ── Product Batches (acc_productbatch) ────────────────────────────────────

class ProductBatch(models.Model):
    product     = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        db_column='product_code',
        primary_key=True,          # product_code is the key — one batch row per product
        related_name='batch',
        db_constraint=False,       # keeps the ORM relation, drops the DB-level FK constraint
    )
    barcode     = models.CharField(max_length=35, blank=True, default='')
    salesprice  = models.FloatField(null=True, blank=True)
    secondprice = models.FloatField(null=True, blank=True)
    thirdprice  = models.FloatField(null=True, blank=True)
    fourthprice = models.FloatField(null=True, blank=True)
    nlc1        = models.FloatField(null=True, blank=True)
    quantity    = models.FloatField(null=True, blank=True)
    bmrp        = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'acc_productbatch'
        ordering = ['product_id']

    def __str__(self):
        return f"{self.product_id}"


# ── Sync Log ──────────────────────────────────────────────────────────────

class SyncLog(models.Model):
    started_at        = models.DateTimeField(auto_now_add=True)
    finished_at       = models.DateTimeField(null=True, blank=True)
    departments_ok    = models.IntegerField(default=0)
    departments_fail  = models.IntegerField(default=0)
    debtors_ok        = models.IntegerField(default=0)
    debtors_fail      = models.IntegerField(default=0)
    products_ok       = models.IntegerField(default=0)
    products_fail     = models.IntegerField(default=0)
    productbatches_ok   = models.IntegerField(default=0)
    productbatches_fail = models.IntegerField(default=0)
    mode              = models.CharField(max_length=10, default='push')  # 'push' or 'pull'
    notes             = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"SyncLog {self.started_at:%Y-%m-%d %H:%M:%S} ({self.mode})"