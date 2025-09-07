from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Size, ProductSize
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.urls import reverse
from questions.models import Question
from django.db.models import Sum
from cart.models import CartItem


def all_products_view(request):
    products = Product.objects.all()
    return render(request, 'all_products.html', {'products': products})


def category_view(request, main_category):
    main_category_obj = get_object_or_404(Category, name__iexact=main_category)
    subcategories = Category.objects.filter(parent=main_category_obj)

   
    subcategory_name = request.GET.get('subcategory')


    if subcategory_name == "all" or not subcategory_name:
        all_categories = [main_category_obj] + list(subcategories)
        products = Product.objects.filter(category__in=all_categories)
    else:
      
        subcategory = get_object_or_404(Category, name__iexact=subcategory_name, parent=main_category_obj)
        products = Product.objects.filter(category=subcategory)

    return render(request, 'category.html', {
        'main_category': main_category_obj,
        'subcategories': subcategories,
        'products': products,
        'selected_subcategory': subcategory_name  
    })



def mens_view(request):
    men_category = get_object_or_404(Category, name__iexact="Men")
    subcategories = Category.objects.filter(parent=men_category)

    subcategory_name = request.GET.get('subcategory')

    if subcategory_name:
        subcategory = get_object_or_404(Category, name__iexact=subcategory_name, parent=men_category)
        products = Product.objects.filter(category=subcategory)
    else:
        products = Product.objects.filter(category__in=[men_category] + list(subcategories))

    return render(request, 'mens.html', {
        'products': products,
        'subcategories': subcategories,
    })


def kids_view(request):
    kid_category = get_object_or_404(Category, name__iexact="Kids")
    subcategories = Category.objects.filter(parent=kid_category)

    subcategory_name = request.GET.get('subcategory')

    if subcategory_name:
        subcategory = get_object_or_404(Category, name__iexact=subcategory_name, parent=kid_category)
        products = Product.objects.filter(category=subcategory)
    else:
        products = Product.objects.filter(category__in=[kid_category] + list(subcategories))

    return render(request, 'kids.html', {
        'products': products,
        'subcategories': subcategories,
    })


def womens_view(request):
    women_category = get_object_or_404(Category, name__iexact="Women")
    subcategories = Category.objects.filter(parent=women_category)

    subcategory_name = request.GET.get('subcategory')

    if subcategory_name:
        subcategory = get_object_or_404(Category, name__iexact=subcategory_name, parent=women_category)
        products = Product.objects.filter(category=subcategory)
    else:
        products = Product.objects.filter(category__in=[women_category] + list(subcategories))

    return render(request, 'womens.html', {
        'products': products,
        'subcategories': subcategories,
    })



def add_cart(request, product_id):
    cart = request.session.get('cart', {})

    if product_id in cart:
        cart[product_id] += 1 
    else:
        cart[product_id] = 1  

    request.session['cart'] = cart  
    request.session.modified = True  

    return redirect('cart_page')  


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_items.append({'product': product, 'quantity': quantity})
            total_price += product.price * quantity
        except Product.DoesNotExist:
            pass

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})



def stock_management(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    if not request.user.is_superuser:
        return redirect('home')  

    products = Product.objects.prefetch_related("size_stock__size").all()
    sizes = Size.objects.all()
    unanswered_count = Question.objects.filter(answer__isnull=True).count()

    
    most_purchased = (
        CartItem.objects.values('product')  
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
        .first()
    )

    return render(request, 'stock.html', {
        'products': products,
        'sizes': sizes,
        'unanswered_count': unanswered_count,
        'most_purchased': most_purchased,
    })






      
    



def add_product(request):
    if not request.user.is_superuser:
        return redirect('store:stock_management')

    categories = Category.objects.all()
    sizes = Size.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")
        colour = request.POST.get("colour")
        quantity = request.POST.get("quantity")  

        if not (name and price and category_id):
            return render(request, 'stock.html', {
                'categories': categories,
                'sizes': sizes,
                'error': "All fields are required!"
            })

        category = get_object_or_404(Category, id=category_id)

        new_product = Product(
            name=name,
            price=price,
            category=category,
            image=image,
            colour=colour
        )
        new_product.save()

        
        selected_size_ids = request.POST.getlist('sizes')
        new_product.sizes.set(selected_size_ids)

        
        total_quantity = 0
        for size in sizes:
            quantity_size = request.POST.get(f"quantity_{size.id}")
            if quantity_size:
                quantity_int = int(quantity_size)
                total_quantity += quantity_int
                ProductSize.objects.create(
                    product=new_product,
                    size=size,
                    quantity=quantity_int
                )

        new_product.quantity_in_stock = total_quantity
        new_product.save()

        return redirect('store:stock_management')

    return render(request, 'add.html', {'categories': categories, 'sizes': sizes})




def delete_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('store:stock_management')

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":  
        product.delete()
        return redirect('store:stock_management')  

    return render(request, 'homepage.html', {'product': product}) 


from django.shortcuts import render
from .models import Product, Category

def filter_list(request):
    products = Product.objects.filter(quantity_in_stock__gt=0)  
    categories = Category.objects.all()
    sizes = Size.objects.all()

   
    category_filter = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    colour_filter = request.GET.get('colour')
    size_filter = request.GET.get('size')


    colours = Product.objects.values_list('colour', flat=True).distinct()
    

    
    if category_filter and category_filter != "all":
        products = products.filter(category__id=category_filter)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if colour_filter and colour_filter != "all":
        products = products.filter(colour=colour_filter)

    if size_filter and size_filter != "all":
        products = products.filter(sizes__name=size_filter) 

    

    return render(request, 'filter_list.html', {
        'products': products,
        'categories': categories,
        'colours': colours,
        'sizes': sizes,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})



def stock_search(request):
    query = request.GET.get('q', '')  

    if request.method == "POST":
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('new_stock')

        try:
            product = Product.objects.get(id=product_id)
            product.quantity_in_stock = int(new_stock)
            product.save()
        except Product.DoesNotExist:
            pass

      
        return redirect('store:stock_management')

  
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.none()

    return render(request, 'stock.html', {'products': products, 'query': query})




def update_stock(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == "POST":
        product_id = request.POST.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return HttpResponseNotFound("Product not found")

        total_quantity = 0  

        for size in product.sizes.all():
            size_field_name = f"size_{size.id}"
            new_stock = request.POST.get(size_field_name)

            if new_stock:
                try:
                    new_stock = int(new_stock)
                except ValueError:
                    continue

                product_size, created = ProductSize.objects.get_or_create(
                    product=product,
                    size=size,
                    defaults={'quantity': new_stock}
                )

                if not created:
                    product_size.quantity = new_stock
                    product_size.save()

                total_quantity += new_stock  

        
        product.quantity_in_stock = total_quantity
        product.save()

        return redirect('store:stock_management')

    return redirect('store:stock_management')


def analytics_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    
    top_item = (
        CartItem.objects.values('product')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
        .first()
    )

    most_purchased = None
    if top_item:
        try:
            product = Product.objects.get(id=top_item['product'])
            most_purchased = {
                'product': product,
                'total_quantity': top_item['total_quantity']
            }
        except Product.DoesNotExist:
            pass  

    
    recent_cart_item = (
        CartItem.objects
        .select_related('product')
        .order_by('-id') 
        .first()
    )

    
    low_stock_threshold = 10
    low_stock_products = Product.objects.filter(quantity_in_stock__lt=low_stock_threshold)

    context = {
        'most_purchased': most_purchased,
        'recent_cart_item': recent_cart_item,
        'low_stock_products': low_stock_products, 
    }

    return render(request, 'analysis.html', context)
