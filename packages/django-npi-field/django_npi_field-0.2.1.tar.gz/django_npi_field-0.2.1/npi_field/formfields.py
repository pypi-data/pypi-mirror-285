from django.forms.fields import CharField
from npi_field.validators import npi_validator
from npi_field.widgets import NPIWidget
from django.utils.translation import gettext_lazy as _


class NPIField(CharField):
    default_validators = [npi_validator]
    widget = NPIWidget
    label = _("NPI number")
    default_error_messages = {
        "invalid": _("Input must be a valid NPI number"),
    }
    help_text = _(
        "Please enter the provider's or facility's National Provider Identifier number"
    )

    def __init__(self, *args, **kwargs):
        self.max_length = 10
        self.min_length = 10
        super().__init__(*args, **kwargs)
        self.error_messages |= self.default_error_messages

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value
