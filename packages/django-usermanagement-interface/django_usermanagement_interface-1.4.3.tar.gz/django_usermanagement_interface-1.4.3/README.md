### django_usermanagement

[![PyPI version](https://badge.fury.io/py/django_usermanagement.svg)](https://badge.fury.io/py/django_usermanagement)
![Downloads](https://img.shields.io/pypi/dm/django_usermanagement)
![License](https://img.shields.io/badge/license-MIT-blue)

`django_usermanagement_interface` is a Django app designed for efficient user profile management. It integrates seamlessly with Django's authentication system, providing a robust framework for user management.

### Features
- **User Profile Management**: Create, update, and view user profiles.
- **Bootstrap 5 Integration**: Enhances UI with Bootstrap 5.
- **Image Handling with Pillow**: Manage user profile pictures.
- **Automatic File Cleanup**: Uses `django-cleanup` to manage file deletion.
- **JWT Authentication**: Secure authentication with `pyjwt`.
- **Secure Encryption**: Uses `cryptography` for enhanced security.
- **django-allauth and django-htmx Integration**: Easy setup for user authentication and dynamic content.

### Installation

1. **Install the package:**
   ```sh
   pip install django_usermanagement_interface
   ```

2. **Add to `INSTALLED_APPS`:**
   ```python
   INSTALLED_APPS = [
       ...
       'django_usermanagement',
   ]
   ```

3. **Include URLconf in `urls.py`:**
   ```python
   from django.urls import path, include

   urlpatterns = [
       ...
       path('user/', include('django_usermanagement.urls')),
   ]
   ```

4. **Run migrations:**
   ```sh
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```sh
   python manage.py createsuperuser
   ```

6. **Start the server:**
   ```sh
   python manage.py runserver
   ```

7. **Access the app:**
   - Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
   - User management: [http://127.0.0.1:8000/user-managment/](http://127.0.0.1:8000/user-managment/)

### URL Configuration

- `path('', ProfileView.as_view(), name="profile")`: Default profile view.
- `path('profile/', ProfileView.as_view(), name='profile')`: Profile view.
- `path('onboarding/', ProfileView.as_view(), name="profile-onboarding")`: Onboarding view.
- `path('profile/edit/', Profile_edit_View.as_view(), name='edit_profile')`: Edit profile view.
- `path('emailverify/', profile_email_verify, name="profile-email-verify")`: Email verification.
- `path('settings/', Profile_Settings_View.as_view(), name="profile-settings")`: Profile settings.
- `path('@<username>/', ProfileView.as_view(), name="profile")`: View profile by username.

### Models

**User Model:**
- `fields = ['username', 'email', 'password1', 'password2']`
- Widgets: Custom form controls for each field.
- Error handling and help texts.

**Profile Model:**
- `fields = ['profile_pic','display_name', 'bio', 'location', 'birth_date', 'website', 'facebook', 'twitter', 'instagram', 'linkedin']`
- Widgets: Custom form controls for each field.

### Forms

**UserForm:**
```python
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

**ProfileForm:**
```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic','display_name', 'bio', 'location', 'birth_date', 'website', 'facebook', 'twitter', 'instagram', 'linkedin']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
        }
```

### Templates and Static Files

Include these in your `MANIFEST.in`:
```
include README.md
include LICENSE
recursive-include usermanagement/templates *
recursive-include usermanagement/static *
```

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contributing

Feel free to submit pull requests, create issues, or suggest features.

### Contact

Author: Hamed Jamali  
Email: hamed.jamali.software@gmail.com

### Hashtags

#Django #UserManagement #Python #WebDevelopment #OpenSource

For more details, visit the [GitHub repository](https://github.com/hamed-jamali-software/usermanagement).