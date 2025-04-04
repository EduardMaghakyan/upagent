from django import forms
from .models import FlowMonitor, FlowStep

class FlowMonitorBasicForm(forms.ModelForm):
    """Form for the first step of flow creation - basic information"""
    class Meta:
        model = FlowMonitor
        fields = ['name', 'description', 'starting_url', 'interval_seconds']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'Checkout Flow'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'rows': 3,
                'placeholder': 'Describe what this flow checks for'
            }),
            'starting_url': forms.URLInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'https://example.com/product'
            }),
            'interval_seconds': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set choices for interval
        self.fields['interval_seconds'].widget.choices = [
            (3600, 'Every hour'),
            (7200, 'Every 2 hours'),
            (14400, 'Every 4 hours'),
            (28800, 'Every 8 hours'),
            (43200, 'Every 12 hours'),
            (86400, 'Daily'),
        ]


class FlowStepForm(forms.ModelForm):
    """Form for adding a single step to the flow"""
    class Meta:
        model = FlowStep
        fields = ['action_type', 'description', 'url', 'element_description', 
                 'input_value', 'timeout_seconds', 'wait_time_seconds']
        widgets = {
            'action_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
            }),
            'description': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'Click Add to Cart button'
            }),
            'url': forms.URLInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'https://example.com/checkout'
            }),
            'element_description': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'Add to Cart'
            }),
            'input_value': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'placeholder': 'test@example.com'
            }),
            'timeout_seconds': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'min': 1,
                'max': 60
            }),
            'wait_time_seconds': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500',
                'min': 0,
                'max': 10
            }),
        }

    def __init__(self, *args, **kwargs):
        self.step_number = kwargs.pop('step_number', 1)
        super().__init__(*args, **kwargs)
        
        # Set some nice defaults
        self.fields['timeout_seconds'].initial = 10
        self.fields['wait_time_seconds'].initial = 1