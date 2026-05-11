import re

with open('templates/base.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_header = """    <!-- Navbar Start -->
    <header class="sticky top-0 z-[999] w-full border-b bg-[var(--background)]/95 backdrop-blur-xl">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between gap-4">
          <div class="flex items-center gap-8">
            <a href="/" class="flex items-center gap-2">
              <img src="{% static 'images/sp_logo.png' %}" alt="StudentPeeps" class="h-8 w-auto" />
              <span class="text-lg font-bold tracking-tight hidden sm:inline">
                <span class="text-[var(--primary)]">Student</span><span>Peeps</span>
              </span>
            </a>

            <nav class="hidden md:flex items-center gap-1">
              <a href="/">
                <button class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] h-9 px-3 {% if request.path == '/' %}bg-[var(--muted)] text-[var(--foreground)]{% endif %}">
                  Home
                </button>
              </a>
              <a href="/explore">
                <button class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] h-9 px-3 {% if '/explore' in request.path %}bg-[var(--muted)] text-[var(--foreground)]{% endif %}">
                  Explore
                </button>
              </a>
            </nav>
          </div>

          <div class="hidden md:flex items-center flex-1 max-w-md mx-4">
            <form action="/explore" method="GET" class="w-full relative">
              <i class="fa fa-search absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]"></i>
              <input
                type="search"
                name="search"
                placeholder="Search gift cards..."
                class="flex h-10 w-full rounded-md border border-[var(--muted)] bg-[var(--muted)]/50 px-3 py-2 text-sm placeholder:text-[var(--muted-foreground)] focus-visible:outline-none focus:ring-2 focus:ring-[var(--primary)] pl-9"
              />
            </form>
          </div>

          <div class="flex items-center gap-2">
            <button
              class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] h-10 w-10 md:hidden"
              onclick="document.querySelector('.search-mobile-panel').classList.toggle('hidden');"
            >
              <i class="fa fa-search"></i>
            </button>

            <a href="/checkout" class="relative group">
              <button class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] h-10 w-10 relative">
                <i class="fa fa-shopping-bag"></i>
              </button>
            </a>

            {% if user.is_authenticated %}
              <div class="relative group user-dropdown-container">
                <button class="inline-flex items-center justify-center rounded-full text-sm font-medium transition-colors hover:bg-[var(--muted)] h-10 w-10 bg-[var(--muted)]">
                  <span class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--primary)] text-white text-xs font-bold uppercase">
                    {{ user.first_name|default:"U"|slice:":1" }}
                  </span>
                </button>
                <div class="absolute right-0 top-full mt-2 w-48 rounded-md border bg-white p-1 shadow-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <div class="px-2 py-1.5">
                    <p class="text-sm font-medium text-black">{{ user.first_name }} {{ user.last_name }}</p>
                    <p class="text-xs text-gray-500">{{ user.email }}</p>
                  </div>
                  <div class="h-px bg-gray-200 my-1"></div>
                  <a href="/account/logout" class="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-gray-100 text-black">
                    <i class="fa fa-sign-out mr-2"></i>
                    Sign out
                  </a>
                </div>
              </div>
            {% else %}
              <a href="/account/v2/identify">
                <button class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-[var(--primary)] text-white hover:bg-[var(--primary)]/90 h-10 px-4 py-2">
                  Sign In
                </button>
              </a>
            {% endif %}

            <button
              class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] h-10 w-10 md:hidden"
              onclick="document.querySelector('.mobile-menu-panel').classList.toggle('hidden');"
            >
              <i class="fa fa-bars"></i>
            </button>
          </div>
        </div>

        <div class="search-mobile-panel hidden border-t overflow-hidden md:hidden bg-white">
          <form action="/explore" method="GET" class="py-3 px-4 flex gap-2">
            <input
              type="search"
              name="search"
              placeholder="Search gift cards..."
              class="flex h-10 w-full rounded-md border border-[var(--muted)] bg-white px-3 py-2 text-sm placeholder:text-[var(--muted-foreground)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
            />
            <button type="button" class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] h-10 w-10" onclick="document.querySelector('.search-mobile-panel').classList.add('hidden');">
              <i class="fa fa-times"></i>
            </button>
          </form>
        </div>
        
        <div class="mobile-menu-panel hidden border-t overflow-hidden md:hidden">
          <div class="py-3 px-4 space-y-1 bg-white">
            <a href="/">
              <button class="inline-flex items-center justify-start rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] text-black h-10 px-4 py-2 w-full">Home</button>
            </a>
            <a href="/explore">
              <button class="inline-flex items-center justify-start rounded-md text-sm font-medium transition-colors hover:bg-[var(--muted)] text-black h-10 px-4 py-2 w-full">Explore</button>
            </a>
          </div>
        </div>
      </div>
    </header>
    <!-- Navbar End -->
"""

new_footer = """    <!-- FOOTER -->
    <footer class="border-t bg-gray-50 mt-auto">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8 py-12">
          <div class="space-y-4 lg:col-span-2">
            <a href="/" class="inline-flex items-center gap-2.5">
              <img src="{% static 'images/sp_logo.png' %}" alt="StudentPeeps" class="h-9 w-auto" />
              <span class="text-xl font-bold tracking-tight">
                <span class="text-[var(--primary)]">Student</span>Peeps
              </span>
            </a>

            <div>
              <h4 class="font-semibold text-sm mb-2">About Us</h4>
              <p class="text-sm text-gray-500 leading-relaxed max-w-sm">
                StudentPeeps is a platform where university students get exclusive student discounts when they shop. We aim to change how students shop in India.
              </p>
            </div>

            <a
              href="https://studentpeeps.club"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center text-sm text-[var(--primary)] hover:underline"
            >
              Visit studentpeeps.club
            </a>
          </div>
          <div>
            <h4 class="font-semibold mb-4 text-sm tracking-wide uppercase text-gray-500">Shop</h4>
            <ul class="space-y-2.5">
              <li><a href="/explore" class="text-sm hover:text-[var(--primary)] transition-colors">All Gift Cards</a></li>
              <li><a href="/explore?category=streaming" class="text-sm hover:text-[var(--primary)] transition-colors">Streaming</a></li>
              <li><a href="/explore?category=gaming" class="text-sm hover:text-[var(--primary)] transition-colors">Gaming</a></li>
              <li><a href="/explore?category=food" class="text-sm hover:text-[var(--primary)] transition-colors">Food & Dining</a></li>
              <li><a href="/explore?category=fashion" class="text-sm hover:text-[var(--primary)] transition-colors">Fashion</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold mb-4 text-sm tracking-wide uppercase text-gray-500">Categories</h4>
            <ul class="space-y-2.5">
              <li><a href="/explore?category=for-him" class="text-sm hover:text-[var(--primary)] transition-colors">For Him</a></li>
              <li><a href="/explore?category=for-her" class="text-sm hover:text-[var(--primary)] transition-colors">For Her</a></li>
              <li><a href="/explore?category=electronics" class="text-sm hover:text-[var(--primary)] transition-colors">Electronics</a></li>
              <li><a href="/explore?category=travel" class="text-sm hover:text-[var(--primary)] transition-colors">Travel</a></li>
              <li><a href="/explore?category=grocery" class="text-sm hover:text-[var(--primary)] transition-colors">Grocery</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold mb-4 text-sm tracking-wide uppercase text-gray-500">Contact Us</h4>
            <ul class="space-y-3">
              <li>
                <a
                  href="mailto:hi@studentpeeps.club"
                  class="text-sm hover:text-[var(--primary)] transition-colors flex items-start gap-2"
                >
                  <i class="fa fa-envelope h-4 w-4 mt-0.5 flex-shrink-0 text-gray-500"></i>
                  hi@studentpeeps.club
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-200 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-xs text-gray-500">
            &copy; {% now "Y" %} StudentPeeps. All rights reserved.
          </p>
          <div class="flex items-center gap-4">
            <a href="https://studentpeeps.club" target="_blank" rel="noopener noreferrer" class="text-xs text-gray-500 hover:text-[var(--primary)] transition-colors">
              studentpeeps.club
            </a>
          </div>
        </div>
      </div>
    </footer>
"""

# Find indices
nav_start = -1
nav_end = -1
for i, l in enumerate(lines):
    if "<!-- Navbar Start -->" in l:
        nav_start = i
    if "<!-- Navbar End -->" in l:
        nav_end = i
        break

footer_start = -1
footer_end = -1
for i, l in enumerate(lines):
    if "<!-- FOOTER -->" in l:
        footer_start = i
    if l.strip() == "</footer>":
        footer_end = i
        break

script_start = -1
script_end = -1
for i, l in enumerate(lines):
    if "let input = document.getElementById('search-input1');" in l:
        script_start = i
    if l.strip() == "if (accountIcon !== null && accountDropdown !== null && accountUserName !== null && accountUserNameSpan !== null) {":
        script_end = i + 4
        break

new_lines = []
for i, l in enumerate(lines):
    if nav_start <= i <= nav_end:
        if i == nav_start:
            new_lines.append(new_header)
    elif footer_start <= i <= footer_end:
        if i == footer_start:
            new_lines.append(new_footer)
    elif script_start <= i <= script_end + 1:
        # omit the script body
        pass
    else:
        new_lines.append(l)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
