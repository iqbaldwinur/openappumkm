from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from .models import TransaksiBelanja, Anggaran, MasterUser, MasterBelanja, RencanaAnggaranBelanja
from django.forms import DateInput


class TransaksiForm(forms.ModelForm):
    class Meta:
        model = TransaksiBelanja
        fields = ['kode_belanja', 'urai_belanja', 'tgl_belanja', 'realisasi', 'sisa', 'saldo']
        widgets = {
            'tgl_belanja': DateInput(attrs={'type': 'date'}),
        }

    
class AnggaranForm(forms.ModelForm):
    class Meta:
        model = Anggaran
        fields = ['belanja', 'anggaran', 'user', 'rencana_anggaran_belanja']


class MasterUserForm(forms.ModelForm):
    class Meta:
        model = MasterUser
        fields = ['username', 'password', 'role']

class MasterBelanjaForm(forms.ModelForm):
    class Meta: 
        model = MasterBelanja
        fields = ['nama']

class RencanaAnggaranBelanjaForm(forms.ModelForm):
    class Meta: 
        model = RencanaAnggaranBelanja
        fields = ['nama_keperluan', 'tgl_mulai', 'tgl_berakhir', 'user', 'deskripsi']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-field'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-field'}))
    
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MasterUser
        fields = ('username', 'role', 'email', 'fullname', 'nomortelephone', 'is_active', 'is_staff')
    
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = MasterUser
        fields = ['username', 'role', 'is_active', 'is_staff']



        
