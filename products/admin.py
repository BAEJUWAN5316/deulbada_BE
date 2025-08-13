from django.contrib import admin
from django import forms
from .models import Product, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Custom form for the Product admin
class ProductAdminForm(forms.ModelForm):
    # A text field for comma-separated tags
    tag_input = forms.CharField(
        label='Tags (comma-separated)',
        required=False,
        help_text='Enter tags separated by commas. e.g., 사과, 청송, 여름'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing product, populate the tag_input field
        if self.instance and self.instance.pk:
            self.fields['tag_input'].initial = ', '.join(t.name for t in self.instance.tags.all())
        # Make the original tags field not required as we are using tag_input
        if 'tags' in self.fields:
            self.fields['tags'].required = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('id', 'seller', 'name', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    
    # Define fieldsets to control the order and display our custom field
    # and hide the original 'tags' field.
    fieldsets = (
        (None, {
            'fields': ('seller', 'name', 'description', 'price', 'is_sold')
        }),
        ('Details', {
            'fields': ('category', 'variety', 'region', 'harvest_date', 'sales_link', 'image_urls')
        }),
        ('Tags', {
            'fields': ('tag_input',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Save the product instance first
        super().save_model(request, obj, form, change)

        # Get the tag string from the form's cleaned data
        tag_input_string = form.cleaned_data.get('tag_input', '')

        # Clear existing tags
        obj.tags.clear()

        # If there's input, process it
        if tag_input_string:
            tag_names = [name.strip() for name in tag_input_string.split(',') if name.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                obj.tags.add(tag)
