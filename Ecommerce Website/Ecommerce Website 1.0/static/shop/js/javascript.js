var pathname = $(location).attr('pathname')

// clearing cart - index/checkout
function cartClear() {

    cart = JSON.parse(localStorage.getItem('cart'))
    
    localStorage.clear()
    cart = {}
    updateLocalStorageWithCart(cart)
    popoverUpdate_cart()
    
    if (pathname == '/shop/' || pathname == '/shop/index'){
        for (item in cart) {
            document.getElementById('sp' + item).innerHTML = `<img id="plus`+item +`" src="{% static 'shop/images/addToCart.png' %}" width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
        }
    }
    else if (pathname == '/shop/checkpout'){
        if (document.getElementById('successAlert') == null){
            window.location.replace("index");
        }
    }

    if(pathname == '/shop/checkout'){
        window.location.replace("index");
    }
}


//function to execute when plus button is clicked - index/checkout
$('.sppr').on('click', 'img.plus', function () {
    prod_id = this.id.toString().slice(4);   // fetching id of the clicked element and then using slice function to get desired part of the id
    cart = fetchCart()

    if (cart[prod_id] == null) {  // checking if cart dictionary has any key with same value as id of button clicked.
        discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML);
        price = document.getElementById('price' + prod_id).innerHTML;
        name = document.getElementById("name" + prod_id).title;
        desc = document.getElementById("desc" + prod_id).title;
        image = document.getElementById("image" + prod_id).src;
        qnty = 1
        
        //cart[prod_id] = {'name': name.trim(), 'qnty': qnty, 'price': price, 'discount': discount}
        cart[prod_id] = [name.trim(), qnty, price, discount, image, desc]
        
        // executing only for homepage of shop
        if (pathname == '/shop/' || pathname == '/shop/index'){
            updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
            add_cart_button()      
        }// executing only for homepage of shop
        else if (pathname == '/shop/checkout'){
            updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
        }
    }
    else {
      cart[prod_id][1] = cart[prod_id][1] + 1;    // decreasing the ordered quantity of the product in the cart by 1
      document.getElementById('val' + prod_id).innerHTML = cart[prod_id][1];   // updating the ordered quantity in the product description
      updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
    }
    
    popoverUpdate_cart();   // updating the ordered quantity in the popup cart

    if (pathname == '/shop/checkout'){
      discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML)
      price = parseFloat(document.getElementById('price' + prod_id).innerHTML)
      document.getElementById('total' + prod_id).innerHTML = (price - (price * discount / 100)) * cart[prod_id][1]

      cartTotal = parseFloat(localStorage.getItem('cartTotal'))
      change_cartTotal = price - (price * discount / 100)
      updateCartTotalLocalStorage(cartTotal + change_cartTotal)
    }
});


//function to execute when minus button is clicked - index/checkout
$('.sppr').on('click', 'img.minus', function () {

    prod_id = this.id.toString().slice(5);   // fetching id of the clicked element and then using slice function to get desired part of the id
    cart = fetchCart()

    if (cart[prod_id] == null) {

    }
    else {
      cart[prod_id][1] = cart[prod_id][1] - 1;    // decreasing the ordered quantity of the product in the cart by 1
      
      cart[prod_id][1] = Math.max(0, cart[prod_id][1]);   // making sure user cant reduce the ordered quantity less the 0 s
      document.getElementById('val' + prod_id).innerHTML = cart[prod_id][1];   // updating the ordered quantity in the product description

      if (cart[prod_id][1] == 0) {
          delete cart[prod_id];
        if (pathname == '/shop/' || pathname == '/shop/index'){
          document.getElementById('sp' + prod_id).innerHTML = `<img id="plus` +prod_id + `" src=` + staticAddToCartImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                                  onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
        }
        else if (pathname == '/shop/checkout'){
            quantity = 1
            cartTotalCalculation(0)
        }
      }
      else{

        if (pathname == '/shop/checkout'){
            cartTotalCalculation(cart[prod_id][1] )
        }   
      }

        updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
        popoverUpdate_cart();   // updating the ordered quantity in the popup cart

    }
});

// function to calculate the cart total - checkout
function cartTotalCalculation(quantity){
    discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML)
    price = parseFloat(document.getElementById('price' + prod_id).innerHTML)
    document.getElementById('total' + prod_id).innerHTML = (price - (price * discount / 100)) * quantity
    cartTotal = parseFloat(localStorage.getItem('cartTotal'))
    change_cartTotal = price - (price * discount / 100)
    updateCartTotalLocalStorage(cartTotal - change_cartTotal)
}

// function to update card total - checkout
function updateCartTotalLocalStorage(cartTotal) {
    localStorage.setItem('cartTotal', cartTotal)
    document.getElementById('cartTotal').innerHTML = cartTotal
    //update_CartItemHiddenInput()
}


//function that that changes image when cursor mover away from them. - index
function changebutton_Hover(element){
    img_name = element.getAttribute('src')
    hover_image_name = img_name.slice(0, -4)+ "_hover" + img_name.slice(-4)
    img_name = element.setAttribute('src', hover_image_name)
}


//function that that changes image when cursor hovers over them. - index
function changebutton_Hover_Out(element){
    hover_img_name = element.getAttribute('src')
    hover_out_image_name = hover_img_name.slice(0, -10)+ ".png"
    img_name = element.setAttribute('src', hover_out_image_name)
}


//function that add plus and minus button and is called from main function when Add to cart is clicked - index
function add_cart_button() {
    cart = fetchCart()
    for (item in cart) {
      document.getElementById("sp" + item).innerHTML = `<img id="minus`+item +`" src=` + staticMinusImage() + ` width="25" class="minus" title="Remove From Cart"  alt="Remove From Cart" 
                                                            onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />
                                                        <span id='val` + item + `' class='mx-2'>` + cart[item][1] + `</span> 
                                                        <img id="plus`+item +`" src=` + staticPlusImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                            onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
    }
}


//function that returns the cart - index/checkout
function fetchCart() {
    cart = JSON.parse(localStorage.getItem('cart'));
    return cart;
}


// updating localStorage with cart - index/checkout
function updateLocalStorageWithCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}


// function that returns items in cart - index/checkout
function numberOfItemsInCard() {
    var items_in_cart = 0;
    if (localStorage.getItem('cart') == null) {
        return 0;
    }
    else {
        cart = fetchCart();
        for (item in cart) {
            items_in_cart = items_in_cart + cart[item][1];
        }
        return items_in_cart;
    }
}


// function to display products in cart popover
function popoverUpdate_cart() {
    document.getElementById('cart').innerHTML = numberOfItemsInCard();
    cart = fetchCart()
    items_in_cart = numberOfItemsInCard()

    if (items_in_cart == 0) {
      document.getElementById('popcart').setAttribute('title', "<h6>There are no items in your cart</h6>");
      document.getElementById('popcart').setAttribute('data-content', "");
    }
    else {
      var popStr = "<div class='popover-div'>";
      var i = 1

      for (item in cart) {
        if(cart[item][0].length > 20){
            var name = cart[item][0].slice(0, 20) + "...";
        }
        else{
            var name = cart[item][0];
        }

        var prod_id = item.slice(2, );

        popStr = popStr + "<div class='row mx=2 my-2'><div class='col-md-2'>" +
          "<a href='product?id=" + prod_id + "'><img src='" + cart[item][4] + "' width='25' height='35' /> </a></div><div class='col-md-10'>" +
          name + "<br />" +
          cart[item][1] +
          " pcs. @ $" +
          cart[item][2] + " - " +
          " Discount " +
          cart[item][3] + "%" +
          " <br /></div></div>";

        i = i + 1;
      }
      popStr = popStr + "<div class='mt-3' style='text-align:center'><a href='checkout'><button class='btn btn-primary'>Checkout</button></a>&emsp;<button class='btn btn-primary' onClick='cartClear()'>Clear Cart</button></div>"
      popSts = popStr + "</div>"
      document.getElementById('popcart').setAttribute('title', "<h6>There are " + numberOfItemsInCard() + " items in your cart</h6>");
      document.getElementById('popcart').setAttribute('data-content', popStr);
    }
    $('#popcart').popover('show');  
}
