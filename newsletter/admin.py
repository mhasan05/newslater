from django.contrib import admin
from .models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        # Prevent manual addition since emails are added via the form
        return False
