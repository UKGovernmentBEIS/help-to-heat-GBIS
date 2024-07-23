from help_to_heat import portal
from help_to_heat.frontdoor.interface import SupplierConverter, api


class DuplicateReferralChecker:
    def __init__(self, session_id):
        self.session_id = session_id

    def _try_find_duplicate_referral(self):
        session_data = api.session.get_session(self.session_id)
        uprn = session_data.get("uprn")
        if not uprn:
            return None
        duplicate_referrals = portal.models.Referral.objects.filter(data__uprn=uprn).order_by("-created_at")
        if len(duplicate_referrals) == 0:
            return None
        return duplicate_referrals[0]

    def is_referral_a_duplicate(self):
        referral = self._try_find_duplicate_referral()
        return referral is not None

    def is_duplicate_referral_sent_to_same_energy_supplier(self):
        if not self.is_referral_a_duplicate():
            raise NoMatchingReferralInSessionException

        # needs to compare against the supplier that would've been saved
        saved_supplier = SupplierConverter(self.session_id).get_supplier_on_success_page()
        referral = self._try_find_duplicate_referral()
        return referral.supplier.name == saved_supplier

    def get_date_of_previous_referral(self):
        if not self.is_referral_a_duplicate():
            raise NoMatchingReferralInSessionException

        referral = self._try_find_duplicate_referral()
        return referral.created_at


class NoMatchingReferralInSessionException(Exception):
    pass
