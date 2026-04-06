"""
urls.py  ─  API app URL patterns
=================================
Place this file at:  FLASH_ERP_API/api/urls.py

Endpoints:
    GET  /api/departments/                  → list all departments
    POST /api/departments/                  → create / update a department
    GET  /api/departments/<department_id>/  → get one department

    GET  /api/debtors/                      → list all debtors (super_code = DEBTO)
    POST /api/debtors/                      → create / update a debtor
    GET  /api/debtors/<code>/               → get one debtor

    GET  /api/sync/                         → combined pull (departments + debtors)
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Bulk upsert (must come BEFORE detail routes) ──────────────────────
    path('api/departments/bulk/',
         views.DepartmentBulkView.as_view(),
         name='department-bulk'),

    path('api/debtors/bulk/',
         views.DebtorBulkView.as_view(),
         name='debtor-bulk'),

    # ── Reset / Truncate ──────────────────────────────────────────────────
    path('api/reset/',
         views.ResetView.as_view(),
         name='reset'),

    # ── Departments ───────────────────────────────────────────────────────
    path('api/departments/',
         views.DepartmentListView.as_view(),
         name='department-list'),

    path('api/departments/<str:department_id>/',
         views.DepartmentDetailView.as_view(),
         name='department-detail'),

    # ── Debtors ───────────────────────────────────────────────────────────
    path('api/debtors/',
         views.DebtorListView.as_view(),
         name='debtor-list'),

    path('api/debtors/<str:code>/',
         views.DebtorDetailView.as_view(),
         name='debtor-detail'),

    # ── Combined sync ─────────────────────────────────────────────────────
    path('api/sync/',
         views.SyncView.as_view(),
         name='sync'),
]