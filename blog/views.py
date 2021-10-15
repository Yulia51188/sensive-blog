from django.db.models import Count
from django.shortcuts import render
from blog.models import Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in 
                 post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_details(post):
    return {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': [serialize_comment(comment)
                     for comment in post.comments.all()],
        'likes_amount': post.likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }


def serialize_comment(comment):
    return {
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_amount
    }


def get_most_popular_posts(number_of_posts):  
    most_popular_posts = (
        Post.objects
        .popular()[:number_of_posts]
        .prefetch_related('author')
        .join_posts_amount()
        .join_comments_amount()
    )
    return list(most_popular_posts)


def get_most_fresh_posts(number_of_posts):   
    fresh_posts = (
        Post.objects
        .annotate(comments_amount=Count('comments', distinct=True))
        .order_by('-published_at')[:number_of_posts]
        .prefetch_related('author')
        .join_posts_amount()
    )
    return list(fresh_posts)


def get_tag_related_posts(tag, number_of_posts):
    related_posts = (
        tag.posts.all()[:number_of_posts]
        .prefetch_related('author')
        .join_posts_amount()
        .join_comments_amount()
    )
    return list(related_posts)


def get_post_with_related_items(slug):

    post = (
        Post.objects
        .select_related('author')
        .join_posts_amount()
        .annotate(likes_amount=Count('likes', distinct=True))
        .prefetch_related('comments__author')
        .get(slug=slug)
    )
    return post


def index(request):
    most_popular_posts = get_most_popular_posts(5)
    most_fresh_posts = get_most_fresh_posts(5)
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_post_with_related_items(slug)
    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = get_most_popular_posts(5)

    context = {
        'post': serialize_post_details(post),
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = get_most_popular_posts(5)
    related_posts = get_tag_related_posts(tag, 20)

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
