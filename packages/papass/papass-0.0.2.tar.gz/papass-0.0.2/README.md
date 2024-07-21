<h1 align="center">
  papass
</h1>

[![PyPI](https://img.shields.io/pypi/v/papass.svg)](https://pypi.org/project/papass/)
[![CI](https://github.com/rainij/papass/actions/workflows/ci.yml/badge.svg)](https://github.com/rainij/papass/actions/workflows/ci.yml)

**This is a work in progress**

**papass** generates passphrases following the
[diceware](https://theworld.com/~reinhold/diceware.html) approach as proposed by Arnold
G. Reinhold.

# Usage

Assuming you have a wordlist file `wordlist.txt` you can run the following command to
generate a random list of five words:

```bash
$ papass -c 5 -w /path/to/wordlist.txt
Phrase: anthem hamstring transport doorbell circle
Entropy: 64.62406251802891
```

By default this uses the system's most secure random number generator. To use physical dice add `-r dice`.

You can download a wordlist designed for passphrases from the
[EFF](https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases). You might
need to remove the dice numbers, that is, change a line like this

```
11114     abide
```

into

```
abide
```

# Development
Create a virtual environment and do

```bash
$ pip install -r requirements.txt .[dev]
```

Run unit tests via

```bash
$ pytest
```

Formatting and linting is done via [ruff](https://github.com/astral-sh/ruff).

```bash
$ ruff format
$ ruff check --fix
```
