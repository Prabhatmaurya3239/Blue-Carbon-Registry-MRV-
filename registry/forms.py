from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ProjectSite, PlantationRecord
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization = forms.CharField(max_length=200, required=False)
    role = forms.ChoiceField(choices=User.USER_ROLES, widget=forms.Select())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'organization', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ProjectSiteForm(forms.ModelForm):
    class Meta:
        model = ProjectSite
        fields = ['name', 'location_lat', 'location_lng', 'ecosystem_type', 'area_ha']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location_lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'location_lng': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'ecosystem_type': forms.Select(attrs={'class': 'form-select'}),
            'area_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PlantationRecordForm(forms.ModelForm):
    class Meta:
        model = PlantationRecord
        fields = ['project_site', 'date_planted', 'species', 'number_of_plants', 'uploaded_images']
        widgets = {
            'project_site': forms.Select(attrs={'class': 'form-select'}),
            'date_planted': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'species': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_plants': forms.NumberInput(attrs={'class': 'form-control'}),
            'uploaded_images': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project_site'].queryset = ProjectSite.objects.filter(created_by=user)
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})