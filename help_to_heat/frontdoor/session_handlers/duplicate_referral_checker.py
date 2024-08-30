from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from help_to_heat import portal
from help_to_heat.frontdoor.consts import uprn_field
from help_to_heat.frontdoor.interface import SupplierConverter, api


class DuplicateReferralChecker:
    def __init__(self, session_id):
        self.session_id = session_id

    def _try_find_most_recent_duplicate_referral_within_range(self, recent_interval_months=6):
        session_data = api.session.get_session(self.session_id)
        uprn = session_data.get(uprn_field)
        if not uprn:
            return None
        recent_cutoff_date = datetime.utcnow() + relativedelta(months=-recent_interval_months)
        duplicate_referrals = (
            portal.models.Referral.objects.filter(data__uprn=uprn)
            .filter(created_at__gte=recent_cutoff_date.astimezone(pytz.UTC))
            .order_by("-created_at")
        )
        if len(duplicate_referrals) == 0:
            return None
        return duplicate_referrals[0]

    def is_referral_a_recent_duplicate(self):
        referral = self._try_find_most_recent_duplicate_referral_within_range()
        return referral is not None

    def is_recent_duplicate_referral_sent_to_same_energy_supplier(self):
        if not self.is_referral_a_recent_duplicate():
            raise NoMatchingReferralInSessionException

        # needs to compare against the supplier that would've been saved
        saved_supplier = SupplierConverter(self.session_id).get_supplier_on_success_page()
        referral = self._try_find_most_recent_duplicate_referral_within_range()
        return referral.supplier.name == saved_supplier

    def get_date_of_previous_referral(self):
        if not self.is_referral_a_recent_duplicate():
            raise NoMatchingReferralInSessionException

        referral = self._try_find_most_recent_duplicate_referral_within_range()
        return referral.created_at


class NoMatchingReferralInSessionException(Exception):
    pass
