from django import template

register = template.Library()

@register.filter
def sklanjaj_vsecke(stevilo):
    if stevilo % 100 == 1:
        return "všeček"
    elif stevilo % 100 == 2:
        return "všečka"
    elif stevilo % 100 == 3 or stevilo % 100 == 4:
        return "všečki"
    else:
        return "všečkov" 