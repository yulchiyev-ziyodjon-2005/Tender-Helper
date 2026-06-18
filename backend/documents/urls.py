from django.urls import path

from documents import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list_view, name='list'),
    path('templates/', views.template_list_view, name='templates'),
    path('generate/', views.generate_document_view, name='generate'),
    path('<uuid:pk>/', views.document_detail_view, name='detail'),
    path('<uuid:pk>/approve/', views.approve_document_view, name='approve'),
    path('<uuid:pk>/archive/', views.archive_document_view, name='archive'),
    path('<uuid:pk>/export/', views.export_document_view, name='export'),
    path('<uuid:pk>/versions/', views.document_versions_view, name='versions'),
    path('exports/<uuid:pk>/', views.export_status_view, name='export-status'),
    path(
        'exports/<uuid:pk>/download/',
        views.export_download_view,
        name='export-download',
    ),
]
