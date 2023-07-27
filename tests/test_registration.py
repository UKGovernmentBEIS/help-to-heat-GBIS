import datetime

import freezegun
from django.contrib.auth import authenticate
from django.utils import timezone

from help_to_heat.portal import models

from . import utils


def test_registration():
    client = utils.get_client()
    page = client.get("/portal/")
    assert page.status_code == 302


def invite_user(name, email, password, role, try_fake_email=False, skip_otp=False):
    utils.wipe_emails()
    client = utils.get_client()
    page = utils.login_as_team_leader(client)
    page = page.click(contains="Add a new team member or leader")

    form = page.get_form()
    form["team-role"] = role
    page = form.submit().follow()

    form = page.get_form()
    form["user-name"] = name
    form["user-email"] = email
    page = form.submit().follow()

    assert page.has_text(name)

    invite_url = utils.get_latest_email_url(email)

    client = utils.get_client()
    page = client.get(invite_url)

    if try_fake_email:
        form = page.get_form()
        form["email"] = "fakey.fakington@example.com"
        page = form.submit()
        assert page.has_text("Something has gone wrong.  Please contact your team leader.")

    form = page.get_form()
    form["email"] = email
    page = form.submit().follow()

    form = page.get_form()
    form["password1"] = password
    form["password2"] = password
    page = form.submit().follow()

    assert page.has_text("Please setup Two Factor Authentication (2FA)")

    if not skip_otp:
        form = page.get_form()
        secret = form["totp_secret"]
        form["otp"] = utils.get_otp(secret)
        page = form.submit().follow()

        if role == "TEAM_MEMBER":
            assert not page.has_text("Manage members")
        if role == "TEAM_LEADER":
            assert page.has_text("Manage members")
    return page


def test_team_leader():
    client = utils.get_client()
    email = f"larry-the-leader+{utils.make_code()}@example.com"
    new_password = "N3wP455w0rd"
    team_lead_name = f"Larry the Leader {utils.make_code()}"
    role = "TEAM_LEADER"
    page = utils.login_as_team_leader(client)
    page = page.click(contains="Add a new team member or leader")

    page = invite_user(team_lead_name, email, new_password, role)

    assert page.has_one("""h1:contains('Manage team members')""")

    page = page.click(f"""th:contains('{team_lead_name}') ~ td:nth-of-type(4) a""")

    assert page.status_code == 200

    page = page.click("""dt:contains('Role') ~ dd:nth-of-type(2) a:contains('Edit')""")

    form = page.get_form()
    form["user-name"] = f"{team_lead_name} v2"
    page = form.submit().follow()
    page = page.click(contains="Disable")

    form = page.get_form()
    page = form.submit().follow().follow()
    assert page.has_one("h1:contains('Unauthorised')")


def test_team_member():
    client = utils.get_client()
    email = f"milly-the-member+{utils.make_code()}@example.com"
    new_password = "N3wP455w0rd"
    team_lead_name = f"Milly the member {utils.make_code()}"
    role = "TEAM_MEMBER"
    page = utils.login_as_team_leader(client)
    page = page.click(contains="Add a new team member or leader")

    page = invite_user(team_lead_name, email, new_password, role)
    assert page.status_code == 200
    assert not page.has_one("""h1:contains('Manage team members')""")


def test_no_supplier_set():
    email = f"nancy-no-supplier+{utils.make_code()}@example.com"
    password = "Fl1bbl3Fl1bbl3"
    user = models.User.objects.create_user(email, password)
    user.invite_accepted_at = timezone.now()
    user.role = "TEAM_LEADER"
    user.supplier_id = None
    user.save()

    client = utils.get_client()
    utils.login(client, email, password)
    page = client.get("/portal/")
    page = page.follow()
    assert page.status_code == 403


def test_password_reset():
    utils.wipe_emails()
    email = f"team-leader-password-reset+{utils.make_code()}@example.com"
    new_password = "Bl4mbl3Bl4mbl3"
    client = utils.get_client()
    ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(seconds=600)
    with freezegun.freeze_time(ten_minutes_ago):
        page = utils.login_as_team_leader(client, email=email)
    page = client.get("/portal/accounts/login/")
    page = page.click(contains="Request password reset")
    form = page.get_form()
    form["email"] = email
    page = form.submit().follow()

    invite_url = utils.get_latest_email_url(email)
    page = client.get(invite_url)
    form = page.get_form()
    form["password1"] = new_password
    form["password2"] = new_password
    page = form.submit().follow()

    user = authenticate(None, email=email, password=new_password)
    assert user.email == email

    assert page.has_text("Please setup Two Factor Authentication (2FA)")

    form = page.get_form()
    secret = form["totp_secret"]
    form["otp"] = utils.get_otp(secret)
    page = form.submit().follow()

    assert page.has_text("Manage members")


def test_login_without_invite():
    email = f"admin-user{utils.make_code()}@example.com"
    password = "Fl1bbl3Fl1bbl3"

    models.User.objects.create_user(email, password)
    client = utils.get_client()

    page = client.get("/portal/accounts/login/")
    form = page.get_form()
    form["login"] = email
    form["password"] = password
    page = form.submit()
    assert page.has_text("Something has gone wrong.  Please contact your team leader.")


def test_logout():
    email = f"team-leader-password-reset+{utils.make_code()}@example.com"
    client = utils.get_client()
    page = utils.login_as_team_leader(client, email=email)

    assert page.has_one("""h1:contains('Manage team members')""")

    page = page.click(contains="Logout")
    assert page.has_one("""h1:contains('Are you sure you want to logout?')""")
    form = page.get_form()
    page = form.submit()
    page = page.follow()
    assert page.has_text("You have signed out.")
    assert page.has_one("""h1:contains('Log in')""")


def test_accept_fake_email():
    client = utils.get_client()
    email = f"milly-the-member+{utils.make_code()}@example.com"
    new_password = "N3wP455w0rd"
    team_lead_name = f"Milly the member {utils.make_code()}"
    role = "TEAM_MEMBER"
    page = utils.login_as_team_leader(client)
    page = page.click(contains="Add a new team member or leader")

    page = invite_user(team_lead_name, email, new_password, role, try_fake_email=True)
    assert page.status_code == 200
    assert not page.has_one("""h1:contains('Manage team members')""")


def test_invite_user_skip_otp():
    email = f"larry-the-leader+{utils.make_code()}@example.com"
    password = "Fl1bbl3Fl1bbl3"
    user = models.User.objects.create_user(email, password)
    user.full_name = f"Larry the Leader {utils.make_code()}"
    user.invite_accepted_at = timezone.now()
    user.role = "TEAM_LEADER"
    user.supplier_id = models.Supplier.objects.get(name="Utilita").id
    user.save()

    client = utils.get_client()

    page = client.get("/portal/accounts/login/")
    form = page.get_form()
    form["login"] = email
    form["password"] = password
    page = form.submit()
    page = page.follow()

    page = client.get("/portal/")
    page = page.follow()
    assert not page.has_text("Manage members")
    assert page.has_text("Unauthorised")
