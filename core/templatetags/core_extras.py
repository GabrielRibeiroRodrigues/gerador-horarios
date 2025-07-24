"""
Template tags personalizados para o sistema de horários escolares.
"""
from django import template

register = template.Library()

@register.filter
def lookup(dict_obj, key):
    """
    Filtro para acessar valores de dicionário no template.
    
    Uso: {{ dict|lookup:key }}
    """
    if hasattr(dict_obj, 'get'):
        return dict_obj.get(key, None)
    return None

@register.filter
def add_str(value, arg):
    """
    Filtro para concatenar strings.
    
    Uso: {{ valor|add_str:"-"|add_str:outro_valor }}
    """
    return str(value) + str(arg)

@register.filter
def get_item(dictionary, key):
    """
    Outro filtro para acessar itens de dicionário.
    """
    return dictionary.get(key)
