from django.core.management.base import BaseCommand

from help_to_heat.frontdoor.live_settings import (
    public_portal_is_open,
    set_public_portal_open,
)


class Command(BaseCommand):
    help = "Set the public portal to be open or closed"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--state", type=str, help="'open' or 'closed'")

    def handle(self, *args, **kwargs):
        # parse the passed state
        arg_open = None

        match kwargs.get("state"):
            case "open":
                arg_open = True
            case "closed":
                arg_open = False

        # query the current public portal state
        live_setting_open = public_portal_is_open()

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("This is a dangerous command!")
        print("Running this command toggles whether the public portal of the site is closed or open.")
        print("If the public portal is closed, users will not be able to submit referrals.")
        print("Instead, all requests for question pages will redirect to the GOV.UK start page.")
        print("This should ONLY be run with agreement from DESNZ allow users to start or stop submitting referrals.")
        print("If unsure, quit and consult the documentation.")

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if arg_open is None:
            print("Please pass a flag whether to open the site!")
            print("ex: python manage.py set_public_portal_open --state open/closed")
            print("Exiting without changes...")
            return

        print("Current configuration:")
        if arg_open:
            print("Request is to open the public portal of the site.")
        else:
            print("Request is to close the public portal of the site.")
        if live_setting_open:
            print("Public portal is currently open. Referrals can be submitted to Energy Suppliers.")
        else:
            print("Public portal is closed. Referrals cannot be submitted to Energy Suppliers.")

        # no difference
        if arg_open == live_setting_open:
            print("No changes to make.")
            print("Exiting without changes...")
            return

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(
            f"Please confirm whether you would like to {'open' if arg_open else 'close'} the public portal of the site."
        )

        confirmation = input("Enter 'Y' to continue, or 'N' to cancel: ")

        if confirmation != "Y":
            print("Exiting without changes...")
            return

        set_public_portal_open(arg_open)

        print(f"Public portal is now {'open' if arg_open else 'closed'}.")
        print("Exiting...")
