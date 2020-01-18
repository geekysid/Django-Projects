var pathname = $(location).attr('pathname')

function GetParameter_URL(param) {  
    var url = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');  
    for (var i = 0; i < url.length; i++) {  
        var urlparam = url[i].split('=');  
        if (urlparam[0] == param) {  
            return urlparam[1];  
        }  
    }  
}  

$(document).ready(function(){
    $('[data-toggle=popover]').popover();
});


//function to execute when plus button is clicked - index/checkout
$('.sppr').on('click', 'img.plus', function () {
    prod_id = this.id.toString().slice(4);   // fetching id of the clicked element and then using slice function to get desired part of the id
    cart = fetchCart()
    console.log(prod_id)
    console.log(cart)

    if (cart[prod_id] == null) {  // checking if cart dictionary has any key with same value as id of button clicked.
        discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML);
        price = document.getElementById('price' + prod_id).innerHTML;
        name = document.getElementById("name" + prod_id).title;
        console.log("desc" + prod_id)
        desc = document.getElementById("desc" + prod_id).title;
        image = document.getElementById("image" + prod_id).src;
        qnty = 1
        
        //cart[prod_id] = {'name': name.trim(), 'qnty': qnty, 'price': price, 'discount': discount}
        cart[prod_id] = [name.trim(), qnty, price, discount, image, desc]
        
        // executing only for homepage of shop
        if (pathname == '/shop/' || pathname == '/shop/index' || pathname == '/shop/product'){
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
    AddToCart_ModalDisplay(prod_id, "plus");

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
        if (pathname == '/shop/' || pathname == '/shop/index' || pathname == '/shop/product'){
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
      
      AddToCart_ModalDisplay(prod_id, "minus");
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
    element.style.cursor="pointer"
}


//function that that changes image when cursor hovers over them. - index
function changebutton_Hover_Out(element){
    hover_img_name = element.getAttribute('src')
    hover_out_image_name = hover_img_name.slice(0, -10)+ ".png"
    img_name = element.setAttribute('src', hover_out_image_name)
    element.style.cursor="default"
}


//function that add plus and minus button and is called from main function when Add to cart is clicked - index
function add_cart_button() {

    cart = fetchCart()
    for (item in cart) {
        id = parseInt(item.slice(2,))
        if(pathname == '/shop/product'){
            if(id == parseInt(GetParameter_URL('id'))){
                document.getElementById("sp" + item).innerHTML = add_button(item)
                break
            }
        }
        else{
            document.getElementById("sp" + item).innerHTML = add_button(item)
        }
    }
}


function add_button(item){
    cart = fetchCart()
    return `<img id="minus`+item +`" src=` + staticMinusImage() + ` width="25" class="minus" title="Remove From Cart"  alt="Remove From Cart" 
                onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />
            <span id='val` + item + `' class='mx-2'>` + cart[item][1] + `</span> 
            <img id="plus`+item +`" src=` + staticPlusImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
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


function AddToCart_ModalDisplay(prod_id, buttonClicked){
    
    var cart = fetchCart();
    var modalBody = ""
    if (buttonClicked == "plus"){
        var modalTitle = "1 Book Added to the Cart"
    }
    else if (buttonClicked == "minus"){
        var modalTitle = "1 Book Removed from the Cart"
    }
    

    for (item in cart){
        if(item == prod_id){
        console.log(item + '==' + prod_id)
            if (cart[item][5].length > 200) {
                var desc = cart[item][5].slice(0, 200) + "...";
            }
            else{
                var desc = cart[item][5];
            }
            var prod_id = item.slice(2, );

            var modalBody = `<div class="row my-2" style="font-size:12px" >
                                <div class="col-md-12">
                                    <li class="media">
                                        <div class="col-md-2">
                                            <a href="product?id=`+ prod_id + `"><img src="` + cart[item][4] + `" width="70px" id="image` + item + `" height="100px" class="mr-3" alt="..." /></a>
                                        </div>
                                        <div class="col-md-10">
                                            <div class="row">
                                                <div class="media-body col-md-12">
                                                    <b><span class="" style="font-size:13px" id="name`+ item + `">
                                                        `+ cart[item][0] + `
                                                    </span></b>
                                                    <br />
                                                    <span class="" id="desc`+ item + `" title="` + desc + `">` + desc + `</span>
                                                </div>
                                            </div>

                                            <div class="row mt-3">
                                                <div class="col-md-6 media-body" style="text-align:center;" id="">
                                                    <b>Discount</b> = <span class="discount`+ item + `" id="discount` + item + `">` + cart[item][3] + `</span>%
                                                </div>
                                                <div class="col-md-6 media-body" style="text-align:center;" id="">
                                                    <b>Price</b> = $<span class="price`+ item + `" id="price` + item + `">` + cart[item][2] + `</span>
                                                </div>
                                            </div>
                                        </div>
                                    </li>
                                </div>
                            </div>`
        }
    }

    var modalHtml = `<div class="modal fade" id="popoverCart_Add_Modal" tabindex="-1" data-backdrop="static" role="dialog" aria-labelledby="popoverCart_Add_Title" aria-hidden="true" focus="true" keyboard="flase">
                        <div class="modal-dialog  modal-dialog-centered" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                            <h5 class="modal-title" id="popoverCart_Add_Title">` + modalTitle + `</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                            </div>
                            <div class="modal-body" id="popoverCart_Add_Body">
                                ` + modalBody + `
                            </div>
                            <div class="modal-footer">
                            <button type="button" class="btn btn-success" data-dismiss="modal">Ok</button>
                            </div>
                        </div>
                        </div>
                    </div>`
    
    document.getElementById('AddToCart_Modal').innerHTML = modalHtml

    $('#popoverCart_Add_Modal').modal({
        show:true
    });
}


// function to display products in cart popover
function popoverUpdate_cart() {
    document.getElementById('cart').title = numberOfItemsInCard();
    cart = fetchCart()
    items_in_cart = numberOfItemsInCard()

    if (items_in_cart < 1) {
      document.getElementById('popcart').setAttribute('data-content', "<b>There are no items in your cart</b>");
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
      data_content = "<b>Number of items in cart:" + numberOfItemsInCard() + "</b><br />"+ popStr
      document.getElementById('popcart').setAttribute('data-content', data_content);
    }
    $('#popcart').popover('show');  
}


// clearing cart - index/checkout
function cartClear() {
    
    cart = fetchCart()

    if (pathname == '/shop/' || pathname == '/shop/index'){
        for (item in cart) {
            document.getElementById('sp' + item).innerHTML = `<img id="plus`+item +`" src=` + staticAddToCartImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
        }
    }
    
    localStorage.clear()
    cart = {}
    updateLocalStorageWithCart(cart)
    popoverUpdate_cart()

    if (pathname == '/shop/checkpout'){
        if (document.getElementById('successAlert') == null){
            window.location.replace("index");
        }
    }

    if(pathname == '/shop/checkout'){
        window.location.replace("index");
    }
}

