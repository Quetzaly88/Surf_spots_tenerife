# import statements
from django import forms  # used to create user input
from django.contrib.auth.forms import UserCreationForm  # build in for user registration
from .models import NovaUser  # imports the custom NovaUSer
from .models import SurfSpot
from .models import Comment

# define RegistrationForm class.
# adds email to the form, ensures valid email, uses widget appearance.


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter your email'
        })
    )

# nested class with the form that provides metadata about the form. Meta allowws to automatically populate fields.
    class Meta:
        model = NovaUser
        fields = ['username', 'email', 'password1', 'password2']


# used save Method
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class SurfSpotForm(forms.ModelForm):
    class Meta:
        model = SurfSpot
        fields = ['title', 'location', 'description', 'best_seasons', 'category'] #new field
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def clean_title(self):
        """
        Custom validation for the title field to enforce a max lenght
        and provide a custom message
        """
        title = self.cleaned_data.get('title')
        if len(title) > 50:
            raise forms.ValidationError("Title must not exceed 50 characters.")
        return title

    def clean_location(self):
        """
        Custom validation method for the location field
        """
        location = self.cleaned_data.get('location')
        if len(location) > 50:
            raise forms.ValidationError("Location must not exceed 50 characters.")
        return location

#Comment form for submitting user comments
class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content'] # Only include the content field for user input
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 3,
            })
        }
        labels = {
            'content': 'Add a Comment',
        }