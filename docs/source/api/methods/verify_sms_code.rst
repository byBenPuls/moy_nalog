################
verify_sms_code
################

Верифицирует SMS-код и получает токены авторизации.

Возвращает: :obj:`AuthDetails`

- ``inn`` — ИНН пользователя
- ``token.value`` — access token
- ``token.expire_in`` — дата истечения токена
- ``token.refresh_value`` — refresh token для обновления


Использование
=====

.. code-block:: python

    auth: AuthDetails = await nalog.verify_sms_code(
        code="123456",
        challenge_token=challenge.challenge_token,
    )
    print(auth.inn)
