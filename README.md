# Betting Emulator for Marathonbet.ru

## Requirements

```
pip install -U selenium
```

Install geckodriver from `https://github.com/mozilla/geckodriver/releases`.

For GUI-mode you will need a fully functional Firefox installation.

## Headless

Use `headless` flag in constructor.

## Flow

If betting wasn't successful an Exception will be thrown. You should catch it.
