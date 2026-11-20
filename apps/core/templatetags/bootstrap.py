"""Small helpers for rendering Django forms with Bootstrap, without an extra dependency."""

from django import forms, template

register = template.Library()

# Widgets that Bootstrap styles with their own class; everything else gets 'form-control'.
_CHECKBOX = (forms.CheckboxInput,)
_SELECT = (forms.Select, forms.SelectMultiple)
_UNSTYLED = (forms.RadioSelect, forms.CheckboxSelectMultiple, forms.HiddenInput)


@register.filter
def bootstrap_field(bound_field):
    """Render a form field's widget with the matching Bootstrap class.

    Adds ``is-invalid`` when the field has errors. Classes already set on the widget are kept.
    """
    widget = bound_field.field.widget
    classes = widget.attrs.get('class', '').split()
    if isinstance(widget, _CHECKBOX):
        classes.append('form-check-input')
    elif isinstance(widget, _SELECT):
        classes.append('form-select')
    elif not isinstance(widget, _UNSTYLED):
        classes.append('form-control')
    if bound_field.errors and not isinstance(widget, forms.HiddenInput):
        classes.append('is-invalid')
    return bound_field.as_widget(attrs={'class': ' '.join(classes)} if classes else None)
