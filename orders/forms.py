from django import forms
from .models import Order

class DeliveryMethodForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_method']
        widgets = {
            'delivery_method': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_method'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['delivery_method'].label = 'Select Delivery Method'