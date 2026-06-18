from django.urls import path

from competitors import views

app_name = 'competitors'

urlpatterns = [
    path('top/', views.top_competitors_view, name='top'),
    path('freshness/', views.competitor_freshness_view, name='freshness'),
    path(
        '<str:stir>/history/',
        views.competitor_history_view,
        name='history',
    ),
]
