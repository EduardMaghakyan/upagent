from django import forms
from .models import SupportRequest


class ContactForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ["subject", "message"]

        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500",
                    "placeholder": "How can we help you?",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500",
                    "rows": 6,
                    "placeholder": "Please describe your issue or question in detail...",
                }
            ),
        }
