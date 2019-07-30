from django.contrib.auth.mixins import LoginRequiredMixin


class MLMAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_mlm_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
