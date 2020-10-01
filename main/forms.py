from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Footage

class NewUserForm(UserCreationForm): #inherit from UserCreationForm
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    # when the form got saved
    def save(self, commit=True): # commit data, chuck in the db
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class FootageForm(forms.ModelForm):
    class Meta:
        model = Footage
        fields = ('video_title', 'upload_date', 'video')