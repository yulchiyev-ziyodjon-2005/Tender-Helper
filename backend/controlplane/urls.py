from django.urls import path

from controlplane import views

app_name = 'controlplane'

urlpatterns = [
    path('auth/step-up/', views.AdminStepUpView.as_view(), name='step-up'),
    path('overview/', views.OverviewView.as_view(), name='overview'),
    path('search/', views.AdminGlobalSearchView.as_view(), name='search'),
    path('users/', views.AdminUserListView.as_view(), name='users'),
    path(
        'users/<uuid:user_id>/',
        views.AdminUserDetailView.as_view(),
        name='user-detail',
    ),
    path(
        'users/<uuid:user_id>/action/',
        views.UserActionView.as_view(),
        name='user-action',
    ),
    path(
        'users/<uuid:user_id>/reveal/',
        views.UserRevealView.as_view(),
        name='user-reveal',
    ),
    path(
        'users/<uuid:user_id>/export/',
        views.UserPIIExportView.as_view(),
        name='user-export',
    ),
    path('companies/', views.AdminCompanyListView.as_view(), name='companies'),
    path(
        'companies/<uuid:company_id>/',
        views.AdminCompanyDetailView.as_view(),
        name='company-detail',
    ),
    path(
        'companies/<uuid:company_id>/entitlements/',
        views.CompanyEntitlementPreviewView.as_view(),
        name='company-entitlements',
    ),
    path('plans/', views.PlanListView.as_view(), name='plans'),
    path(
        'plans/<slug:plan_code>/preview/',
        views.PlanPreviewView.as_view(),
        name='plan-preview',
    ),
    path(
        'plans/<slug:plan_code>/',
        views.PlanUpdateView.as_view(),
        name='plan-update',
    ),
    path(
        'subscriptions/',
        views.SubscriptionListView.as_view(),
        name='subscriptions',
    ),
    path(
        'subscriptions/<uuid:company_id>/preview/',
        views.SubscriptionActionPreviewView.as_view(),
        name='subscription-preview',
    ),
    path(
        'subscriptions/<uuid:company_id>/action/',
        views.SubscriptionActionView.as_view(),
        name='subscription-action',
    ),
    path('payments/', views.PaymentListView.as_view(), name='payments'),
    path('operations/', views.OperationsView.as_view(), name='operations'),
    path(
        'operations/features/<str:feature>/',
        views.FeatureFlagActionView.as_view(),
        name='feature-flag-action',
    ),
    path(
        'operations/maintenance-banner/',
        views.MaintenanceBannerActionView.as_view(),
        name='maintenance-banner-action',
    ),
    path(
        'operations/templates/<uuid:template_id>/',
        views.TemplatePublishActionView.as_view(),
        name='template-action',
    ),
    path('audit/', views.AuditListView.as_view(), name='audit'),
    path('audit/export/', views.AuditExportView.as_view(), name='audit-export'),
    path(
        'principals/<uuid:user_id>/',
        views.CapabilityAssignmentView.as_view(),
        name='principal-action',
    ),
]
