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

from .models import Department, Debtor
from .serializers import DepartmentSerializer, DebtorSerializer

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


# ── Combined Sync ─────────────────────────────────────────────────────────

class SyncView(APIView):
    """
    GET /api/sync/  → returns both departments and debtors in one response.
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
            })

        try:
            depts   = Department.objects.all()
            debtors = Debtor.objects.filter(super_code='DEBTO')

            return Response({
                "departments": {
                    "count":   depts.count(),
                    "results": DepartmentSerializer(depts, many=True).data,
                },
                "debtors": {
                    "count":   debtors.count(),
                    "results": DebtorSerializer(debtors, many=True).data,
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

        # Build list of Debtor objects for bulk_create / bulk_update
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
        update_fields = self.ALL_FIELDS

        try:
            if to_create:
                Debtor.objects.bulk_create(to_create, ignore_conflicts=True)
                created = len(to_create)
            if to_update:
                Debtor.objects.bulk_update(to_update, update_fields)
                updated = len(to_update)
        except Exception as e:
            logger.exception("DebtorBulkView bulk operation failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"created": created, "updated": updated, "errors": errors})


# ── Reset / Truncate ──────────────────────────────────────────────────────

class ResetView(APIView):
    """DELETE /api/reset/ — wipe all departments and debtors for a clean sync."""

    def delete(self, request):
        if is_demo_mode():
            DEMO_DEPARTMENTS.clear()
            DEMO_MASTERS.clear()
            return Response({"departments_deleted": 0, "debtors_deleted": 0})
        try:
            d = Department.objects.all().delete()[0]
            m = Debtor.objects.all().delete()[0]
            logger.info(f"Reset: {d} depts, {m} debtors deleted")
            return Response({"departments_deleted": d, "debtors_deleted": m})
        except Exception as e:
            logger.exception("ResetView.delete failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)