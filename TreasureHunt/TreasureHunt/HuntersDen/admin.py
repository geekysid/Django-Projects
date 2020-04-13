from django.contrib import admin
from .models import *

admin.site.site_header = "GeekySid Dashboard"


class RiddleCategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_id', 'name', 'desc')
    ordering = ('name',)
    search_fields = ('name', 'desc')


class RiddleLevelAdmin(admin.ModelAdmin):
    list_display = ('level_id', 'name', 'short_name', 'desc', 'positive_score_percent', 'negetive_score_percent')
    ordering = ('name', 'positive_score_percent', 'negetive_score_percent',)
    search_fields = ('name', 'desc')


class RiddleTypeAdmin(admin.ModelAdmin):
    list_display = ('type_id', 'name')
    ordering = ('name',)


class RiddleAdmin(admin.ModelAdmin):
    list_display = ('riddle_id', 'category', 'riddle_level', 'type_riddle', 'media', 'uin_code', 'question', 'answer_1', 'answer_2', 'answer_3', 'answer_4', 'answer_5', 'answer_6', 'answer_7', 'answer_8', 'answer_9', 'point', 'hint', 'answer_format')
    list_filter = ('category', 'riddle_level', 'type_riddle')
    ordering = ('category', 'riddle_level', 'type_riddle', 'question',)
    ordering = ('category', 'riddle_level', 'type_riddle', 'question')


class DenAdmin(admin.ModelAdmin):
    list_display = ('den_id', 'name', 'admin', 'desc', 'avatar', 'uin_code', 'score', 'riddle_start_time', 'riddles_per_day', 'time_bw_riddle', 'is_active', 'started_at', 'ended_at', 'invitation_code')
    list_filter = ('admin', 'name', 'is_active')
    ordering = ('name', 'score', 'is_active', 'started_at', 'ended_at', 'invitation_code')
    search_fields = ('name', 'desc', 'uin_code')


class DenInviteeAdmin(admin.ModelAdmin):
    list_display = ('invitee', 'email_to', 'den', 'invite_code', 'sent_on', 'accepted_on', 'status')
    list_filter = ('invitee', 'den', 'status')
    ordering = ('invitee', 'email_to', 'den', 'invite_code', 'sent_on')
    search_fields = ('invitee', 'email_to', 'status', 'invite_code')


class Hunter_Den_MappingAdmin(admin.ModelAdmin):
    list_display = ('map_id', 'den', 'hunter', 'member_status', 'invitation_code')
    list_filter = ('den', 'hunter')
    ordering = ('den',)
    search_fields = ('den', 'hunter')


class DenRiddleAdmin(admin.ModelAdmin):
    list_display = ('den_riddle_id', 'den', 'riddle', 'uin_code', 'added_at', 'started_at', 'ending_at', 'is_pending', 'is_active', 'has_expired')
    list_filter = ('den', 'riddle', 'is_pending', 'is_active', 'has_expired')
    ordering = ('den', 'riddle', 'started_at', 'ending_at',)
    search_fields = ('den', 'riddle', 'uin_code', 'is_pending', 'is_active', 'has_expired')


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('response_id', 'den_riddle', 'hunter', 'answer', 'image', 'is_correct', 'score',                        'response_at', 'response_time')
    list_filter = ('hunter', 'is_correct', 'score')
    ordering = ('hunter', 'answer', 'score', 'response_at', 'response_time')
    search_fields = ('hunter', 'answer', 'score', )


class ResponseImageAdmin(admin.ModelAdmin):
    list_display = ('response', 'image')
    ordering = ('response',)


# Register your models here.
admin.site.register(RiddleCategory, RiddleCategoryAdmin)
admin.site.register(RiddleLevel, RiddleLevelAdmin)
admin.site.register(RiddleType, RiddleTypeAdmin)
admin.site.register(Riddle, RiddleAdmin)
admin.site.register(Den, DenAdmin) 
admin.site.register(Hunter_Den_Mapping, Hunter_Den_MappingAdmin)
admin.site.register(DenRiddle, DenRiddleAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(ResponseImage, ResponseImageAdmin)
admin.site.register(DenInvitee, DenInviteeAdmin)