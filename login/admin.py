from django.contrib import admin
from .models import User, ConfirmString

admin.site.register(User)
admin.site.register(ConfirmString)