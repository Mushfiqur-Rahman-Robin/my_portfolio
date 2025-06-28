from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class CustomAnonRateThrottle(AnonRateThrottle):
    """
    Limits the rate of API requests for anonymous users based on IP address.
    Applied globally as a baseline for non-sensitive public APIs.
    """

    scope = "anon"


class CustomUserRateThrottle(UserRateThrottle):
    """
    Limits the rate of API requests for authenticated users based on the user ID.
    Applied globally as a baseline.
    """

    scope = "user"


class ContactFormRateThrottle(AnonRateThrottle):
    """
    Limits the rate of contact form submissions for anonymous users.
    Stricter than the general 'anon' throttle to prevent spam.
    """

    scope = "contact_form"


class VisitorCountRateThrottle(AnonRateThrottle):
    """
    Limits the rate of visitor count increments for anonymous users.
    Stricter than the general 'anon' throttle to prevent abuse.
    """

    scope = "visitor_count"
