from django.contrib import admin 
from app.models import * 

admin.site.register(AppUser)
admin.site.register(Designation)
admin.site.register(Group)
admin.site.register(Category)
admin.site.register(PDFfiles)
admin.site.register(Notification_db)
admin.site.register(Apps_db)

admin.site.register(Forms_db)