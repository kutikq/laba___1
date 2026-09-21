VARIANT_NUMBER = 12
VARIANT_DESCRIPTION = "Наличие строчных и прописных букв, а также цифр"


def check_password(password: str) -> bool:
    has_lower = False
    has_upper = False
    has_digit = False

    for ch in password:
        if ch.islower():
            has_lower = True
        elif ch.isupper():
            has_upper = True
        if ch.isdigit():
            has_digit = True

    return has_lower and has_upper and has_digit


def requirements_text() -> str:
    return (
        f"Вариант №{VARIANT_NUMBER}: {VARIANT_DESCRIPTION}.\n"
        "Пароль должен содержать хотя бы одну строчную букву,\n"
        "хотя бы одну прописную букву и хотя бы одну цифру."
    )
