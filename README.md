# Check eligibility for Great British Insulation Scheme

Formerly known as "Help to Heat".

## Initial Setup

1. From the project root, run `cp envs/web.template envs/web`
2. Populate the OS API key into the OS_API_KEY variable in `envs/web`. The key can be found in Keeper. Please only use a single value (i.e. `["my_key_here"]`), rather than all of the keys that are stored in Keeper, in order to avoid needing to rotate all of the keys if your local environment is accidentally leaked.

## Using Docker

1. [Install Docker](https://docs.docker.com/get-docker/) on your machine
2. `docker-compose up --build --force-recreate web`
3. It's now available at: http://localhost:8012/

Migrations are run automatically at startup, and suppliers are added automatically at startup

## Running tests

    make test

## Checking code

    make check-python-code

## Deployment

We have three branches linked to environments: develop, staging, and main. Committing to any of these will trigger a release to the relevant environment. To merge to main, the `production release` label must be applied to your pull request.

## Migration

All migrations are created by Django.
Go inside Docker - `help-to-heat` - `web-1` and run the following command in Terminal:

    python manage.py makemigrations

then restart the container. All required migrations will be created automatically.

## Translations

### Summary

1. Wrap user-facing strings in a translation function (typically just `_`).
2. Run `make extract-translations`
3. Update `help_to_heat/locale/cy/LC_MESSAGES/django.po` with Welsh translations.
4. Run `make compile-translations`.

### Walkthrough

Any user-readable text in the application will likely need translation (only exceptions are things like phone numbers
or strings that consist entirely of proper nouns). This is done by passing the text through a translation function.

The simplest and most common version of this is a straightforward string of text in a template. Given the following:

```html
<p>This is some text!</p>
```

This template content can be translated by using the `_` function, which is globally available within templates:

```html
<p>{{_("This is some text!")}}</p>
```

Any time you add/change/remove a translated string from the code, you will need to run `make extract-translations`.
This will update the "message file", `help_to_heat/locale/cy/LC_MESSAGES/django.po`, which is where we provide
translations. For any added translations, check that they have been added to the message file, and add their translation
to the empty string at the bottom of the entry. For any removed translations, confirm that they have been commented out
automatically by the extractor, and delete the commented entry once you have checked it. Changes to English strings will
appear as the old one being deleted and the new one being added.

If the same English string appears in the code in multiple places, the messages file will only include it once with the
multiple locations it appears listed in a comment on the message entry (if you need the same English string to be
translated to different Welsh text in different places, see Context below).

**If a message is tagged as `fuzzy`, then it will be ignored at runtime.** This means it was very close to another
translation, and the extractor guessed they might be the same. You will need to delete the "fuzzy" tag to have it
actually be used. The speculative translation will also be added as a comment; you will probably need to delete that
and replace it with the actual translation.

Once you have updated the message file, then you will need to run `make compile-translations` to compile it to
`django.mo` in the same folder. With the translations compiled, you can restart the server, and the new translations
should show up when the language is set to Welsh.

There are a few variations/additional wrinkles you may need to consider when translating strings, which are detailed in
the subsections below.

### Python code

If the text is in a Python file rather than template, then you will need to import the translation function using
`from django.utils.translation import gettext as _` (possibly replacing `gettext` with a different function, see
below).

The extractor should recognise `_` or any of the translation function names (`gettext`, `gettext_lazy`, `pgettext`,
`pgettext_lazy`) when detecting translatable strings. Currently only `_` is surfaced in templates, so if you need to
make use of the other variants within templates, it will need to be exposed as a global (in `help_to_heat/jinja2.py`).

### Static data

If the data is created/loaded once at launch and referenced thereafter (e.g. a dictionary of radio button labels for a
form), then you will need to use `gettext_lazy` instead of `gettext`, in order to have the language be checked each time
the string is used (rather than once on server load).

### Context

In some cases the English string alone is not enough to identify the translation (e.g. "Close" as in quit and "Close" as
in nearby, or entire sentences that are the same in English but have different translations in Welsh depending on the
context they are used in). In these cases, you will need to use `pgettext` instead of `gettext`. This takes an extra
first argument, the "context" of the translation. Instead of just using the English string as a key, this will use
context + English, e.g.

```python
pgettext("yes no question option", "Yes")
```

If you need both context _and_ lazy, then there is `pgettext_lazy` combining the two.

### Interpolation

If you need to interpolate values into a translated string, this can be done using named placeholders, e.g.

```python
_("Your details have been submitted to %(supplier)s") % { "supplier": chosen_supplier }
```

The `%` operator takes a dictionary of values to interpolate. Within the string itself you must include a character at
the end of the interpolation denoting the type of data being interpolated (in this case, `s` for string).
