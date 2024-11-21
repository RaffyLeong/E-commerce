console.log("working fine");

// Submit Comment Form from Review
$("#commentForm").submit(function(e){
    e.preventDefault();

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function(response){
            console.log("Comment Saved to DB...");

            if(response.bool === true){
                $("#review-res").html("Review added successfully.")
                $(".hide-comment-form").hide()
                
            }
        }
    });
});

// Add To Cart Start
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}


// Add Cart
$(".add-to-cart-btn").on("click", function() {
    let this_val = $(this);
    let index = this_val.attr("data-index");
    
    let quantity = $(".product-quantity-" + index).val();
    let product_id = $(".product-id-" + index).val();
    let product_title = $(".product-title-" + index).val();
    let product_price = $(".current-product-price-" + index).text().replace('$', '').trim(); 
    let product_pid = $(".product-pid-" + index).val();
    let product_image = $(".product-image-" + index).val();


    console.log("Product ID:", product_id);
    console.log("Quantity:", quantity);
    console.log("Title:", product_title);
    console.log("Price:", product_price);
    console.log("PID:", product_pid);
    console.log("Image:", product_image);

    if (!product_id || !product_title || !quantity || !product_price) {
        console.error("Missing required fields");
        return;
    }

    $.ajax({
        url: '/add-to-cart/',
        type: 'POST',
        data: {
            'id': product_id,
            'pid': product_pid,
            'image': product_image,
            'qty': quantity,
            'title': product_title,
            'price': product_price,
        },
        headers: {
            'X-CSRFToken': getCSRFToken() 
        },
        dataType: 'json',
        success: function(response) {
            this_val.html("✔");
            $(".cart-items-count").text(response.totalcartitems);
            console.log("Added Product to Cart!");
        },
        error: function(xhr, status, error) {
            console.error("Error adding to cart:", error);
            console.log(xhr.responseText);
        }
    });
});


// Delete Product start
$(".delete-product").on("click", function(){
    let product_id = $(this).attr("data-product");
    let this_val = $(this);

    console.log("Product ID:", product_id);

    $.ajax({
        url: "/delete-from-cart/",
        data: {
            "id": product_id
        },
        dataType: "json",
        beforeSend: function(){
            this_val.hide();
        },
        success: function(response){
            this_val.show();
            $(".cart-items-count").text(response.totalcartitems);
            $("#cart-list").html(response.data);
        },
        error: function(xhr, status, error){
            console.error("Error deleting from cart:", error);
            this_val.show();
        }
    });
});



// Contact

$(document).on("submit","#contact-form-ajax", function(e){
    e.preventDefault()
    console.log("Submited...");

    let full_name = $("#full_name").val()
    let email = $("#email").val()
    let phone = $("#phone").val()
    let subject = $("#subject").val()
    let message = $("#message").val()

    console.log("Name:", full_name);
    console.log("Email:", email);
    console.log("Phone:", phone);
    console.log("Subject:", subject);
    console.log("Message:", message);

    $.ajax({
        url: "/ajax-contact-form",
        data: {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "subject": subject,
            "message": message,
        },
        dataType:"json",
        beforeSend: function(){
            console.log("Sending data to Server...");

        },
        success: function(res){
            console.log("Sent Data to server!");
            $("#contact-form-ajax").hide()
            $("#message-response").html("Message Sent successfully")
        }
    })
})


 // Coupon
 $(document).ready(function() {
    $('#coupon-form').submit(function(e) {
        e.preventDefault(); // Prevent default form submission

        let code = $('#code').val();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {
                'code': code,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                console.log("Coupon applied successfully");
                // Handle successful application, e.g., update totals
            },
            error: function(xhr, status, error) {
                console.error("Coupon application failed:", error);
            }
        });
    });
});