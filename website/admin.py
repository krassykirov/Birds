from django.contrib import admin
from django.contrib.auth.admin import User, UserAdmin
from .models import Bird,BirdImage,BirdCategory,BirdSong,BirdUser


class CustomUserAdmin(UserAdmin):
    model = BirdUser
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Bird)
admin.site.register(BirdImage)
admin.site.register(BirdCategory)
admin.site.register(BirdSong)
admin.site.register(BirdUser)
admin.site.register(User, CustomUserAdmin)