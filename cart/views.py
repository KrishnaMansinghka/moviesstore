from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from .forms import CartStateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    
    # Get state from session or form
    state = request.session.get('selected_state', None)
    
    if request.method == 'POST':
        form = CartStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            request.session['selected_state'] = state
        else:
            messages.error(request, 'Please select a state before purchasing.')
            return redirect('cart.index')
    
    if not state:
        messages.error(request, 'Please select a state before purchasing.')
        return redirect('cart.index')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.state = state
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    request.session['selected_state'] = None  # Clear state after purchase
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    template_data['state'] = state
    return render(request, 'cart/purchase.html', {'template_data': template_data})

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
    
    # Handle state selection form
    form = CartStateForm()
    selected_state = request.session.get('selected_state', None)
    
    if request.method == 'POST':
        form = CartStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            request.session['selected_state'] = state
            messages.success(request, f'State selected: {dict(form.fields["state"].choices)[state]}')
            return redirect('cart.index')
        else:
            messages.error(request, 'Please select a valid state.')
    
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    template_data['form'] = form
    template_data['selected_state'] = selected_state
    return render(request, 'cart/index.html', {'template_data': template_data})


def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[str(id)] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')
# Create your views here.

def add_to_cart(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[str(id)] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')
