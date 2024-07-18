from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import argparse


def npi_validator(npi):
    """Validate NPI code against Luhn algorithm and raise ValidationError if invalid."""
    if not npi.isdigit() or len(npi) != 10:
        raise ValidationError(_("NPI must be a 10-digit number"), code="invalid")

    nums = [8, 0, 8, 4, 0]
    nums += [int(num) for num in str(npi)]
    chk_digit = nums.pop()
    nums.reverse()
    total = 0
    for index, number in enumerate(nums):
        debug = index % 2
        if index % 2:
            total += number
        else:
            number = number * 2
            if number >= 10:
                number = (number // 10) + (number % 10)
            total += number
    chksum = 10 - (total % 10)
    if chksum != chk_digit:
        raise ValidationError(_("Value is not a valid NPI number"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("value")
    npi_validator(parser.parse_args().value)
