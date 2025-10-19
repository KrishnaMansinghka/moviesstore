from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from cart.models import Item


def index(request):
    template_data = {'title': 'Movies Store'}
    return render(request, 'home/index.html', {'template_data': template_data})


def about(request):
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})


def local_popularity_map(request):
    template_data = {'title': 'Local Popularity Map'}
    return render(request, 'home/local_popularity_map.html', {'template_data': template_data})


def top_movies_by_state(request):
    """
    GET /api/top_movies_by_state/?state=GA
    Returns JSON: [{"name": "<Movie Name>", "count": <int>}, ...]
    Aggregates Item rows by movie name for the given Order.state.
    """
    state = request.GET.get('state')
    if not state:
        return JsonResponse({'error': 'Missing state parameter'}, status=400)

    qs = (
        Item.objects
        .filter(order__state=state)
        .values('movie__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    data = [{'name': row['movie__name'], 'count': row['count']} for row in qs]
    return JsonResponse(data, safe=False)
