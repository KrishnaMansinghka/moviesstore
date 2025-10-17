from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {
        'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
                  'home/about.html',
                  {'template_data': template_data})

def local_popularity_map(request):
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    return render(request,
                  'home/local_popularity_map.html',
                  {'template_data': template_data})
# Create your views here.
