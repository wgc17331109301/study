from django.contrib import admin
from user_options.models import user_leave_message, user_address


admin.site.site_title = '二手书商城'
admin.site.site_header = '二手书商城'
admin.site.index_title = '二手书商城'


@admin.register(user_leave_message)
class user_leave_message_Admin(admin.ModelAdmin):
    pass


@admin.register(user_address)
class user_address_Admin(admin.ModelAdmin):
    pass
