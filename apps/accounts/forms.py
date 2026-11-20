from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('display_name', 'bio', 'phone_number', 'avatar')
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}
