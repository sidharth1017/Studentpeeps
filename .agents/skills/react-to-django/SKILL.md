---
name: react-to-django
description: Converts React design components into Django HTML templates. Use when migrating React UI elements into the Django frontend.
---
# React to Django Conversion Skill

When this skill is triggered, you must strictly follow these directory rules:
- **Source Directory:** Always read the React reference from `_reference-react-design/`
- **Destination Directory:** Always write the converted Django templates to my django code which you already have access to.

When converting React components from the reference folder to Django templates, strictly follow these rules:

1. **Analyze the React Component:** Review the React file to understand the HTML structure, CSS classes, and static asset usage.
2. **Translate Logic to Django Tags:** Replace React props and state variables with Django template variables (`{{ variable_name }}`). Convert `.map()` iterations into `{% for item in items %}` loops, and ternary operators/conditionals into `{% if condition %}` blocks.
3. **Handle Static Files:** Convert standard image or asset paths into Django's static format (e.g., `{% static 'images/logo.png' %}`). Ensure `{% load static %}` is included at the top of the template.
4. **Preserve Styling:** Keep all CSS utility classes and structure exactly as they appear in the React component so the final design matches the reference perfectly.
