import re

new_content = """{% extends 'base.html' %}
{% load static %}

{% block title %}Gift Card Details{% endblock %}

{% block body %}
<div class="min-h-screen bg-[var(--background)]">
  <div class="relative">
    <!-- Top Background Graphic -->
    <div class="absolute inset-x-0 top-0 h-[320px] sm:h-[400px] overflow-hidden pointer-events-none" style="background: linear-gradient(135deg, rgba(1,115,230,0.15) 0%, rgba(239,65,103,0.05) 100%);">
      <div class="absolute inset-0" style="background: radial-gradient(ellipse 80% 60% at 20% 30%, rgba(1,115,230,0.1), transparent 70%);"></div>
      <div class="absolute bottom-0 left-0 right-0 h-32" style="background: linear-gradient(to top, var(--background) 0%, transparent 100%);"></div>
    </div>

    <div class="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 pt-6 pb-16">
      <a href="javascript:history.back()" class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-gray-200 h-10 px-4 py-2 mb-6 text-gray-700">
        <i class="fa fa-arrow-left mr-2"></i> Back
      </a>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12">
        <!-- left column -->
        <div class="lg:col-span-3">
          <!-- Gift Card Design Block -->
          <div class="relative w-full aspect-[16/10] rounded-xl overflow-hidden group shadow-xl" style="background: linear-gradient(135deg, #1f2937 0%, #111827 60%, #030712 100%);">
            <div class="absolute inset-0 overflow-hidden">
              <div class="absolute -top-1/4 -right-1/4 w-3/4 h-3/4 rounded-full opacity-10" style="background: radial-gradient(circle, white 0%, transparent 70%);"></div>
              <div class="absolute -bottom-1/4 -left-1/4 w-2/3 h-2/3 rounded-full opacity-[0.05]" style="background: radial-gradient(circle, white 0%, transparent 70%);"></div>
            </div>

            <div class="relative z-10 flex flex-col justify-between h-full p-6 sm:p-8">
              <div class="flex items-start justify-between gap-4">
                <span class="text-xs font-semibold tracking-[0.2em] uppercase opacity-70 text-white">Gift Card</span>
                <div class="flex items-center gap-2">
                  <div class="px-2 py-0.5 rounded-md bg-emerald-500 text-white">
                    <span class="text-[10px] font-bold">{{ giftcard.margin }} OFF</span>
                  </div>
                  <i class="fa fa-gift h-5 w-5 text-white/40"></i>
                </div>
              </div>

              <div class="flex items-end justify-between gap-4">
                <div class="flex items-center gap-4">
                  <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-md flex items-center justify-center backdrop-blur-md bg-white/10 border border-white/20">
                    <!-- hardcoded icon since lucide not available -->
                    <span class="text-white text-3xl font-bold">{{ giftcard.brand_name|slice:":1" }}</span>
                  </div>
                  <div>
                    <h2 class="text-2xl sm:text-3xl font-bold tracking-tight text-white">{{ giftcard.brand_name }}</h2>
                    <p class="text-sm opacity-70 mt-0.5 text-white capitalize">{{ giftcard.category }}</p>
                  </div>
                </div>
                <div class="text-right flex-shrink-0">
                  <span class="text-3xl sm:text-4xl font-bold text-white" id="cardOverlayAmount">₹100</span>
                </div>
              </div>
            </div>
            <div class="absolute bottom-0 left-0 right-0 h-px opacity-20" style="background: linear-gradient(90deg, transparent, white, transparent);"></div>
          </div>

          <div class="space-y-3 mt-12 lg:mt-16">
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">{{ giftcard.name }} Gift Card</h1>
            <p class="text-gray-600 text-base leading-relaxed max-w-2xl">
              {{ giftcard.description }}
            </p>
            <div class="flex flex-wrap gap-1.5 pt-2">
                <span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-700 capitalize">gift voucher</span>
                <span class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-700 capitalize">shopping</span>
            </div>
          </div>

          <div class="mt-10">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="p-3.5 text-center space-y-1.5 rounded-xl bg-gray-50 border border-gray-100">
                <i class="fa fa-bolt h-5 w-5 mx-auto text-[var(--primary)]"></i>
                <p class="font-medium text-xs text-gray-900">Instant Delivery</p>
                <p class="text-xs text-gray-500">Delivered in minutes</p>
              </div>
              <div class="p-3.5 text-center space-y-1.5 rounded-xl bg-gray-50 border border-gray-100">
                <i class="fa fa-shield h-5 w-5 mx-auto text-[var(--primary)]"></i>
                <p class="font-medium text-xs text-gray-900">100% Secure</p>
                <p class="text-xs text-gray-500">Encrypted transactions</p>
              </div>
              <div class="p-3.5 text-center space-y-1.5 rounded-xl bg-gray-50 border border-gray-100">
                <i class="fa fa-clock-o h-5 w-5 mx-auto text-[var(--primary)]"></i>
                <p class="font-medium text-xs text-gray-900">No Expiry</p>
                <p class="text-xs text-gray-500">Use anytime</p>
              </div>
              <div class="p-3.5 text-center space-y-1.5 rounded-xl bg-gray-50 border border-gray-100">
                <i class="fa fa-check-circle-o h-5 w-5 mx-auto text-[var(--primary)]"></i>
                <p class="font-medium text-xs text-gray-900">Guaranteed</p>
                <p class="text-xs text-gray-500">Full value assured</p>
              </div>
            </div>
          </div>

          <div class="mt-10">
            <h3 class="font-semibold text-lg mb-4 text-gray-900">How It Works</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <div class="flex gap-3 items-start">
                <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-[var(--primary)]/10 text-[var(--primary)]">
                  <i class="fa fa-credit-card"></i>
                </div>
                <div>
                  <p class="font-medium text-sm text-gray-900">Choose & Pay</p>
                  <p class="text-xs text-gray-500 mt-1 leading-relaxed">Select your amount and complete secure checkout</p>
                </div>
              </div>
              <div class="flex gap-3 items-start">
                <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-[var(--primary)]/10 text-[var(--primary)]">
                  <i class="fa fa-paper-plane"></i>
                </div>
                <div>
                  <p class="font-medium text-sm text-gray-900">Get Your Card</p>
                  <p class="text-xs text-gray-500 mt-1 leading-relaxed">Receive your digital gift card code instantly via email</p>
                </div>
              </div>
              <div class="flex gap-3 items-start">
                <div class="w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 bg-[var(--primary)]/10 text-[var(--primary)]">
                  <i class="fa fa-gift"></i>
                </div>
                <div>
                  <p class="font-medium text-sm text-gray-900">Redeem & Enjoy</p>
                  <p class="text-xs text-gray-500 mt-1 leading-relaxed">Use the code online or in-store at any location</p>
                </div>
              </div>
            </div>
          </div>

          <!-- FAQs -->
          <div class="mt-10">
            <h3 class="font-semibold text-lg mb-4 text-gray-900">FAQs</h3>
            <div class="space-y-0.5 rounded-lg overflow-hidden border">
              {% for faq in faqs %}
              <details class="group bg-white border-b last:border-0">
                  <summary class="px-6 py-4 cursor-pointer font-medium hover:bg-gray-50 flex justify-between items-center text-sm text-gray-800 list-none [&::-webkit-details-marker]:hidden">
                      {{ faq.question }}
                      <span class="group-open:rotate-180 transition-transform"><i class="fa fa-chevron-down text-gray-400"></i></span>
                  </summary>
                  <div class="px-6 py-4 bg-gray-50 text-sm text-gray-600 leading-relaxed border-t border-gray-100">
                      {{ faq.answer }}
                  </div>
              </details>
              {% endfor %}
            </div>
          </div>

          <div class="mt-10">
            <h3 class="font-semibold text-lg mb-4 text-gray-900">Similar Cards</h3>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 border-2 border-dashed border-gray-200 rounded-xl p-8 items-center justify-center min-h-[160px] bg-gray-50/50">
              <p class="col-span-full text-center text-gray-500 text-sm">No similar cards available at the moment.</p>
            </div>
          </div>
        </div>

        <!-- right column -->
        <div class="lg:col-span-2">
          <div class="lg:sticky lg:top-24 z-50">
            <div class="p-6 space-y-6 shadow-xl border border-gray-100 bg-white/95 backdrop-blur-xl rounded-2xl">
              <div>
                <h3 class="font-semibold text-base mb-3 text-gray-900">Select Amount</h3>
                <div class="grid grid-cols-3 gap-2" id="amountOptions">
                  <button data-amount="100" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border shadow-sm h-11 px-4 py-2 bg-[var(--primary)] text-white border-[var(--primary)]">₹100</button>
                  <button data-amount="500" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border hover:border-gray-400 hover:bg-gray-50 h-11 px-4 py-2 bg-white text-gray-700">₹500</button>
                  <button data-amount="1000" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border hover:border-gray-400 hover:bg-gray-50 h-11 px-4 py-2 bg-white text-gray-700">₹1000</button>
                  <button data-amount="2000" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border hover:border-gray-400 hover:bg-gray-50 h-11 px-4 py-2 bg-white text-gray-700">₹2000</button>
                  <button data-amount="5000" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border hover:border-gray-400 hover:bg-gray-50 h-11 px-4 py-2 bg-white text-gray-700">₹5000</button>
                  <button data-amount="custom" class="amount-btn inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all border hover:border-gray-400 hover:bg-gray-50 h-11 px-4 py-2 bg-white text-gray-700">Custom</button>
                </div>
              </div>

              <div class="flex items-center justify-between gap-4">
                <span class="text-sm font-medium text-gray-500">Quantity</span>
                <div class="flex items-center gap-2">
                  <button id="qtyMinusBtn" class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors border hover:bg-gray-100 h-9 w-9 disabled:opacity-50 text-gray-700" disabled>
                    <i class="fa fa-minus"></i>
                  </button>
                  <span id="qtyText" class="w-10 text-center text-base font-semibold tabular-nums text-gray-900">1</span>
                  <button id="qtyPlusBtn" class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors border hover:bg-gray-100 h-9 w-9 text-gray-700">
                    <i class="fa fa-plus"></i>
                  </button>
                </div>
              </div>

              <div class="border-t border-gray-100 pt-5 space-y-3">
                <div class="flex items-center justify-between gap-4 text-sm text-gray-600">
                  <span>Card value</span>
                  <span class="tabular-nums font-medium" id="cardValueDisp">₹100</span>
                </div>
                <div class="flex items-center justify-between gap-4 text-sm text-emerald-600">
                  <span class="flex items-center gap-1.5 font-medium">
                    <i class="fa fa-bolt"></i>
                    StudentPeeps Discount (<span id="discountPercentDisp">2</span>%)
                  </span>
                  <span class="tabular-nums font-bold" id="savingsDisp">-₹2</span>
                </div>
                <div class="flex items-center justify-between gap-4 pt-1">
                  <span class="font-semibold text-lg text-gray-900">Total</span>
                  <div class="text-right">
                    <span class="text-2xl font-bold tabular-nums text-gray-900" id="finalPrice">₹98</span>
                    <p class="text-xs text-gray-500 line-through tabular-nums mt-0.5" id="originalPrice">₹100</p>
                  </div>
                </div>
              </div>

              <form id="addToCartForm" method="POST" action="{% url 'giftcard:add_to_cart' %}" class="space-y-3 pt-2">
                {% csrf_token %}
                <input type="hidden" name="sku" value="{{ giftcard.sku }}">
                <input type="hidden" name="denomination" id="selectedDenomination" value="100">
                <input type="hidden" name="quantity" id="selectedQty" value="1">
                <input type="hidden" name="buy_now" id="buyNowField" value="false">

                <button type="button" onclick="handleCartAction(true)" class="inline-flex items-center justify-center rounded-xl text-sm font-semibold transition-all hover:opacity-90 h-12 px-4 py-2 w-full bg-[var(--primary)] text-white shadow-md shadow-[var(--primary)]/20">
                  Buy Now
                </button>
                <button type="button" onclick="handleCartAction(false)" class="inline-flex items-center justify-center rounded-xl text-sm font-semibold transition-all border hover:bg-gray-50 h-12 px-4 py-2 w-full bg-white text-gray-700 border-gray-200">
                  <i class="fa fa-shopping-bag mr-2"></i> Add to Cart
                </button>
              </form>

              <div class="border-t border-gray-100 pt-5 space-y-3">
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <i class="fa fa-check-circle text-gray-400 flex-shrink-0"></i>
                  <span>Valid at all locations & online</span>
                </div>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <i class="fa fa-check-circle text-gray-400 flex-shrink-0"></i>
                  <span>No expiration date or fees</span>
                </div>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <i class="fa fa-check-circle text-gray-400 flex-shrink-0"></i>
                  <span>Digital delivery via email</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
    const discountPercent = parseFloat("{{ giftcard.margin_raw|default:2 }}");
    let currentAmount = 100;
    let currentQty = 1;

    const buttons = document.querySelectorAll('.amount-btn');
    const finalPriceEl = document.getElementById('finalPrice');
    const originalPriceEl = document.getElementById('originalPrice');
    const discountPercentDisp = document.getElementById('discountPercentDisp');
    const savingsDisp = document.getElementById('savingsDisp');
    const cardValueDisp = document.getElementById('cardValueDisp');
    const cardOverlayAmount = document.getElementById('cardOverlayAmount');
    
    if (discountPercentDisp) discountPercentDisp.textContent = discountPercent;

    function formatCurrency(amount) {
        return "₹" + amount.toLocaleString("en-IN");
    }

    function updatePrice() {
        const amount = currentAmount;
        const qty = currentQty;
        const originalTotal = amount * qty;
        
        let customDiscountPercent = discountPercent;
        if (customDiscountPercent > 0 && customDiscountPercent < 1) {
            customDiscountPercent = customDiscountPercent * 100;
        }

        const discountValue = (originalTotal * customDiscountPercent) / 100;
        const savings = Math.round(discountValue);
        const finalAmount = Math.round(originalTotal - savings);

        finalPriceEl.textContent = formatCurrency(finalAmount);
        originalPriceEl.textContent = formatCurrency(originalTotal);
        savingsDisp.textContent = "-" + formatCurrency(savings);
        cardValueDisp.textContent = formatCurrency(amount) + " x " + qty;
        cardOverlayAmount.textContent = formatCurrency(amount);

        // Update hidden field for form submission
        document.getElementById('selectedDenomination').value = amount;
        document.getElementById('selectedQty').value = qty;
    }

    function handleCartAction(buyNow) {
        const form = document.getElementById('addToCartForm');
        const buyNowField = document.getElementById('buyNowField');

        buyNowField.value = buyNow ? "true" : "false";

        if (buyNow) {
            form.submit();
        } else {
            // Ajax add to cart
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.message) {
                        alert('Added to cart!');
                    } else if (data.error) {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('Something went wrong!');
                });
        }
    }

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            buttons.forEach(btn => {
                btn.classList.remove('bg-[var(--primary)]', 'text-white', 'border-[var(--primary)]', 'shadow-sm');
                btn.classList.add('bg-white', 'text-gray-700');
            });
            this.classList.remove('bg-white', 'text-gray-700');
            this.classList.add('bg-[var(--primary)]', 'text-white', 'border-[var(--primary)]', 'shadow-sm');

            const value = this.dataset.amount;

            if (value === "custom") {
                const customAmount = prompt("Enter custom amount");
                if (customAmount && !isNaN(customAmount)) {
                    currentAmount = parseInt(customAmount);
                    updatePrice();
                }
            } else {
                currentAmount = parseInt(value);
                updatePrice();
            }
        });
    });

    document.getElementById('qtyMinusBtn').addEventListener('click', () => {
        if(currentQty > 1) {
            currentQty--;
            document.getElementById('qtyText').textContent = currentQty;
            updatePrice();
            if(currentQty === 1) document.getElementById('qtyMinusBtn').disabled = true;
        }
    });

    document.getElementById('qtyPlusBtn').addEventListener('click', () => {
        currentQty++;
        document.getElementById('qtyText').textContent = currentQty;
        document.getElementById('qtyMinusBtn').disabled = false;
        updatePrice();
    });

    // Default load
    updatePrice();
</script>
{% endblock %}
"""

with open('templates/pages/giftcard_page.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

