from django.contrib import admin

from .models import Company, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'created_at',
    )
    search_fields = (
        'name',
    )
    ordering = (
        'name',
    )
    readonly_fields = (
        'created_at',
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'company',
        'company_name',
        'industry_sector',
        'plan_type',
        'created_at',
    )
    list_filter = (
        'plan_type',
        'company',
    )
    search_fields = (
        'user__username',
        'user__email',
        'company__name',
        'company_name',
        'industry_sector',
    )
    readonly_fields = (
        'uid',
        'created_at',
    )