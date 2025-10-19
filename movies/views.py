from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Avg, Count



def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    
    # Get rating statistics
    rating_stats = get_movie_rating_stats(movie)
    user_rating = 0
    if request.user.is_authenticated:
        user_rating = get_user_rating(movie, request.user)
    
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['rating_stats'] = rating_stats
    template_data['user_rating'] = user_rating
    
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

# Utility functions for rating calculations
def get_movie_rating_stats(movie):
    """Get average rating and total count for a movie"""
    ratings = Rating.objects.filter(movie=movie)
    avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']
    total_ratings = ratings.count()
    
    return {
        'average_rating': round(avg_rating, 1) if avg_rating else 0.0,
        'total_ratings': total_ratings
    }

def get_user_rating(movie, user):
    """Get user's rating for a specific movie"""
    try:
        rating = Rating.objects.get(movie=movie, user=user)
        return rating.rating
    except Rating.DoesNotExist:
        return 0

@login_required
@require_http_methods(["POST", "DELETE"])
def submit_rating(request, id):
    """Handle both POST (submit/update rating) and DELETE (remove rating) requests"""
    movie = get_object_or_404(Movie, id=id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating_value = data.get('rating')
            
            # Validate rating
            if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid rating. Must be between 1 and 5.'
                }, status=400)
            
            # Get or create rating
            rating, created = Rating.objects.get_or_create(
                movie=movie,
                user=request.user,
                defaults={'rating': rating_value}
            )
            
            if not created:
                # Update existing rating
                rating.rating = rating_value
                rating.save()
            
            # Get updated stats
            stats = get_movie_rating_stats(movie)
            
            return JsonResponse({
                'success': True,
                'average_rating': stats['average_rating'],
                'total_ratings': stats['total_ratings'],
                'user_rating': rating_value
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while saving the rating.'
            }, status=500)
    
    elif request.method == 'DELETE':
        try:
            # Remove user's rating
            rating = get_object_or_404(Rating, movie=movie, user=request.user)
            rating.delete()
            
            # Get updated stats
            stats = get_movie_rating_stats(movie)
            
            return JsonResponse({
                'success': True,
                'average_rating': stats['average_rating'],
                'total_ratings': stats['total_ratings'],
                'user_rating': 0
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while removing the rating.'
            }, status=500)
