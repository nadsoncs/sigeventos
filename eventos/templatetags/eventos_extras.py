from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')

@register.filter(name='addclass')
def add_class(value, css_class):
    string = str(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class), match.group(1))
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value

placeholder_re = re.compile(r'(?<=placeholder=["\'])(.*)(?=["\'])')

@register.filter(name='addplaceholder')
def add_placeholder(value, placeholder_text):
    string = str(value)
    match = placeholder_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (placeholder_text, placeholder_text,
                                                    placeholder_text, placeholder_text), match.group(1))
        if not m:
            return mark_safe(placeholder_re.sub(match.group(1) + " " + placeholder_text,
                                          string))
    else:
        return mark_safe(string.replace('>', ' placeholder="%s">' % placeholder_text))
    return value