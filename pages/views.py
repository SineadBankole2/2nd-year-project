from django.views.generic import TemplateView
from django.shortcuts import render
from store.models import Product, Category
from reviews.forms import ReviewForm
from reviews.models import Review


def homepage(request):
    return render(request, "home.html")

def mens_view(request):
    
    men_category = Category.objects.get(name='Men')
    products = Product.objects.filter(category=men_category).prefetch_related('reviews')
    review_form = ReviewForm()

    return render(request, 'mens.html', {
        'products': products,
        'review_form': review_form
    })

def kids_view(request):
    kid_category = Category.objects.get(name='kids')
    products = Product.objects.filter(category=kid_category).prefetch_related('reviews')
    review_form = ReviewForm()

    return render(request, 'kids.html', {
        'products': products,
        'review_form': review_form
    })



def womens_view(request):
    women_category = Category.objects.get(name='women')
    products = Product.objects.filter(category=women_category).prefetch_related('reviews')
    review_form = ReviewForm()

    return render(request, 'womens.html', {
        'products': products,
        'review_form': review_form
    })
