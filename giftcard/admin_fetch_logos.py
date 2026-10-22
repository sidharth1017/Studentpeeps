from django.http import HttpResponseForbidden, JsonResponse
from django.views import View

from giftcard.services.brand_logo_fetch_service import BrandLogoFetchService


class AdminFetchBrandLogosView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Superuser access required.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return self._run(request)

    def post(self, request):
        return self._run(request)

    def _run(self, request):
        sku = (request.GET.get("sku") or request.POST.get("sku") or "").strip()
        force = self._bool_param(request, "force", default=False)
        skip_llm = self._bool_param(request, "skip_llm", default=True)

        try:
            service = BrandLogoFetchService()
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=503)

        if sku:
            results = [service.fetch_for_sku(sku, force=force, skip_llm=skip_llm)]
        else:
            results = service.fetch_all(force=force, skip_llm=skip_llm)

        payload = [self._serialize_result(r) for r in results]
        summary = {
            "total": len(payload),
            "success": sum(1 for r in payload if r["status"] == "success"),
            "skipped": sum(1 for r in payload if r["status"] == "skipped"),
            "failed": sum(1 for r in payload if r["status"] == "failed"),
        }
        return JsonResponse({"summary": summary, "results": payload})

    @staticmethod
    def _bool_param(request, name: str, *, default: bool) -> bool:
        raw = request.GET.get(name, request.POST.get(name))
        if raw is None:
            return default
        return str(raw).lower() in ("1", "true", "yes", "on")

    @staticmethod
    def _serialize_result(result) -> dict:
        data = {"sku": result.sku, "status": result.status}
        if result.brand_logo_url:
            data["brand_logo_url"] = result.brand_logo_url
        if result.brand_name_used:
            data["brand_name_used"] = result.brand_name_used
        if result.logo_domain_used:
            data["logo_domain_used"] = result.logo_domain_used
        if result.reason:
            data["reason"] = result.reason
        if result.error:
            data["error"] = result.error
        if result.reused_from_sku:
            data["reused_from_sku"] = result.reused_from_sku
        return data
