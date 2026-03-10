from django.contrib import admin
from .models import OMRResult, DebugResult, DSAResult, FinalResult

admin.site.register(OMRResult)
admin.site.register(DebugResult)
admin.site.register(DSAResult)
admin.site.register(FinalResult)
