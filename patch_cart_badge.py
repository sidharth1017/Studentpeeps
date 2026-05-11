import re

filepath = "/Users/sidharthverma/Studentpeeps/codebase/Studentpeeps/templates/base.html"
with open(filepath, 'r+', encoding='utf-8') as f:
    content = f.read()

    # Find the shopping bag block inside base.html
    pattern = r'(<a href="/giftcard/cart/" class="relative group">\s*<button.*?>\s*<i data-lucide="shopping-bag" class=""></i>)(\s*</button>)'
    
    badge_html = '''
              <span id="cartCountBadge" class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--primary)] text-[10px] font-bold text-white hidden">
                0
              </span>
              '''
              
    new_btn = r'\1' + badge_html.strip() + r'\2'
    
    new_content = re.sub(pattern, new_btn, content)
    
    f.seek(0)
    f.write(new_content)
    f.truncate()

print("Base header patched")
