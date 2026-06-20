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

    GET  /api/products/                     → list all products
    POST /api/products/                     → create / update a product
    GET  /api/products/<code>/              → get one product

    GET  /api/productbatches/               → list all batches (?product=<code> to filter)
    POST /api/productbatches/               → create a batch
    GET  /api/productbatches/<product_code>/ → get one batch

    GET  /api/sync/                         → combined pull (all four tables)
    DELETE /api/reset/                      → wipe all data for a clean sync
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

    path('api/products/bulk/',
         views.ProductBulkView.as_view(),
         name='product-bulk'),

    path('api/productbatches/bulk/',
         views.ProductBatchBulkView.as_view(),
         name='productbatch-bulk'),

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

    # ── Products ──────────────────────────────────────────────────────────
    path('api/products/',
         views.ProductListView.as_view(),
         name='product-list'),

    path('api/products/<str:code>/',
         views.ProductDetailView.as_view(),
         name='product-detail'),

    # ── Product Batches ───────────────────────────────────────────────────
    path('api/productbatches/',
         views.ProductBatchListView.as_view(),
         name='productbatch-list'),

    path('api/productbatches/<str:product_code>/',
         views.ProductBatchDetailView.as_view(),
         name='productbatch-detail'),

    # ── Combined sync ─────────────────────────────────────────────────────
    path('api/sync/',
         views.SyncView.as_view(),
         name='sync'),
]