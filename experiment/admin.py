from django.contrib import admin
from .models import Classification, Participant, PaymentCode, Block
# Register your models here.

class ClassificationAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Session/Classification", { "fields": ["session", "classification"]}),
        ("Alarm", {"fields": ["alarm"]}),
        ("Time", {"fields": ["time"]})
    ]


class ParticipantAdmin(admin.ModelAdmin):
    fieldsets = [
        ("ID", {"fields": ["user_id"]}),
        ("Name", { "fields": ["name"]}),
        ("Email", {"fields": ["email"]}),
        ("Condition", {"fields": ["condition"]})
    ]


class PaymentCodeAdmin(admin.ModelAdmin):
    fieldsets = [
        ("ID", {"fields": ["user_id"]}),
        ("Name", { "fields": ["name"]}),
        ("Email", {"fields": ["email"]}),
        ("Condition", {"fields": ["condition"]}),
        ("Code", {"fields": ["code"]})
    ]

class BlocksAdmin(admin.ModelAdmin):
    fieldsets = [
        ("ID", {"fields": ["user_id"]}),
        ("Block", { "fields": ["block"]}),
        ("Score", {"fields": ["score"]}),
        ("System", {"fields": ["alert_system"]}),
        ("Condition", {"fields": ["condition"]})
    ]


admin.site.register(Participant)
admin.site.register(Classification)
admin.site.register(PaymentCode)
admin.site.register(Block)


