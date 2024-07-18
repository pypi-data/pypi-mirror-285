from pinexq_client.core import NotAvailableException


class UnavailableAction:
	"""This class is used to represent an action that is not available. It is used to avoid None
	checks in the code."""

	def execute(self, *args, **kwargs):
		raise NotAvailableException(f"Error while executing action: action is not available")


class UnavailableLink:
	"""This class is used to represent a link that is not available. It is used to avoid None
	checks in the code."""

	def navigate(self):
		raise NotAvailableException(f"Error while navigating: link is not available")
