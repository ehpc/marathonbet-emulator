# Эмулятор ставок

## Требования

Для работы требуется установленный пакет selenium для python
```
pip install -U selenium
```

А также обязательно установить драйвер браузера Firefox.
```
https://github.com/mozilla/geckodriver/releases
```

Для GUI-режима обязательно наличие полноценного firefox.

На linux-сервере возможно придётся ещё повозиться с интеграцией всего этого.

## Headless

Эмулятор работает как в полноценном GUI-режиме, так и headless.
То есть он может открыть окно и щелкать прямо на экране, либо открыться в фоне и щелкать где-то там под капотом.

Для переключения режимов используется флаг `headless` в конструкторе.

## Успешность ставки

Если сделать ставку по какой-то причине нет возможности, вылетит Exception. Его нужно отловить и обработать.
