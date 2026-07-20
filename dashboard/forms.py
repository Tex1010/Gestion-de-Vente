from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class DashboardAuthenticationForm(AuthenticationForm):
    """Restrict dashboard access to staff users."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "Cette interface est reservee aux administrateurs et gestionnaires.",
                code="not_staff",
            )
