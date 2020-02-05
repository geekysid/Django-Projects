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


// function to check if wishlist dictionary is present in local storage on page load
function addToWishlist_initialize(){
    
    var wishList = fetch_LocalStorage_Wishlist();
    add_wishlist_buttons();
}


// function that executes when add to wishlist button is clicked
$('.spWLpr').on('click', 'img.addWL', function(){
    prod_id = this.id.toString().slice(5);

    // adding product to wishlist dictionary in localStorage
    wishList = fetch_LocalStorage_Wishlist();

    if (wishList[prod_id] == null) {  // checking if wishList dictionary has any key with same value as id of button clicked.
        Wishlist_AddRemove(prod_id, 'add_wishlist');  // modal to popup when added
    }

})


// function that executes when remove from wishlist button is clicked
$('.spWLpr').on('click', 'img.removeWL', function(){
    prod_id = this.id.toString().slice(8);
    
    let wishList = fetch_LocalStorage_Wishlist();

    // removing clicked product from wishlist dictionary in localstorage
    if(wishList[prod_id] != null){
        Wishlist_AddRemove(prod_id, 'remove_wishlist');
    }
})


// function that executes when add/remove  to/from wishlisht is clicked.
function Wishlist_AddRemove(prod_id, action){

    let wishList = fetch_LocalStorage_Wishlist();

    if(action == 'remove_wishlist'){
        var product_arr = wishList[prod_id]
        delete wishList[prod_id];   // removing key of clicked product from localstorage

        //updating image for Add To Wishlist button
        new_img = `<img src="` + staticAddToWishlistImage() + `" width="25" class="addWL" id="addWL` + prod_id + `" title="Add To Wishlist"  alt="Add To Wishlist" 
                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
    }
    else if (action == 'add_wishlist'){
        discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML);
        price = document.getElementById('price' + prod_id).innerHTML;
        name = document.getElementById("name" + prod_id).title;
        desc = document.getElementById("desc" + prod_id).title;
        image = document.getElementById("image" + prod_id).src;
        qnty = 1
        
        //WishList[prod_id] = {'name': name.trim(), 'qnty': qnty, 'price': price, 'discount': discount}
        wishList[prod_id] = [name.trim(), qnty, price, discount, image, desc];

        var product_arr = wishList[prod_id]

        //updating image for Remove From Wishlist button
        new_img = `<img src="` + staticAddedToWishlistImage() + `" width="25" class="removeWL" id="removeWL` + prod_id + `" title="Remove From Wishlist"  alt="Remove From Wishlist" 
                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`;
    }
        
    update_LocalStorage_Wishlist(wishList);     // updating dictw ith removed key to localstorage

    document.getElementById('spWL'+prod_id).innerHTML = new_img

    ModalDisplay(prod_id, product_arr, action);  // modal to popup when removed
}


// function called when the pag is load
function add_wishlist_buttons(){
    wishList = fetch_LocalStorage_Wishlist();
    for (item in wishList){
        new_img = `<img src="` + staticAddedToWishlistImage() + `" width="25" class="removeWL" id="removeWL` + item + `" title="Remove From Wishlist"  alt="Remove From Wishlist" 
                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`;

        document.getElementById('spWL'+item).innerHTML = new_img
    }
}


// function to set wishlist dictionary in local storage
function update_LocalStorage_Wishlist(wishList){
    localStorage.setItem('wishList', JSON.stringify(wishList));
    popoverUpdate_wishList();
}


// function to set wishlist dictionary in local storage
function fetch_LocalStorage_Wishlist(){
    if(localStorage.getItem('wishList') == null){
        update_LocalStorage_Wishlist({})    // updating blank dictioanry with key 'wishList' in localstorage
        return {}       // returning blank dictioanry if no dictionary with key 'wishList' exist
    }
    else{
        return JSON.parse(localStorage.getItem('wishList'));
    }
}


// function that returns items in cart - index/checkout
function numberOfWishListedItem() {
    var items_in_WishList = 0;
    if (localStorage.getItem('cart') == null) {
        return 0;
    }
    else {
        wishList = fetch_LocalStorage_Wishlist();
        for (item in wishList) {
            items_in_WishList = items_in_WishList + wishList[item][1];
        }
        return items_in_WishList;
    }
}


//function that that changes image when cursor mover away from them in wishlist popup
function wishlistPopup_Hover(element){
    element.style.cursor="pointer"
}


//function that that changes image when cursor hovers over them in wishlist popup
function wishlistPopup_Hover_Out(element){
    element.style.cursor="default"
}


// function to display products in wishlist popover
function popoverUpdate_wishList() {
    //document.getElementById('popwishList').title = numberOfWishListedItem();
    wishList = fetch_LocalStorage_Wishlist()
    items_in_Wishlist = numberOfWishListedItem()

    if (items_in_Wishlist < 1) {
      document.getElementById('popwishList').setAttribute('data-content', "<b>You have No items in Wish List</b>");
    }
    else {
      var popStr = "<div class='popover-div'>";
      var i = 1

      for (item in wishList) {
        if(wishList[item][0].length > 20){
            var name = wishList[item][0].slice(0, 20) + "...";
        }
        else{
            var name = wishList[item][0];
        }

        var prod_id = item.slice(2, );

        popStr = popStr + "<div class='row mx=2 my-2'><div class='col-md-2'>" +
          "<a href='product?id=" + prod_id + "'><img src='" + wishList[item][4] + "' width='25' height='35' /> </a></div><div class='col-md-10'>" +
          name + "<br />" +
          wishList[item][1] +
          " pcs. @ $" +
          wishList[item][2] + " - " +
          " Discount " +
          wishList[item][3] + "%" +
          " <br />"+
          "<span style='text-align:right' id='popwishList"+item+"' onClick='Wishlist_AddToCart.call(this)' onmouseover='wishlistPopup_Hover(this)' onmouseout='wishlistPopup_Hover_Out(this)' >Move to Cart</span>&emsp;"+
          "<span style='text-align:right' id='popwishList"+item+"' onClick='removeFromWishlist.call(this)' onmouseover='wishlistPopup_Hover(this)' onmouseout='wishlistPopup_Hover_Out(this)' >Remove Item</span>"+
          "</div></div>";

        i = i + 1;
      }
      popSts = popStr + "</div>"
      data_content = "<b>Number of Wishliested items:" + numberOfWishListedItem() + "</b><br />"+ popStr
      document.getElementById('popwishList').setAttribute('data-content', data_content);
    }
    //$('#popwishList').popover('show');  
}


// function called when 'Remove From Wishlist' is clicked from Wishlist Popup
function removeFromWishlist(){
    prod_id = this.id.toString().slice(11)
    Wishlist_AddRemove(prod_id, 'remove_wishlist')
}

// function called when 'Add To Cart' is clicked from Wishlist Popup
function Wishlist_AddToCart(){
    prod_id = this.id.toString().slice(11)
    Cart_AddRemove(prod_id, 'plus_cart')
}


// 
$(document).ready(function(){
    //$('[data-toggle=popover]').popover();
});


//function to execute when plus button is clicked - index/checkout
$('.sppr').on('click', 'img.plus', function () {
    prod_id = this.id.toString().slice(4);   // fetching id of the clicked element and then using slice function to get desired part of the id


    Cart_AddRemove(prod_id, 'plus_cart')

    if (pathname == '/BookStore/checkout'){
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

    prod_arr = cart[prod_id]

    Cart_AddRemove(prod_id, 'minus_cart')

});


function Cart_AddRemove(prod_id, action){

    cart = fetchCart()

    if(action == 'plus_cart'){
        if (cart[prod_id] == null) {  // checking if cart dictionary has any key with same value as id of button clicked.
            discount = parseFloat(document.getElementById('discount' + prod_id).innerHTML);
            price = document.getElementById('price' + prod_id).innerHTML;
            name = document.getElementById("name" + prod_id).title;
            desc = document.getElementById("desc" + prod_id).title;
            image = document.getElementById("image" + prod_id).src;
            qnty = 1
            
            //cart[prod_id] = {'name': name.trim(), 'qnty': qnty, 'price': price, 'discount': discount}
            cart[prod_id] = [name.trim(), qnty, price, discount, image, desc]
            
            var prod_arr = cart[prod_id]

            // executing only for homepage of BookStore
            if (pathname == '/BookStore/' || pathname == '/BookStore/index' || pathname == '/BookStore/product'){
                updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
                add_cart_button()      
            }// executing only for homepage of BookStore
            else if (pathname == '/BookStore/checkout'){
                updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage
            }
        }
        else {
          cart[prod_id][1] = cart[prod_id][1] + 1;    // decreasing the ordered quantity of the product in the cart by 1
          var prod_arr = cart[prod_id]
          document.getElementById('val' + prod_id).innerHTML = cart[prod_id][1];   // updating the ordered quantity in the product description
        }
    }
    else if(action=='minus_cart'){
        if (cart[prod_id] == null) {

        }
        else {
            var prod_arr = cart[prod_id]
            cart[prod_id][1] = cart[prod_id][1] - 1;    // decreasing the ordered quantity of the product in the cart by 1
            
            cart[prod_id][1] = Math.max(0, cart[prod_id][1]);   // making sure user cant reduce the ordered quantity less the 0 s
            document.getElementById('val' + prod_id).innerHTML = cart[prod_id][1];   // updating the ordered quantity in the product description

            if (cart[prod_id][1] == 0) {
                delete cart[prod_id];
                if (pathname == '/BookStore/' || pathname == '/BookStore/index' || pathname == '/BookStore/product'){
                document.getElementById('sp' + prod_id).innerHTML = `<img id="plus` +prod_id + `" src=` + staticAddToCartImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                                        onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
                }
                else if (pathname == '/BookStore/checkout'){
                    quantity = 1
                    cartTotalCalculation(0)
                }
            }
            else{

                if (pathname == '/BookStore/checkout'){
                    cartTotalCalculation(cart[prod_id][1] )
                }   
            }
        }
    }

    updateLocalStorageWithCart(cart)   // updating cart dictionary in the local storage

    popoverUpdate_cart();   // updating the ordered quantity in the popup cart
    ModalDisplay(prod_id, prod_arr, action)

}

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
        if(pathname == '/BookStore/product'){
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


// modal to popup when add to wishlist/remove from wishlist/add to cart/remove from cart is clicked
function ModalDisplay(prod_id, prod_arr, buttonClicked){
    var modalBody = "";

    if (buttonClicked == "add_wishlist"){
        var modalTitle =  prod_arr[0] + " Added to the Whishlist";
    }
    else if (buttonClicked == "remove_wishlist"){
        var modalTitle = prod_arr[0] + " removed to the Whishlist";
    }
    else if (buttonClicked == "plus_cart"){
        var modalTitle = prod_arr[0] + " Added to the Cart";
    }
    else if (buttonClicked == "minus_cart"){
        var modalTitle = prod_arr[0] + " removed to the Cart";
    }
    
    if (prod_arr[5].length > 200) {
        var desc = prod_arr[5].slice(0, 200) + "...";
    }
    else{
        var desc = prod_arr[5];
    }

    var id = prod_id.slice(2, );

    var modalBody = `<div class="row my-2" style="font-size:12px" >
                        <div class="col-md-12">
                            <li class="media">
                                <div class="col-md-2">
                                    <a href="product?id=`+ id + `"><img src="` + prod_arr[4] + `" width="70px" id="image` + prod_id + `" height="100px" class="mr-3" alt="..." /></a>
                                </div>
                                <div class="col-md-10">
                                    <div class="row">
                                        <div class="media-body col-md-12">
                                            <b><span class="" style="font-size:13px" id="name`+ prod_id + `">
                                                `+ prod_arr[0] + `
                                            </span></b>
                                            <br />
                                            <span class="" id="desc`+ prod_id + `" title="` + desc + `">` + desc + `</span>
                                        </div>
                                    </div>

                                    <div class="row mt-3">
                                        <div class="col-md-6 media-body" style="text-align:center;" id="">
                                            <b>Discount</b> = <span class="discount`+ prod_id + `" id="discount` + prod_id + `">` + prod_arr[3] + `</span>%
                                        </div>
                                        <div class="col-md-6 media-body" style="text-align:center;" id="">
                                            <b>Price</b> = $<span class="price`+ prod_id + `" id="price` + prod_id + `">` + prod_arr[2] + `</span>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        </div>
                    </div>`;

    var modalHtml = `<div class="modal fade" id="popoverWishlist_Add_Modal" tabindex="-1" data-backdrop="static" role="dialog" aria-labelledby="popoverWishlist_Add_Title" aria-hidden="true" focus="true" keyboard="flase">
                        <div class="modal-dialog  modal-dialog-centered" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                            <h5 class="modal-title" id="popoverWishlist_Add_Title">` + modalTitle + `</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                            </div>
                            <div class="modal-body" id="popoverWishlist_Add_Body">
                                ` + modalBody + `
                            </div>
                            <div class="modal-footer">
                            <button type="button" class="btn btn-success" data-dismiss="modal">Ok</button>
                            </div>
                        </div>
                        </div>
                    </div>`;
    
    document.getElementById('AddToCart_Modal').innerHTML = modalHtml

    $('#popoverWishlist_Add_Modal').modal({
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
    //$('#popcart').popover('show');  
}


// clearing cart - index/checkout
function cartClear() {
    
    cart = fetchCart()

    if (pathname == '/BookStore/' || pathname == '/BookStore/index'){
        for (item in cart) {
            document.getElementById('sp' + item).innerHTML = `<img id="plus`+item +`" src=` + staticAddToCartImage() + ` width="25" class="plus" title="Add To Cart"  alt="Add To Cart" 
                                                                    onmouseover="changebutton_Hover(this)" onmouseout="changebutton_Hover_Out(this)" />`
        }
    }
    
    localStorage.clear()
    cart = {}
    updateLocalStorageWithCart(cart)
    popoverUpdate_cart()

    if (pathname == '/BookStore/checkpout'){
        if (document.getElementById('successAlert') == null){
            window.location.replace("index");
        }
    }

    if(pathname == '/BookStore/checkout'){
        window.location.replace("index");
    }
}

function popoverClicked (element){
    element_id = element.getAttribute('id')
    alt = document.getElementById(element_id).alt

    if(element_id == 'wishList'){
        if(alt == '0'){
            document.getElementById(element_id).alt='1'
            document.getElementById('cart').alt='0'
            $('#popcart').popover('hide');
            $('#popwishList').popover('show');
        }
        if(alt == '1'){
            document.getElementById(element_id).alt = '0'
            document.getElementById(element_id).alt='0'
            $('#popwishList').popover('hide');
            $('#popcart').popover('hide');
        }
    }
    else if(element_id == 'cart'){
        if(alt == '0'){
            document.getElementById(element_id).alt='1'
            document.getElementById('wishList').alt='0'
            $('#popwishList').popover('hide');
            $('#popcart').popover('show');
        }
        if(alt == '1'){
            document.getElementById(element_id).alt='0'
            document.getElementById(element_id).alt = '0'
            $('#popcart').popover('hide');
            $('#popwishList').popover('hide');  
            
        }
    }


}

