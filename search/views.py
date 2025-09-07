from django.shortcuts import render
from store.models import Product
from django.db.models import Q

def search_results(request):
    query = request.GET.get('q')  
    
    if query:
        
        search_terms = query.split()

        
        query_filter = Q()

        
        for term in search_terms:
            query_filter |= Q(name__icontains=term) | Q(description__icontains=term)

        
        products = Product.objects.filter(query_filter)
    else:
        
        products = Product.objects.none()  

    return render(request, 'search.html', {'products': products, 'query': query})
