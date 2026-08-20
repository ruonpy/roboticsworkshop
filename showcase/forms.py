from django.contrib.auth.forms import AuthenticationForm


class LowercaseUsernameAuthenticationForm(AuthenticationForm):

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return username.lower() if username else username