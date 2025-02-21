from django.db.models import Count
from django.utils import timezone


def get_all_posts(posts):
    return posts.annotate(
        comment_count=Count('comments')
    ).select_related(
        'category', 'author', 'location'
    ).order_by(
        "-pub_date"
    )


def get_relevant_posts(posts):
    return (
        get_all_posts(posts).filter(
            is_published=True
        ).filter(
            pub_date__lte=timezone.now()
        ).filter(
            category__is_published=True
        )
    )
