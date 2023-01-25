from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Menuitem

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class NewItemForm(forms.ModelForm):

		name = forms.CharField(max_length=100)
		type = forms.BooleanField()
		category = forms.CharField(max_length=100)
		price = forms.IntegerField()
		
		class Meta:
			model = Menuitem
			fields = ("name", "type", "category", "price")

		def save(self, commit=True):
			item = super(NewItemForm, self).save(commit=False)
			item.name = self.cleaned_data['name']
			item.type = self.cleaned_data['type']
			item.category = self.cleaned_data['category']
			item.price = self.cleaned_data['price']
			if commit:
				item.save()
			return item