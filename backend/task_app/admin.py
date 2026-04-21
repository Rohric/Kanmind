from django.contrib import admin
from .models import Task, Comment

# Register your models here.


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0  # Verhindert, dass standardmäßig leere Formulare angezeigt werden
    readonly_fields = ('user', 'created_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status",
                    "due_date", "priority", "assignee", "reviewer", "creator",)
    search_fields = ("title",)
    list_filter = ("status", "priority", "board")
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'task', 'user', 'created_at')
    list_filter = ('user', 'task')
    search_fields = ('content',)
