from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ProjectSite, PlantationRecord, CarbonCredit

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'organization', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'organization')}),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(ProjectSite)
class ProjectSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'ecosystem_type', 'area_ha', 'created_by', 'created_date')
    list_filter = ('ecosystem_type', 'created_date')
    search_fields = ('name', 'created_by__username')

@admin.register(PlantationRecord)
class PlantationRecordAdmin(admin.ModelAdmin):
    list_display = ('species', 'project_site', 'number_of_plants', 'verified', 'upload_date')
    list_filter = ('verified', 'date_planted', 'project_site__ecosystem_type')
    search_fields = ('species', 'project_site__name')

@admin.register(CarbonCredit)
class CarbonCreditAdmin(admin.ModelAdmin):
    list_display = ('project_site', 'credits_issued', 'year', 'txn_hash', 'issued_date')
    list_filter = ('year', 'issued_date')
    search_fields = ('project_site__name', 'txn_hash')
    readonly_fields = ('txn_hash',)