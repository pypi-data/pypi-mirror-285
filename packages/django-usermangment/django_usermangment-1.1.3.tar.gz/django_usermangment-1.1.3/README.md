Quick start 
-----------
1. Add "django_usermangment" to your INSTALLED_APPS setting like this::
```
    INSTALLED_APPS = [
        ...
        'django_usermangment',
    ]
```
2. Include the django_usermangment URLconf in your project urls.py like this::
```
    path('user/', include('django_usermangment.urls')),
```
3. Run `python manage.py migrate` to create the django_usermangment models.
4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a user (you'll need the Admin app enabled).
5. Visit http://127.0.0.1:8000/user/ to create a user.