from django.contrib import admin
from django.apps import apps

# Get all models from the 'core.db' module
app_models = apps.get_app_config('core').get_models()

# Register each model dynamically
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # If a model is already registered, skip it
        pass