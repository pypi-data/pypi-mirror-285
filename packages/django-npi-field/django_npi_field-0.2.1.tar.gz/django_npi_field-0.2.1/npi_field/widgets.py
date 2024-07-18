from django.forms.widgets import TextInput


class NPIWidget(TextInput):
    input_type = "text"

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs = {
            "pattern": r"\d{10}",
            "title": "A 10-digit NPI number",
            "required": self.is_required,
        }
