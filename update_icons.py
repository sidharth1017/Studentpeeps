import os
import re

# Mapping from FontAwesome/Unicons to Lucide
MAPPING = {
    # Unicons
    'uil uil-user-circle': 'circle-user',
    'uil uil-search': 'search',
    'uil uil-multiply': 'x',
    'uil uil-check-circle': 'check-circle',
    'uil uil-check': 'check',
    'uil uil-envelope': 'mail',
    'uil uil-shield-check': 'shield-check',
    'uil uil-layer-group': 'layers',
    'uil uil-save': 'save',
    'uil uil-cloud-lock': 'cloud',
    'uil uil-angle-down': 'chevron-down',
    'uil uil-angle-right': 'chevron-right',
    'uil uil-arrow-right': 'arrow-right',
    'uil-user-circle': 'circle-user',
    
    # Font Awesome
    'fa fa-search': 'search',
    'fa fa-bars': 'menu',
    'fa fa-times': 'x',
    'fa fa-shopping-bag': 'shopping-bag',
    'fa fa-user-circle': 'circle-user',
    'fa fa-sign-out': 'log-out',
    'fa fa-envelope': 'mail',
    'fa fa-check-circle-o': 'check-circle',
    'fa fa-check-circle': 'check-circle',
    'fa fa-clock-o': 'clock',
    'fa fa-gift': 'gift',
    'fa fa-bolt': 'zap',
    'fa fa-shield': 'shield',
    'fa fa-credit-card': 'credit-card',
    'fa fa-paper-plane': 'send',
    'fa fa-plus': 'plus',
    'fa fa-minus': 'minus',
    'fa fa-arrow-left': 'arrow-left',
    'fa fa-chevron-down': 'chevron-down',
    'fa fa-instagram': 'instagram',
    'fa fa-facebook': 'facebook',
    'fa fa-twitter': 'twitter',
    'fa fa-linkedin': 'linkedin',
    'fa fa-angle-down': 'chevron-down',
    'fa fa-angle-right': 'chevron-right',
    'fa fa-arrow-right': 'arrow-right',
    'fa fa-check': 'check',
    'fa fa-times-circle': 'x-circle',
}

# Regex to match class="... uil uil-xxx ..." or class="... fa fa-xxx ..."
# We will use a regex search for the matching strings inside class attributes.

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Simple text replacement for exactly matched patterns in HTML
    # Because some classes could have other stuff, let's use regex:
    # We look for <i class="... fa fa-xxx ..."></i> and replace with <i data-lucide="mapped" class="..."></i>

    # Find all <i> tags
    i_tag_pattern = re.compile(r'<i\b([^>]*)> *</i>', re.IGNORECASE)
    
    def replacer(match):
        attributes = match.group(1)
        # Find class attribute
        class_match = re.search(r'class=(["\'])(.*?)\1', attributes, re.IGNORECASE)
        if not class_match:
            return match.group(0)

        classes = class_match.group(2)
        
        lucide_icon = None
        new_classes_list = []
        for cls_part in classes.split():
            new_classes_list.append(cls_part)

        # we need to check if any known combo exists
        class_str = ' '.join(new_classes_list)
        for key, val in MAPPING.items():
            if key in class_str:
                lucide_icon = val
                # Remove the keys
                class_str = class_str.replace(key, '')
                break
        
        # also check if just single class matches key from split
        if not lucide_icon:
            for c in new_classes_list:
                for key, val in MAPPING.items():
                    if key == c:
                        lucide_icon = val
                        class_str = class_str.replace(key, '')

        if lucide_icon:
            # Reconstruct class
            class_str = " ".join(class_str.split()) # clean up extra spaces
            
            # remove old class entirely
            new_attrs = re.sub(r'class=(["\']).*?\1', f'class="{class_str}"', attributes)
            return f'<i data-lucide="{lucide_icon}"{new_attrs}></i>'
        else:
            return match.group(0)

    content = i_tag_pattern.sub(replacer, content)

    # Some a tags might have fa fa-xyz directly on them
    a_tag_pattern = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    def a_replacer(match):
        attributes = match.group(1)
        inner = match.group(2)
        class_match = re.search(r'class=(["\'])(.*?)\1', attributes, re.IGNORECASE)
        if not class_match:
            return match.group(0)
            
        classes = class_match.group(2)
        lucide_icon = None
        for key, val in MAPPING.items():
            if key in classes:
                lucide_icon = val
                classes = classes.replace(key, '')
                break
                
        if lucide_icon:
            classes = " ".join(classes.split())
            new_attrs = re.sub(r'class=(["\']).*?\1', f'class="{classes}"', attributes)
            return f'<a{new_attrs}><i data-lucide="{lucide_icon}" class="inline-block w-4 h-4 mr-1"></i>{inner}</a>'
        return match.group(0)
        
    content = a_tag_pattern.sub(a_replacer, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            replace_in_file(os.path.join(root, file))

