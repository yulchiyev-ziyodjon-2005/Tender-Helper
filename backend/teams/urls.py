from django.urls import path

from . import views

app_name = 'teams'

urlpatterns = [
    path('workspace/', views.workspace_view, name='workspace'),
    path('members/', views.members_view, name='members'),
    path('members/<uuid:pk>/', views.member_detail_view, name='member-detail'),
    path(
        'members/<uuid:pk>/revoke-sessions/',
        views.revoke_member_sessions_view,
        name='member-revoke-sessions',
    ),
]
