from django.contrib import admin
from .models import CustomerMessages, InternalCommunicationNotes


class InternalCommunicationNotesAdmin(admin.StackedInline):
    """
    Internal notes for staff when replying to customers
    messages via email
    """

    model = InternalCommunicationNotes
    extra = 1
    verbose_name_plural = 'Internal Communication Notes'
    verbose_name = 'Internal Communication Note'
    fields = ('notes', 'date',)
    readonly_fields = ('date',)
    can_delete = False


@admin.register(CustomerMessages)
class CustomerMessagesAdmin(admin.ModelAdmin):
    """
    Allows staff to view/filter customer messages
    but prevents the content being changed
    """

    inlines = (InternalCommunicationNotesAdmin,)
    baseModel = CustomerMessages
    list_display = (
        'date_received',
        'name',
        'email',
        'phone_number',
        'pending_reply',
        'marked_as_done',
    )
    list_filter = ('pending_reply', 'marked_as_done', 'date_received')
    search_fields = ('name', 'email', 'phone_number', 'address',)
    summer_note_field = ('address',)
    readonly_fields = ('date_received', 'address',)

    ordering = ('-date_received',)
