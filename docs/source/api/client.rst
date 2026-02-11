########
MoyNalog
########

Экземпляр клиента может быть создан из :code:`moy_nalog.MoyNalog` (:code:`from moy_nalog import MoyNalog`).
Кроме того, методы не могут быть использованы без экземпляра с данными для авторизации.


Авторизация по логину и паролю
==============================

Классический способ авторизации через ИНН (или телефон) и пароль от ЛК ФНС:

.. code-block:: python

    from moy_nalog import MoyNalog

    async with MoyNalog(login="1234567890", password="MyPassword") as nalog:
        user = await nalog.get_user_info()

Авторизация происходит автоматически при первом вызове любого метода API.


Авторизация по SMS
==================

Авторизация через код из SMS-сообщения. Не требует пароля, только номер телефона:

.. code-block:: python

    from moy_nalog import MoyNalog

    async with MoyNalog(phone="79171234567") as nalog:
        # Шаг 1: запросить SMS-код на телефон
        challenge = await nalog.request_sms_code()
        # challenge.challenge_token — токен для верификации
        # challenge.expire_in — время жизни кода (120 сек)

        # Шаг 2: пользователь вводит код из SMS
        code = input("Введите код из SMS: ")

        # Шаг 3: верифицировать код и получить токены
        auth = await nalog.verify_sms_code(
            code=code,
            challenge_token=challenge.challenge_token,
        )
        # auth.inn — ИНН пользователя
        # auth.token.value — access token
        # auth.token.refresh_value — refresh token

        # Шаг 4: теперь можно использовать любые методы
        user = await nalog.get_user_info()

.. warning::

    При SMS-авторизации перед вызовом методов API (``add_income``, ``get_user_info`` и др.)
    необходимо сначала пройти верификацию через ``verify_sms_code()``.
    Иначе будет вызвано исключение ``AuthorizationError``.
