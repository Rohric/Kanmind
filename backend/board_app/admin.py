from django.contrib import admin
from . models import Board, BoardMembership
from task_app.models import Task
# Register your models here


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0  # Verhindert, dass standardmäßig leere Formulare angezeigt werden
    fields = ('title', 'status', 'priority', 'assignee', 'due_date')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner")
    list_filter = ("owner",)
    search_fields = ("title",)
    inlines = [TaskInline]


@admin.register(BoardMembership)
class BoardMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'board', 'role', 'joined_at')
    list_filter = ('user', 'board')
    search_fields = ('user__username', 'board__title')
