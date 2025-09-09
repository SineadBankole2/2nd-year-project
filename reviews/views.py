from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Review
from .forms import ReviewForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from store.models import Product
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Avg, Q
from django.urls import reverse
from order.models import OrderItem

class ReviewsView(View):
    def get(self, request):
        # Newest first; avoid N+1
        reviews = Review.objects.select_related('product', 'user').order_by('-id')
        form = ReviewForm()

        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        if average_rating:
            average_rating = round(average_rating, 1)
            full_stars = int(average_rating)
            has_half_star = (average_rating - full_stars) >= 0.5
            empty_stars = 5 - full_stars - (1 if has_half_star else 0)
        else:
            full_stars = 0
            has_half_star = False
            empty_stars = 5

        return render(request, 'reviews/reviews.html', {
            'reviews': reviews,
            'form': form,
            'average_rating': average_rating,
            'full_stars': range(full_stars),
            'has_half_star': has_half_star,
            'empty_stars': range(empty_stars),
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('cos_accounts:signin')

        form = ReviewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please fix the errors in the form.")
            return redirect('reviews')

        product = form.cleaned_data.get('product')
        if not product:
            messages.error(request, "Product is required for a review.")
            return redirect('reviews')

        # ✅ Has purchased? (match by user OR email; product name OR FK)
        has_purchased = OrderItem.objects.filter(
            Q(order__user=request.user) | Q(order__emailAddress__iexact=request.user.email),
            Q(product=product.name) | Q(product_ref=product)
        ).exists()

        if not has_purchased:
            messages.error(request, "You can only review products you’ve purchased.")
            return redirect('reviews')

        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()

        messages.success(request, "Thanks! Your review has been submitted.")
        return redirect('reviews')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReviewView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('cos_accounts:signin')

        # Where to go after submit — prefer explicit "next", fallback to Reviews page
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('reviews')

        review_text = (request.POST.get('review_text') or "").strip()
        rating_raw = request.POST.get('rating')
        product_id = request.POST.get('product')

        if not (review_text and rating_raw and product_id):
            messages.error(request, "Missing fields.")
            return redirect(next_url)

        try:
            rating = int(rating_raw)
        except ValueError:
            messages.error(request, "Invalid rating.")
            return redirect(next_url)

        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect(next_url)

        product = get_object_or_404(Product, id=product_id)

        # ✅ Has purchased? (user OR email; product name OR FK)
        has_purchased = OrderItem.objects.filter(
            Q(order__user=request.user) | Q(order__emailAddress__iexact=request.user.email),
            Q(product=product.name) | Q(product_ref=product)
        ).exists()

        if not has_purchased:
            messages.error(request, "You can only review products you’ve purchased.")
            return redirect(next_url)

        existing = Review.objects.filter(user=request.user, product=product).first()
        if existing:
            existing.review_text = review_text
            existing.rating = rating
            existing.save()
            messages.success(request, "Your review has been updated.")
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                review_text=review_text,
                rating=rating,
            )
            messages.success(request, "Thanks! Your review has been submitted.")

        return redirect(next_url)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return HttpResponseForbidden("You can't delete someone else's review.")
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('reviews')


def like_test(request):
    review = Review.objects.first()
    return render(request, 'reviews/like_test.html', {'review': review})


@csrf_exempt
def test_like_review(request, review_id):
    if request.method == 'POST':
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        review.helpful_count += 1
        review.save()
        return JsonResponse({'helpful_count': review.helpful_count})
    return JsonResponse({'error': 'Invalid method'}, status=400)


@csrf_exempt
def like_review(request, review_id):
    if request.method == 'POST':
        try:
            review = Review.objects.get(id=review_id)
            review.helpful_count += 1
            review.save()
            return JsonResponse({'helpful_count': review.helpful_count})
        except Review.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=400)
