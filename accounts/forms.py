from django import forms

from .utils import analyze_users_attendance_data


class UserAttendanceForm(forms.Form):
    excel_file = forms.FileField(
        label="Upload Excel File",
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get("excel_file")
        if not excel_file.name.endswith(".xlsx"):
            raise forms.ValidationError("Only .xlsx files are allowed")
        return excel_file

    def save(self):
        excel_file = self.cleaned_data.get("excel_file")
        df = analyze_users_attendance_data(excel_file)
        return df


class SimpleLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    # add class to email field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Email Address"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        # check password length
        if len(password) < 8:
            self.add_error("password", "Password must be at least 8 characters long")
        # check if email is valid
        if not email.endswith("@gmail.com"):
            self.add_error("email", "Email must be gmail")

        return cleaned_data
