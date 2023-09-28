from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Menuitem, Reservation, Profile, Coupons
from datetime import date
from decimal import Decimal


class CouponForm(forms.Form):
    code = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter coupon code'}))

class CreateCouponForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Menuitem.objects.all().values_list('name', flat=True).order_by('category'),
        to_field_name='name',
        label='Product',
    )
    coupon_type = forms.ChoiceField(
        choices=Coupons.COUPON_TYPE_CHOICES,  # Use the choices from your model
    )
    class Meta:
        model = Coupons
        fields = ['coupon_type','percentage', 'code', 'product', 'is_unique']
    def __init__(self, *args, **kwargs):
        super(CreateCouponForm, self).__init__(*args, **kwargs)
        self.fields['product'].required = False
        self.fields['product'].widget.attrs.update({'class': 'conditional-hidden'})

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': '', 'class': 'your-css-class'}),  # Remove help_text here
    )
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


class DateSelectionForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today():
            raise forms.ValidationError("Please select a date in the future")
        return selected_date


from django.forms.widgets import TimeInput
from datetime import datetime, timedelta



from django.forms.widgets import Select
from datetime import time

class CustomTimeWidget(Select):
    def __init__(self, attrs=None, hour_step=None, minute_step=None, *args, **kwargs):
        self.hour_step = hour_step or 1
        self.minute_step = minute_step or 15
        super().__init__(attrs=attrs, choices=self._get_choices(), *args, **kwargs)

    def _get_choices(self):
        choices = []
        for hour in range(8, 24, self.hour_step):
            for minute in range(0, 60, self.minute_step):
                if minute == 0:
                    choices.append((time(hour=hour, minute=minute), f'{hour:02d}:{minute:02d}'))
                else:
                    choices.append(
                        (time(hour=hour, minute=minute), f'{hour:02d}:{minute:02d}')
                    )
        return choices



from django import forms
from datetime import time

class CustomTimeField(forms.TimeField):
    def __init__(self, *args, **kwargs):
        interval = 15  # time interval in minutes
        choices = [(time(hour=h, minute=m).strftime('%H:%M'), time(hour=h, minute=m).strftime('%I:%M %p')) for h in range(8, 24) for m in range(0, 60, interval)]
        super().__init__(*args, **kwargs)
        self.widget = forms.Select(choices=choices)


    def to_python(self, value):
        if value is None:
            return None
        try:
            return super().to_python(value)
        except forms.ValidationError:
            raise forms.ValidationError("Invalid time format. Please select a valid time in 15-minute increments (e.g. 12:15, 12:30, 12:45, 13:00).")


class ReservationForm(forms.ModelForm):
    starttime = forms.TimeField(widget=CustomTimeWidget(hour_step=1, minute_step=15))
	
    endtime = forms.TimeField(widget=CustomTimeWidget(hour_step=1, minute_step=15))
    #endtime = CustomTimeField()
    #starttime = CustomTimeField()

    class Meta:
        model = Reservation
        fields = ('party_size', 'name', 'email', 'starttime', 'endtime')
        

    def __init__(self, *args, **kwargs):
        available_times = kwargs.pop('available_times', None)
        super().__init__(*args, **kwargs)
        if available_times:
            self.fields['starttime'].choices = available_times
            self.fields['endtime'].choices = available_times

	
class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        help_text=''
    )
    class Meta:
        model = Profile
        fields = ['username', 'email', 'points']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']

class CouponRedemptionForm(forms.Form):
    selected_coupon = forms.ChoiceField(
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        available_coupons = kwargs.pop('available_coupons', {})
        super(CouponRedemptionForm, self).__init__(*args, **kwargs)

        # Generate choices dynamically based on available_coupons dictionary keys
        self.fields['selected_coupon'].choices = [
            (key, f"{coupon['name']} - {coupon['percentage']}% Off" if coupon['type'] == 'percentage' else f"{coupon['name']} - {coupon['fixed_amount']} Forint Off")
            for key, coupon in available_coupons.items()
        ]
