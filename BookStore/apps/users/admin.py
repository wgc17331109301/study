from django.contrib import admin
from users.models import user_info, verify_code, user_token


@admin.register(user_info)
class user_info_Admin(admin.ModelAdmin):
    pass


@admin.register(verify_code)
class verify_code_Admin(admin.ModelAdmin):
    pass


@admin.register(user_token)
class user_token_Admin(admin.ModelAdmin):
    pass
