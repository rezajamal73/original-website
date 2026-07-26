from django import forms
from captcha.fields import CaptchaField


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "نام کاربری را وارد کنید",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "••••••••••",
        })
    )

    captcha = CaptchaField(
        label="کد امنیتی",
        error_messages={
            "invalid": "کد امنیتی صحیح نیست."
        },
    )