from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# Register your models here.
from .models import MasterUser, MasterBelanja, MasterPendapatan, RencanaAnggaranBelanja, Anggaran, TransaksiBelanja
class MasterUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'fullname', 'nomortelephone', 'role', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'fullname', 'nomortelephone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'fullname', 'nomortelephone', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'fullname', 'nomortelephone')
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(MasterUser, MasterUserAdmin)
admin.site.unregister(Group)
admin.site.register(MasterBelanja)
admin.site.register(MasterPendapatan)
admin.site.register(RencanaAnggaranBelanja)
admin.site.register(Anggaran)
admin.site.register(TransaksiBelanja)