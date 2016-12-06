"""Flask middleware definitions. This is also where template filters are defined.

To be imported by the application.current_app() factory.
"""

import locale

from logging import getLogger

from flask import current_app, render_template, request
from markupsafe import Markup

from imp_flask.core.email import send_exception

LOG = getLogger(__name__)


# Setup default error templates.
@current_app.errorhandler(400)
@current_app.errorhandler(403)
@current_app.errorhandler(404)
@current_app.errorhandler(500)
def error_handler(e):
    code = getattr(e, 'code', 500)  # If 500, e == the exception.
    if code == 500:
        # Send email to all ADMINS.
        exception_name = e.__class__.__name__
        view_module = request.endpoint
        send_exception('{} exception in {}'.format(exception_name, view_module))
    return render_template('{}.html'.format(code)), code


# Template filters.
@current_app.template_filter()
def whitelist(value):
    """Whitelist specific HTML tags and strings.

    Positional arguments:
    value -- the string to perform the operation on.

    Returns:
    Markup() instance, indicating the string is safe.
    """
    translations = {
        '&amp;quot;': '&quot;',
        '&amp;#39;': '&#39;',
        '&amp;lsquo;': '&lsquo;',
        '&amp;nbsp;': '&nbsp;',
        '&lt;br&gt;': '<br>',
    }
    escaped = str(Markup.escape(value))  # Escapes everything.
    for k, v in translations.items():
        escaped = escaped.replace(k, v)  # Un-escape specific elements using str.replace.
    return Markup(escaped)  # Return as 'safe'.


@current_app.template_filter()
def euro(value):
    """Formats the float value into two-decimal-points euro amount.
    From http://flask.pocoo.org/docs/templating/

    Positional arguments:
    value -- the string representation of a float to perform the operation on.

    Returns:
    Euro formatted string.
    """
    return locale.currency(float(value), grouping=True)


@current_app.template_filter()
def sum_key(value, key):
    """Sums up the numbers in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return sum(values)


@current_app.template_filter()
def max_key(value, key):
    """Returns the maximum value in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return max(values)


@current_app.template_filter()
def average_key(value, key):
    """Returns the average value in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return float(sum(values)) / (len(values) or float('nan'))

