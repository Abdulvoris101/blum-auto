import re

from apps.common.exceptions import InvalidRequestException
from utils import text


async def validatePhoneNumber(phoneNumber):
    # Regular expression to validate phone number
    pattern = r'^\+\d+$'

    if not re.match(pattern, phoneNumber):
        raise InvalidRequestException(messageText=text.INVALID_PHONE_NUMBER_FORMAT.value)


def validateAmount(amount) -> float:
    try:
        amount = float(amount)
    except ValueError:
        raise InvalidRequestException(messageText=text.INCORRECT_AMOUNT.value)

    if amount < 1:
        raise InvalidRequestException(messageText=text.MINIMAL_AMOUNT.value)

    return amount
