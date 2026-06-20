"""
serializers.py  ─  DRF serializers for FLASH_ERP_DB
=====================================================
Place this file at:  FLASH_ERP_API/api/serializers.py
"""

from rest_framework import serializers
from .models import Department, Debtor, Product, ProductBatch


# ── Departments ───────────────────────────────────────────────────────────

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['department_id', 'department']


# ── Debtors ───────────────────────────────────────────────────────────────

class DebtorSerializer(serializers.ModelSerializer):
    # Many source-DB records have NULL in optional fields — accept and coerce to default.
    place             = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    phone             = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    phone2            = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    openingdepartment = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    area              = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    address           = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    city              = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    gstin             = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    remarkcolumntitle = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    opening_balance   = serializers.FloatField(required=False, allow_null=True)
    debit             = serializers.FloatField(required=False, allow_null=True)
    credit            = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model  = Debtor
        fields = [
            "code", "name", "opening_balance", "debit", "credit",
            "place", "phone", "phone2", "openingdepartment", "area",
            "super_code", "address", "city", "gstin", "remarkcolumntitle",
        ]


# ── Products ──────────────────────────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    name         = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    size         = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    sub_category = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    unit         = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    taxcode      = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    company      = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    product      = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    brand        = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    text6        = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    nameinsl     = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")

    class Meta:
        model  = Product
        fields = [
            'code', 'name', 'size', 'sub_category', 'unit', 'taxcode',
            'company', 'product', 'brand', 'text6', 'nameinsl',
        ]


# ── Product Batches ───────────────────────────────────────────────────────

class ProductBatchSerializer(serializers.ModelSerializer):
    # Expose product FK as a plain string field so bulk payloads can send
    # {"product_code": "P001", "salesprice": ..., ...} without nesting.
    product_code  = serializers.CharField(source='product_id')
    barcode       = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="")
    salesprice    = serializers.FloatField(required=False, allow_null=True)
    secondprice   = serializers.FloatField(required=False, allow_null=True)
    thirdprice    = serializers.FloatField(required=False, allow_null=True)
    fourthprice   = serializers.FloatField(required=False, allow_null=True)
    nlc1          = serializers.FloatField(required=False, allow_null=True)
    quantity      = serializers.FloatField(required=False, allow_null=True)
    bmrp          = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model  = ProductBatch
        fields = [
            'product_code', 'barcode', 'salesprice', 'secondprice',
            'thirdprice', 'fourthprice', 'nlc1', 'quantity', 'bmrp',
        ]


# ── Combined sync response ────────────────────────────────────────────────

class DepartmentListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = DepartmentSerializer(many=True)


class DebtorListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = DebtorSerializer(many=True)


class ProductListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = ProductSerializer(many=True)


class ProductBatchListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = ProductBatchSerializer(many=True)


class SyncSerializer(serializers.Serializer):
    departments    = DepartmentListSerializer()
    debtors        = DebtorListSerializer()
    products       = ProductListSerializer()
    productbatches = ProductBatchListSerializer()