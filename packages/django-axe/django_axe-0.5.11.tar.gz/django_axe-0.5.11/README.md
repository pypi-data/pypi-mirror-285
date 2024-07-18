# Django Axe

This project is a Django module designed to extend the functionality of Django applications. It provides a set of models, views, and templates that can be integrated into existing Django projects to add new features or improve existing ones.

## Installation

To install this module, follow these steps:

1. Clone this repository into your Django project directory:
    ```bash
    git clone https://github.com/brahmaduttau/django_axe
    ```
2. Add the app to your INSTALLED_APPS in your project's settings.py:
    ```python
    INSTALLED_APPS = [
        ...
        'django_axe',
        ...
    ]
    ```

3. Include the app's URLs in your project's urls.py:
from django.urls import path, include
```python
urlpatterns = [

    path('axe/', include('django_axe.urls')),
    
]
```
