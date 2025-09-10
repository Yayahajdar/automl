from django.contrib import admin

from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email', 'message')
