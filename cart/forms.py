from django import forms
from .models import ProductSize


class AddToCartForm(forms.Form):
    """
    Форма для добавления товара в корзину.
    Включает поддержку размеров и обязательного количества.
    """
    size_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

        # Если продукт имеет доступные размеры, добавляем поле выбора размера
        if product:
            sizes = product.product_sizes.filter(stock__gt=0)
            if sizes.exists():
                self.fields['size_id'] = forms.ChoiceField(
                    choices=[(ps.id, ps.size.name) for ps in sizes],
                    required=True,
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    help_text="Select an available size.",
                    initial=sizes.first().id
                )
            else:
                # Если у товара нет размеров, удаляем поле
                del self.fields['size_id']

    def clean_size_id(self):
        """
        Проверка наличия выбранного размера среди доступных.
        """
        size_id = self.cleaned_data.get('size_id')
        if size_id:
            try:
                product_size = ProductSize.objects.get(id=size_id, product=self.product)
                if product_size.stock <= 0:
                    raise forms.ValidationError("Selected size is currently unavailable.")
            except ProductSize.DoesNotExist:
                raise forms.ValidationError("Invalid size selected.")
        return size_id