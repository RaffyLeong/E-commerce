from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from core.models import Product, Category, Vendor, CartOrder, CartOrderProducts, ProductImages, ProductReview, wishlist, Address
from userauths.models import ContactUs
from core.forms import ProductReviewForm
from django.contrib import messages
from django.template.loader import render_to_string

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm

################# Index ####################
def index(request):
    products = Product.objects.filter(product_status="published")
    context = {
        "products": products
    }
    return render(request, 'core/index.html', context)
 

################# product list view ####################
def product_list_view(request):
    products = Product.objects.filter(product_status="published")
    context = {
        "products" : products
    }

    return render(request, 'core/product-list.html', context)

################# category list view####################
def category_list_view(request):
    categories = Category.objects.all()
    

    context = {
        "categories" : categories
    }

    return render(request, 'core/category-list.html', context)

################# product detail view ####################
def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    reviews = ProductReview.objects.filter(product=product)
    p_image = product.p_images.all()
    
    review_form = ProductReviewForm()

    context = {
        'product': product,
        'review_form': review_form,
        'p_image': p_image,
        'reviews': reviews,
        'products': products,
    }
    return render(request, 'core/product-detail.html', context)

################# category product list view ####################
def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    

    context = {
        "category":category,
    }
    return render(request, "core/category-product-list.html", context)

################# Vendor list view ####################
def vendor_list_view(request):
    vendor = Vendor.objects.all()
    context = {
        "vendor": vendor,
    }
    return render(request, "core/vendor_list.html", context)

################# Vendor view ####################
def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    context = {
        "vendor": vendor,
    }
    return render(request, "core/vendor_detail.html", context)

################# Review ####################
def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST['review'],
        rating=request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
        'date': review.date.strftime("%B %d, %Y"),
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))
    

    return JsonResponse({
        'bool': True,
        'context': context,
        'average_reviews': average_reviews,
    })




################# Add Cart ####################
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        title = request.POST.get('title')
        qty = request.POST.get('qty')
        price = request.POST.get('price')
        image = request.POST.get('image')  
        pid = request.POST.get('pid')  

       
        if not all([product_id, title, qty, price]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            qty = int(qty)  
            price = float(price) 
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid quantity or price"}, status=400)

       
        if 'cart_data_obj' not in request.session:
            request.session['cart_data_obj'] = {}

        cart_data = request.session['cart_data_obj']

       
        if product_id in cart_data:
            cart_data[product_id]['qty'] += qty 
        else:
            cart_data[product_id] = {
                'title': title,
                'qty': qty,
                'price': price,
                'image': image,
                'pid': pid,
            }  

      
        request.session['cart_data_obj'] = cart_data

        return JsonResponse({
            "data": cart_data,
            'totalcartitems': sum(item['qty'] for item in cart_data.values()) 
        })

    return JsonResponse({"error": "Invalid request method."}, status=405)


################# Cart View ####################
def cart_view(request):
    cart_total_amount = 0
    total_items = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            try:
                qty = int(item['qty'])
                price = float(item['price'])
                cart_total_amount += qty * price
                total_items += qty
            except (ValueError, TypeError):
                messages.error(request, f"Invalid price for product ID {product_id}")
        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'], 
            'totalcartitems': total_items,
            'cart_total_amount': cart_total_amount
        })
    else:
        messages.warning(request, "Your cart is empty.")
        return render(request, "core/cart.html", {
            "cart_data": {}, 
            'totalcartitems': total_items,
            'cart_total_amount': cart_total_amount
        })
    

################# Delete Item ####################
def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])


    context = render_to_string("core/async/cart-list.html", {
            "cart_data": request.session['cart_data_obj'], 
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


################# Check Out ####################
@login_required
def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0

    # Checking if cart_data_obj session exosts
    if 'cart_data_obj' in request.session:

        # Getting total amount for Paypal Amount
        for product_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])
        
        # create Order Object
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount
        )

        # Getting total amount for Cart
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

            cart_order_product = CartOrderProducts.objects.create(
                order=order,
                invoice_no="INVOICE_NO-" + str(order.id), #INVOICE_NO-5
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total = float(item['qty']) * float(item['price'])
            )


    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(round(cart_total_amount, 2)),
        'item_name': "Order-Item_No-" + str(order.id),
        'invoice': "INV_NO-4" + str(order.id),
        'currency_code': "USD",
        'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
        'cancel_return': 'http://{}{}'.format(host, reverse("core:payment-failed")),
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    try:
        active_address = Address.objects.get(user=request.user, status=True)
    except:
        messages.warning(request, "There are multiple address, only one should be activated")
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

        return render(request, "core/checkout.html", {
            "cart_data": request.session['cart_data_obj'], 
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount,
            'paypal_payment_button': paypal_payment_button,
            'active_address':active_address
        })
    else:
        return render(request, "core/checkout.html", {
            "cart_data": {}, 
            'totalcartitems': 0,
            'cart_total_amount': 0
        })


################# Paypal Completed View ####################
@login_required
def payment_completed_view(request):
    return render(request, 'core/payment-completed.html')


################# Paypal failed View ####################
@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

################# Customer Dashboard View ####################
@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Successfully.")
        return redirect("core:dashboard")
    
    context = {
        "orders": orders,
        "address": address
    }
    return render(request, 'core/dashboard.html', context)

################# Contact View ####################
def contact(request):
    return render(request, "core/contact.html")

def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    message = request.GET['message']
    subject = request.GET['subject']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        message=message,
        subject=subject,
    )

    data = {
        "bool": True,
        "message": "Message sent successfully"
    }

    return JsonResponse({"data":data})


################# About Us View ####################
def about_us(request):
    return render(request, "core/about-us.html")

################# Services View ####################
def services(request):
    return render(request, "core/services.html")

################# Blog View ####################
def blog(request):
    return render(request, "core/blog.html")

