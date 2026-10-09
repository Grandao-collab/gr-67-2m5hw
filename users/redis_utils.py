from django.core.cache import cache

CONFIRMATION_PREFIX = "confirmation_code"


def confirmation_key(user_id):
    return f"{CONFIRMATION_PREFIX}:{user_id}"


def save_confirmation_code(user_id, code, ttl=300):
    cache.set(confirmation_key(user_id), code, timeout=ttl)
    return code


def get_confirmation_code(user_id):
    return cache.get(confirmation_key(user_id))


def consume_confirmation_code(user_id, code):
    saved_code = get_confirmation_code(user_id)
    if saved_code != code:
        return False
    cache.delete(confirmation_key(user_id))
    return True


def delete_confirmation_code(user_id):
    cache.delete(confirmation_key(user_id))
