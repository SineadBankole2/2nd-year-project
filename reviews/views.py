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
from django.db.models import Avg

# ✅ import OrderItem (and optionally Order if you need it later)
from order.models import OrderItem

class ReviewsView(View):
    def get(self, request):
        reviews = Review.objects.all()
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

        # ✅ PURCHASE CHECK (do NOT pass a raw string to 'order')
        # If your Order model has user FK (ideal):
        # has_purchased = OrderItem.objects.filter(order__user=request.user, product=product.name).exists()

        # Works even if Order has no user FK; matches by email on the Order:
        has_purchased = OrderItem.objects.filter(
            order__emailAddress=request.user.email,
            product=product.name  # OrderItem.product is a string name in your codebase
        ).exists()

        if not has_purchased:
            messages.error(request, "You can only review products you’ve purchased.")
            return redirect('reviews')

        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        # If you added a verified_purchase field, set it here:
        # review.verified_purchase = True
        review.save()

        messages.success(request, "Thanks! Your review has been submitted.")
        return redirect('reviews')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReviewView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('cos_accounts:signin')

        review_text = request.POST.get('review_text')
        rating_raw = request.POST.get('rating')
        product_id = request.POST.get('product')

        if not (review_text and rating_raw and product_id):
            messages.error(request, "Missing fields.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            rating = int(rating_raw)
        except ValueError:
            messages.error(request, "Invalid rating.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        product = get_object_or_404(Product, id=product_id)

        # ✅ PURCHASE CHECK (safe related lookup on the FK)
        # If Order has user FK (preferred):
        # has_purchased = OrderItem.objects.filter(order__user=request.user, product=product.name).exists()

        # If not, match on order email (string) + product name (string):
        has_purchased = OrderItem.objects.filter(
            order__emailAddress=request.user.email,
            product=product.name
        ).exists()

        if not has_purchased:
            messages.error(request, "You can only review products you’ve purchased.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Prevent duplicate reviews (update instead)
        existing = Review.objects.filter(user=request.user, product=product).first()
        if existing:
            existing.review_text = review_text
            existing.rating = rating
            # existing.verified_purchase = True
            existing.save()
            messages.success(request, "Your review has been updated.")
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                review_text=review_text,
                rating=rating,
                # verified_purchase=True
            )
            messages.success(request, "Thanks! Your review has been submitted.")

        return redirect(request.META.get('HTTP_REFERER', '/'))


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
