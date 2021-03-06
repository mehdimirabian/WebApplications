// This is the js for the default/index.html view.

var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) {
        var k=0;
        return v.map(function(e) {e._idx = k++;});
    };

    self.get_products = function () {
        // Gets new products in response to a query, or to an initial page load.
        $.getJSON(products_url, $.param({q: self.vue.product_search}), function(data) {
            self.vue.products = data.products;
            enumerate(self.vue.products);
        });
    };

    self.store_cart = function() {
        localStorage.cart = JSON.stringify(self.vue.cart);
    };

    self.read_cart = function() {
        if (localStorage.cart) {
            self.vue.cart = JSON.parse(localStorage.cart);
        } else {
            self.vue.cart = [];
        }
        self.update_cart();
    };

    self.inc_desired_quantity = function(product_idx, qty) {
        // Inc and dec to desired quantity.
        var p = self.vue.products[product_idx];
        p.desired_quantity = Math.max(0, p.desired_quantity + qty);
        p.desired_quantity = Math.min(p.quantity, p.desired_quantity);
    };

    self.inc_cart_quantity = function(product_idx, qty) {
        // Inc and dec to desired quantity.
        var p = self.vue.cart[product_idx];
        p.cart_quantity = Math.max(0, p.cart_quantity + qty);
        p.cart_quantity = Math.min(p.quantity, p.cart_quantity);
        self.update_cart();
        self.store_cart();
    };

    self.update_cart = function () {
        enumerate(self.vue.cart);
        var cart_size = 0;
        var cart_total = 0;
        for (var i = 0; i < self.vue.cart.length; i++) {
            var q = self.vue.cart[i].cart_quantity;
            if (q > 0) {
                cart_size++;
                cart_total += q * self.vue.cart[i].price;
            }
        }
        self.vue.cart_size = cart_size;
        self.vue.cart_total = cart_total;
    };

    self.buy_product = function(product_idx) {
        var p = self.vue.products[product_idx];
        // I need to put the product in the cart.
        // Check if it is already there.
        var already_present = false;
        var found_idx = 0;
        for (var i = 0; i < self.vue.cart.length; i++) {
            if (self.vue.cart[i].id === p.id) {
                already_present = true;
                found_idx = i;
            }
        }
        // If it's there, just replace the quantity; otherwise, insert it.
        if (!already_present) {
            found_idx = self.vue.cart.length;
            self.vue.cart.push(p);
        }
        self.vue.cart[found_idx].cart_quantity = p.desired_quantity;

        // Updates the amount of products in the cart.
        self.update_cart();
        self.store_cart();
    };


    self.goto = function (page) {
        self.vue.page = page;

    };

    self.pay_without_stripe = function() {
        console.log("Payment for:", self.customer_info);
        // Calls the server.
        $.post(purchase_url,
            {
               // customer_info: JSON.stringify(self.customer_info),
                amount: self.vue.cart_total,
                cart: JSON.stringify(self.vue.cart),
            },
            function (data) {
                // The order was successful.
                self.vue.cart = [];
                self.update_cart();
                self.store_cart();
                self.goto('prod');
                $.web2py.flash("Thank you for your purchase");

            }
        );

    };

        self.get_history = function() {
            $.getJSON(history_url, function (data) {
            self.vue.history_list = data.history_list;
            for(i=0; i<self.vue.history_list.length; i++){
                self.vue.cart_history[i] = JSON.parse(self.vue.history_list[i].order_json);
                self.vue.time_history[i] = self.vue.history_list[i].created_on;
            }
            for(i=0; i<self.vue.cart_history.length; i++){
                self.vue.purchase_total[i] = 0;
                for(j=0; j<self.vue.cart_history[i].length; j++){
                    self.vue.purchase_total[i] = self.vue.purchase_total[i] + self.vue.cart_history[i][j].cart_quantity * self.vue.cart_history[i][j].price;

                }
            }
            self.vue.mehdi = self.vue.cart_history[0][0].time;
        });
    };

    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            mehdi: "",
            purchase_total: [],
            history_list: [],
            products: [],
            cart: [],
            cart_history: [],
            time_history:[],
            product_search: '',
            cart_size: 0,
            cart_total: 0,
            page: 'prod'
        },
        methods: {
            get_products: self.get_products,
            inc_desired_quantity: self.inc_desired_quantity,
            inc_cart_quantity: self.inc_cart_quantity,
            buy_product: self.buy_product,
            goto: self.goto,
            do_search: self.get_products,
        //    pay: self.pay,
            pay_without_stripe: self.pay_without_stripe,
            get_history: self.get_history
        }

    });

    self.get_products();
    self.read_cart();
    $("#vue-div").show();


    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
