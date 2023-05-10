import datetime

from django.contrib.auth import authenticate
from help_to_heat.portal import models

from . import utils


def login(client, email, password):
    page = client.get(utils.make_url("/accounts/login/"))
    form = page.get_form()
    form["login"] = email
    form["password"] = password
    page = form.submit()
    page = page.follow()
    return page


def login_as_service_manager(client, email, password):
    if models.User.objects.filter(email=email).exists():
        user = models.User.objects.get(email=email).delete()
    user = models.User.objects.create_user(email, password)
    user.invite_accepted_at = datetime.datetime.now()
    user.is_supplier_admin = True
    user.save()
    page = login(client, email, password)
    assert page.has_text("Logout")
    return page


def test_service_manager_add_supplier():
    client = utils.get_client()
    supplier_name = f"Mr Flibble's Energy Co - {utils.make_code}"
    page = login_as_service_manager(client, email="service-manager@example.com", password="Fl1bbl3Fl1bbl3")
    page = page.click(contains="Add a new energy supplier")
    form = page.get_form()
    form['supplier_name'] = supplier_name
    page = form.submit().follow()
    assert page.has_one(f'''th:contains("{supplier_name}")''')
