"""
serializers.py  ─  DRF serializers for FLASH_ERP_DB
=====================================================
Place this file at:  FLASH_ERP_API/api/serializers.py
"""

from rest_framework import serializers
from .models import Department, Debtor


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


# ── Combined sync response ────────────────────────────────────────────────

class DepartmentListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = DepartmentSerializer(many=True)


class DebtorListSerializer(serializers.Serializer):
    count   = serializers.IntegerField()
    results = DebtorSerializer(many=True)


class SyncSerializer(serializers.Serializer):
    departments = DepartmentListSerializer()
    debtors     = DebtorListSerializer()