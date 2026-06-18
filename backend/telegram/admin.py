from django.contrib import admin

from .models import (
    NotificationDelivery,
    NotificationPreference,
    TelegramIdentity,
    TelegramLinkChallenge,
    TelegramMiniAppSession,
)


admin.site.register(TelegramIdentity)
admin.site.register(TelegramLinkChallenge)
admin.site.register(TelegramMiniAppSession)
admin.site.register(NotificationPreference)
admin.site.register(NotificationDelivery)
