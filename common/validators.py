from datetime import date

from rest_framework.exceptions import ValidationError


def validate_user_age(birthdate):
    if birthdate in (None, ''):
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

    if isinstance(birthdate, str):
        try:
            birthdate = date.fromisoformat(birthdate)
        except ValueError as exc:
            raise ValidationError('Укажите дату рождения, чтобы создать продукт.') from exc

    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError('Вам должно быть 18 лет, чтобы создать продукт.')

    return birthdate


def get_birthdate_from_request(request):
    auth = getattr(request, 'auth', None)
    if isinstance(auth, dict):
        return auth.get('birthdate')

    user = getattr(request, 'user', None)
    return getattr(user, 'birthdate', None)


def validate_product_creation_age(request):
    birthdate = get_birthdate_from_request(request)
    return validate_user_age(birthdate)
