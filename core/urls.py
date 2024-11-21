from django.urls import path, include
from core.views import index, category_list_view, product_list_view, product_detail_view, category_product_list_view, vendor_list_view, ajax_add_review, add_to_cart, cart_view, delete_item_from_cart, checkout_view, payment_completed_view, payment_failed_view, customer_dashboard, contact, ajax_contact_form, about_us, services, blog


app_name = "core"

urlpatterns = [

    # Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),

    # Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Vendor
    path("vendors/", vendor_list_view, name="vendor-list"),

    # Add Review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    # Add to cart
    path("add-to-cart/", add_to_cart, name="add-to-cart"),

    # cart Page URL
    path("cart/", cart_view, name="cart"),

     # Delete Item form cart
    path("delete-from-cart/", delete_item_from_cart, name="delete_item_from_cart"),

    # Checkout URL
    path("checkout/", checkout_view, name="checkout"),

    # paypal URL
    path("paypal/", include('paypal.standard.ipn.urls')),

    # Payment Successful
    path("payment-completed/", payment_completed_view, name="payment-completed"),

    # Payment Failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),

    # Dashboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),

    # Contact URL
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),

    # About Us URL
    path("about/", about_us, name="about"),

    # Services URL
    path("services/", services, name="services"),

    # Blog URL
    path("blog/", blog, name="blog"),

]