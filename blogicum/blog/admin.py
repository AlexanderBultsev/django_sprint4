from django.contrib import admin
from django.template.defaultfilters import truncatechars

from .models import Category, Location, Post


def trunc_text(self):
    return truncatechars(self.text, 30)


trunc_text.short_description = 'Текст'


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        trunc_text,
        'pub_date',
        'author',
        'category',
        'is_published',
    )
    list_editable = (
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('author', 'is_published',)
    list_display_links = ('title',)

    list_per_page = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published',)
    list_editable = ('is_published',)
