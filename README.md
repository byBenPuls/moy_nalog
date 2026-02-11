# Moy Nalog

Неофициальная асинхронная библиотека **moy_nalog** предоставляет API для автоматизации отчётности самозанятых на [lknpd.nalog.ru](https://npd.nalog.ru/web-app/).


Авторизация по логину и паролю:

```python
import asyncio

from moy_nalog import MoyNalog

nalog = MoyNalog("1234567890", "MyStrongPassword")


async def main():
    await nalog.add_income(
        "Предоставление информационных услуг #970/2495", amount=1000, quantity=1
    )


asyncio.run(main())
```

Авторизация по номеру телефона (SMS):

```python
import asyncio

from moy_nalog import MoyNalog

nalog = MoyNalog(phone="+79991234567")


async def main():
    challenge = await nalog.request_sms_code()
    code = input("Введите код из SMS: ")
    await nalog.verify_sms_code(code, challenge.challenge_token)

    await nalog.add_income(
        "Предоставление информационных услуг #970/2495", amount=1000, quantity=1
    )


asyncio.run(main())
```