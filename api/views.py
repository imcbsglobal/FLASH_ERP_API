"""
views.py  ─  REST API views for FLASH_ERP_DB (PostgreSQL)
==========================================================
Place this file at:  FLASH_ERP_API/api/views.py

All DB access uses Django ORM (PostgreSQL via psycopg2).
No pyodbc / SQL Anywhere dependency here anymore.
Demo mode still works — set DB_DEMO_MODE=True in .env to use mock data.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .models import Department, Debtor, Product, ProductBatch
from .serializers import (
    DepartmentSerializer, DebtorSerializer,
    ProductSerializer, ProductBatchSerializer,
)

logger = logging.getLogger(__name__)


# ── Demo / mock data ──────────────────────────────────────────────────────
#   Only used when DB_DEMO_MODE=True in .env

DEMO_DEPARTMENTS = [
    {"department_id": "DEPT001", "department": "Sales"},
    {"department_id": "DEPT002", "department": "Purchase"},
    {"department_id": "DEPT003", "department": "Accounts"},
    {"department_id": "DEPT004", "department": "Warehouse"},
]

DEMO_MASTERS = [
    {
        "code": "DEBTO001", "name": "Al-Rashid Trading LLC",
        "opening_balance": 15000.0, "debit": 45000.0, "credit": 30000.0,
        "place": "Kozhikode", "phone": "9876543210", "phone2": "0495-1234567",
        "openingdepartment": "DEPT001", "area": "North Zone", "super_code": "DEBTO",
        "address": "MG Road, Kozhikode", "city": "Kozhikode",
        "gstin": "32AABCT1332L1ZU", "remarkcolumntitle": "Invoice No",
    },
    {
        "code": "DEBTO002", "name": "Malabar Enterprises",
        "opening_balance": 8500.0, "debit": 22000.0, "credit": 13500.0,
        "place": "Calicut", "phone": "9745123456", "phone2": "",
        "openingdepartment": "DEPT002", "area": "South Zone", "super_code": "DEBTO",
        "address": "Beach Road, Calicut", "city": "Calicut",
        "gstin": "32BBBCT2441L1ZV", "remarkcolumntitle": "Bill No",
    },
]

DEMO_PRODUCTS = [
    {
        "code": "PRD001", "name": "Basmati Rice 1kg",
        "size": "1kg", "sub_category": "Rice", "unit": "KG",
        "taxcode": "GST5", "company": "Malabar", "product": "Rice",
        "brand": "India Gate", "text6": "", "nameinsl": "Basmati Rice 1kg",
    },
    {
        "code": "PRD002", "name": "Sunflower Oil 1L",
        "size": "1L", "sub_category": "Oils", "unit": "LTR",
        "taxcode": "GST5", "company": "Fortune", "product": "Oil",
        "brand": "Fortune", "text6": "", "nameinsl": "Sunflower Oil 1L",
    },
]

DEMO_BATCHES = [
    {
        "product_code": "PRD001", "barcode": "8901234567890",
        "salesprice": 95.0, "secondprice": 92.0, "thirdprice": 90.0,
        "fourthprice": 88.0, "nlc1": 80.0, "quantity": 100.0, "bmrp": 100.0,
    },
    {
        "product_code": "PRD002", "barcode": "8901234567891",
        "salesprice": 140.0, "secondprice": 135.0, "thirdprice": 132.0,
        "fourthprice": 130.0, "nlc1": 120.0, "quantity": 50.0, "bmrp": 150.0,
    },
]


def is_demo_mode() -> bool:
    return getattr(settings, 'DB_DEMO_MODE', False)


# ── Departments ───────────────────────────────────────────────────────────

class DepartmentListView(APIView):
    """
    GET  /api/departments/  → list all departments
    POST /api/departments/  → create or update a department
    """

    def get(self, request):
        if is_demo_mode():
            serializer = DepartmentSerializer(DEMO_DEPARTMENTS, many=True)
            return Response({"count": len(DEMO_DEPARTMENTS), "results": serializer.data})

        try:
            depts      = Department.objects.all()
            serializer = DepartmentSerializer(depts, many=True)
            return Response({"count": depts.count(), "results": serializer.data})
        except Exception as e:
            logger.exception("DepartmentListView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dept_id    = serializer.validated_data["department_id"]
        department = serializer.validated_data["department"]

        if is_demo_mode():
            existing = next((d for d in DEMO_DEPARTMENTS if d["department_id"] == dept_id), None)
            if existing:
                existing["department"] = department
                return Response({"message": "updated", "data": serializer.data}, status=status.HTTP_200_OK)
            DEMO_DEPARTMENTS.append(dict(serializer.validated_data))
            return Response({"message": "created", "data": serializer.data}, status=status.HTTP_201_CREATED)

        try:
            obj, created = Department.objects.update_or_create(
                department_id=dept_id,
                defaults={"department": department},
            )
            msg         = "created" if created else "updated"
            http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response({"message": msg, "data": DepartmentSerializer(obj).data}, status=http_status)
        except Exception as e:
            logger.exception("DepartmentListView.post failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentDetailView(APIView):
    """
    GET /api/departments/<department_id>/  → get one department
    """

    def get(self, request, department_id):
        if is_demo_mode():
            dept = next((d for d in DEMO_DEPARTMENTS if d["department_id"] == department_id), None)
            if not dept:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(DepartmentSerializer(dept).data)

        try:
            dept = Department.objects.get(department_id=department_id)
            return Response(DepartmentSerializer(dept).data)
        except Department.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("DepartmentDetailView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Debtors ───────────────────────────────────────────────────────────────

class DebtorListView(APIView):
    """
    GET  /api/debtors/  → list all debtors (super_code = DEBTO)
    POST /api/debtors/  → create or update a debtor
    """

    def get(self, request):
        if is_demo_mode():
            serializer = DebtorSerializer(DEMO_MASTERS, many=True)
            return Response({"count": len(DEMO_MASTERS), "results": serializer.data})

        try:
            debtors    = Debtor.objects.filter(super_code='DEBTO')
            serializer = DebtorSerializer(debtors, many=True)
            return Response({"count": debtors.count(), "results": serializer.data})
        except Exception as e:
            logger.exception("DebtorListView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = DebtorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fields = serializer.validated_data
        code   = fields["code"]

        if is_demo_mode():
            existing = next((x for x in DEMO_MASTERS if x["code"] == code), None)
            if existing:
                existing.update(fields)
                return Response({"message": "updated", "data": serializer.data}, status=status.HTTP_200_OK)
            DEMO_MASTERS.append(dict(fields))
            return Response({"message": "created", "data": serializer.data}, status=status.HTTP_201_CREATED)

        try:
            obj, created = Debtor.objects.update_or_create(
                code=code,
                defaults={k: v for k, v in fields.items() if k != "code"},
            )
            msg         = "created" if created else "updated"
            http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response({"message": msg, "data": DebtorSerializer(obj).data}, status=http_status)
        except Exception as e:
            logger.exception("DebtorListView.post failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebtorDetailView(APIView):
    """
    GET /api/debtors/<code>/  → get one debtor by code
    """

    def get(self, request, code):
        if is_demo_mode():
            debtor = next((d for d in DEMO_MASTERS if d["code"] == code), None)
            if not debtor:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(DebtorSerializer(debtor).data)

        try:
            debtor = Debtor.objects.get(code=code, super_code='DEBTO')
            return Response(DebtorSerializer(debtor).data)
        except Debtor.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("DebtorDetailView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Products ──────────────────────────────────────────────────────────────

class ProductListView(APIView):
    """
    GET  /api/products/  → list all products
    POST /api/products/  → create or update a product
    """

    def get(self, request):
        if is_demo_mode():
            serializer = ProductSerializer(DEMO_PRODUCTS, many=True)
            return Response({"count": len(DEMO_PRODUCTS), "results": serializer.data})

        try:
            products   = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response({"count": products.count(), "results": serializer.data})
        except Exception as e:
            logger.exception("ProductListView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fields = serializer.validated_data
        code   = fields["code"]

        if is_demo_mode():
            existing = next((p for p in DEMO_PRODUCTS if p["code"] == code), None)
            if existing:
                existing.update(fields)
                return Response({"message": "updated", "data": serializer.data}, status=status.HTTP_200_OK)
            DEMO_PRODUCTS.append(dict(fields))
            return Response({"message": "created", "data": serializer.data}, status=status.HTTP_201_CREATED)

        try:
            obj, created = Product.objects.update_or_create(
                code=code,
                defaults={k: v for k, v in fields.items() if k != "code"},
            )
            msg         = "created" if created else "updated"
            http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response({"message": msg, "data": ProductSerializer(obj).data}, status=http_status)
        except Exception as e:
            logger.exception("ProductListView.post failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailView(APIView):
    """
    GET /api/products/<code>/  → get one product by code
    """

    def get(self, request, code):
        if is_demo_mode():
            product = next((p for p in DEMO_PRODUCTS if p["code"] == code), None)
            if not product:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(ProductSerializer(product).data)

        try:
            product = Product.objects.get(code=code)
            return Response(ProductSerializer(product).data)
        except Product.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ProductDetailView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Product Batches ───────────────────────────────────────────────────────

class ProductBatchListView(APIView):
    """
    GET  /api/productbatches/          → list all batches (?product=<code> to filter)
    POST /api/productbatches/          → create a batch
    """

    def get(self, request):
        if is_demo_mode():
            product_filter = request.query_params.get("product")
            data = [b for b in DEMO_BATCHES if not product_filter or b["product_code"] == product_filter]
            serializer = ProductBatchSerializer(data, many=True)
            return Response({"count": len(data), "results": serializer.data})

        try:
            qs             = ProductBatch.objects.all()
            product_filter = request.query_params.get("product")
            if product_filter:
                qs = qs.filter(product_id=product_filter)
            serializer = ProductBatchSerializer(qs, many=True)
            return Response({"count": qs.count(), "results": serializer.data})
        except Exception as e:
            logger.exception("ProductBatchListView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = ProductBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = serializer.save()
            return Response(
                {"message": "created", "data": ProductBatchSerializer(obj).data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.exception("ProductBatchListView.post failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductBatchDetailView(APIView):
    """
    GET /api/productbatches/<product_code>/  → get one batch by product code
    """

    def get(self, request, product_code):
        if is_demo_mode():
            batch = next((b for b in DEMO_BATCHES if b["product_code"] == product_code), None)
            if not batch:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(ProductBatchSerializer(batch).data)

        try:
            batch = ProductBatch.objects.get(product_id=product_code)
            return Response(ProductBatchSerializer(batch).data)
        except ProductBatch.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ProductBatchDetailView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Combined Sync ─────────────────────────────────────────────────────────

class SyncView(APIView):
    """
    GET /api/sync/  → returns departments, debtors, products and batches in one response.
    Used by sync.py pull mode and the Test API button.
    """

    def get(self, request):
        if is_demo_mode():
            return Response({
                "departments": {
                    "count":   len(DEMO_DEPARTMENTS),
                    "results": DepartmentSerializer(DEMO_DEPARTMENTS, many=True).data,
                },
                "debtors": {
                    "count":   len(DEMO_MASTERS),
                    "results": DebtorSerializer(DEMO_MASTERS, many=True).data,
                },
                "products": {
                    "count":   len(DEMO_PRODUCTS),
                    "results": ProductSerializer(DEMO_PRODUCTS, many=True).data,
                },
                "productbatches": {
                    "count":   len(DEMO_BATCHES),
                    "results": ProductBatchSerializer(DEMO_BATCHES, many=True).data,
                },
            })

        try:
            depts    = Department.objects.all()
            debtors  = Debtor.objects.filter(super_code='DEBTO')
            products = Product.objects.all()
            batches  = ProductBatch.objects.all()

            return Response({
                "departments": {
                    "count":   depts.count(),
                    "results": DepartmentSerializer(depts, many=True).data,
                },
                "debtors": {
                    "count":   debtors.count(),
                    "results": DebtorSerializer(debtors, many=True).data,
                },
                "products": {
                    "count":   products.count(),
                    "results": ProductSerializer(products, many=True).data,
                },
                "productbatches": {
                    "count":   batches.count(),
                    "results": ProductBatchSerializer(batches, many=True).data,
                },
            })
        except Exception as e:
            logger.exception("SyncView.get failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Bulk upsert endpoints ─────────────────────────────────────────────────

class DepartmentBulkView(APIView):
    """POST /api/departments/bulk/ — upsert a list of departments at once."""

    def post(self, request):
        records = request.data
        if not isinstance(records, list):
            return Response({"error": "Expected a JSON array"}, status=status.HTTP_400_BAD_REQUEST)

        created = updated = errors = 0
        for item in records:
            dept_id = item.get("department_id", "")
            dept    = item.get("department", "")
            if not dept_id:
                errors += 1
                continue
            try:
                _, was_created = Department.objects.update_or_create(
                    department_id=dept_id,
                    defaults={"department": dept},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception:
                logger.exception(f"DepartmentBulkView error for {dept_id}")
                errors += 1

        return Response({"created": created, "updated": updated, "errors": errors})


class DebtorBulkView(APIView):
    """POST /api/debtors/bulk/ — upsert a list of debtors at once."""

    STR_FIELDS = {
        "place", "phone", "phone2", "openingdepartment",
        "area", "address", "city", "gstin", "remarkcolumntitle",
    }
    ALL_FIELDS = [
        "name", "opening_balance", "debit", "credit",
        "place", "phone", "phone2", "openingdepartment", "area",
        "super_code", "address", "city", "gstin", "remarkcolumntitle",
    ]

    def post(self, request):
        records = request.data
        if not isinstance(records, list):
            return Response({"error": "Expected a JSON array"}, status=status.HTTP_400_BAD_REQUEST)

        to_create = []
        to_update = []
        existing_codes = set(
            Debtor.objects.filter(
                code__in=[r.get("code") for r in records if r.get("code")]
            ).values_list("code", flat=True)
        )

        errors = 0
        for item in records:
            code = item.get("code", "")
            if not code:
                errors += 1
                continue
            defaults = {}
            for field in self.ALL_FIELDS:
                val = item.get(field)
                if val is None and field in self.STR_FIELDS:
                    val = ""
                defaults[field] = val

            obj = Debtor(code=code, **defaults)
            if code in existing_codes:
                to_update.append(obj)
            else:
                to_create.append(obj)

        created = updated = 0
        try:
            if to_create:
                Debtor.objects.bulk_create(to_create, ignore_conflicts=True)
                created = len(to_create)
            if to_update:
                Debtor.objects.bulk_update(to_update, self.ALL_FIELDS)
                updated = len(to_update)
        except Exception as e:
            logger.exception("DebtorBulkView bulk operation failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"created": created, "updated": updated, "errors": errors})


class ProductBulkView(APIView):
    """POST /api/products/bulk/ — upsert a list of products at once."""

    STR_FIELDS  = {
        'name', 'size', 'sub_category', 'unit', 'taxcode',
        'company', 'product', 'brand', 'text6', 'nameinsl',
    }
    ALL_FIELDS = [
        'name', 'size', 'sub_category', 'unit', 'taxcode',
        'company', 'product', 'brand', 'text6', 'nameinsl',
    ]

    def post(self, request):
        records = request.data
        if not isinstance(records, list):
            return Response({"error": "Expected a JSON array"}, status=status.HTTP_400_BAD_REQUEST)

        existing_codes = set(
            Product.objects.filter(
                code__in=[r.get("code") for r in records if r.get("code")]
            ).values_list("code", flat=True)
        )

        to_create, to_update, errors = [], [], 0
        for item in records:
            code = item.get("code", "")
            if not code:
                errors += 1
                continue
            defaults = {}
            for field in self.ALL_FIELDS:
                val = item.get(field)
                if val is None and field in self.STR_FIELDS:
                    val = ""
                defaults[field] = val

            obj = Product(code=code, **defaults)
            (to_update if code in existing_codes else to_create).append(obj)

        try:
            if to_create:
                Product.objects.bulk_create(to_create, ignore_conflicts=True)
            if to_update:
                Product.objects.bulk_update(to_update, self.ALL_FIELDS)
        except Exception as e:
            logger.exception("ProductBulkView bulk operation failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"created": len(to_create), "updated": len(to_update), "errors": errors})


class ProductBatchBulkView(APIView):
    """POST /api/productbatches/bulk/ — upsert batches keyed on product_code.

    One batch row per product. If the source has several batch rows for a
    product, the last one received wins (sync.py orders by slno, so the most
    recent batch is kept). One existence-lookup query plus
    bulk_create/bulk_update.
    """

    ALL_FIELDS = [
        'barcode', 'salesprice', 'secondprice', 'thirdprice', 'fourthprice',
        'nlc1', 'quantity', 'bmrp',
    ]
    STR_FIELDS = {'barcode'}

    def post(self, request):
        records = request.data
        if not isinstance(records, list):
            return Response({"error": "Expected a JSON array"}, status=status.HTTP_400_BAD_REQUEST)

        valid_records = []
        errors = 0
        for item in records:
            if not item.get("product_code"):
                errors += 1
                continue
            valid_records.append(item)

        # Collapse duplicate product_code within this chunk — last one wins.
        deduped = {}
        for item in valid_records:
            deduped[item["product_code"]] = item
        valid_records = list(deduped.values())

        # One query to find which product_code values already exist
        codes = [r["product_code"] for r in valid_records]
        existing = set(
            ProductBatch.objects.filter(product_id__in=codes).values_list("product_id", flat=True)
        )

        to_create, to_update = [], []
        for item in valid_records:
            product_code = item["product_code"]
            defaults     = {}
            for f in self.ALL_FIELDS:
                val = item.get(f)
                if val is None and f in self.STR_FIELDS:
                    val = ""
                defaults[f] = val

            obj = ProductBatch(product_id=product_code, **defaults)
            (to_update if product_code in existing else to_create).append(obj)

        created = updated = 0
        try:
            if to_create:
                ProductBatch.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=500)
                created = len(to_create)
            if to_update:
                ProductBatch.objects.bulk_update(to_update, self.ALL_FIELDS, batch_size=500)
                updated = len(to_update)
        except Exception as e:
            logger.exception("ProductBatchBulkView bulk operation failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"created": created, "updated": updated, "errors": errors})


# ── Reset / Truncate ──────────────────────────────────────────────────────

class ResetView(APIView):
    """DELETE /api/reset/ — wipe all departments, debtors, products and batches for a clean sync."""

    def delete(self, request):
        if is_demo_mode():
            DEMO_DEPARTMENTS.clear()
            DEMO_MASTERS.clear()
            DEMO_PRODUCTS.clear()
            DEMO_BATCHES.clear()
            return Response({
                "departments_deleted": 0, "debtors_deleted": 0,
                "products_deleted": 0, "productbatches_deleted": 0,
            })
        try:
            # Batches must be deleted before products (FK constraint)
            b = ProductBatch.objects.all().delete()[0]
            p = Product.objects.all().delete()[0]
            d = Department.objects.all().delete()[0]
            m = Debtor.objects.all().delete()[0]
            logger.info(f"Reset: {d} depts, {m} debtors, {p} products, {b} batches deleted")
            return Response({
                "departments_deleted":    d,
                "debtors_deleted":        m,
                "products_deleted":       p,
                "productbatches_deleted": b,
            })
        except Exception as e:
            logger.exception("ResetView.delete failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)