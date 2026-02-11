################
request_sms_code
################

Отправляет SMS-код на номер телефона, указанный при создании экземпляра ``MoyNalog``.

Возвращает: :obj:`SmsChallenge`

- ``challenge_token`` — токен для передачи в ``verify_sms_code()``
- ``expire_date`` — дата истечения кода
- ``expire_in`` — время жизни кода в секундах (обычно 120)


Использование
=====

.. code-block:: python

    challenge: SmsChallenge = await nalog.request_sms_code()
    print(challenge.challenge_token)  # UUID токен
    print(challenge.expire_in)  # 120
