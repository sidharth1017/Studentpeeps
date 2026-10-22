import hashlib
from dataclasses import dataclass
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

import requests
from django.conf import settings


class LogoDevError(Exception):
    pass


class LogoDevNotReady(LogoDevError):
    pass


@dataclass
class LogoDevImage:
    content: bytes
    content_type: str
    etag: str
    file_ext: str


class LogoDevClient:
    """
    Logo.dev has two surfaces:
    - API (sk_): JSON + temporary download URLs — can return 202 while indexing.
    - CDN (pk_): img.logo.dev — what the dashboard playground uses for name search.
    """

    API_BASE_URL = "https://api.logo.dev/v2"
    CDN_BASE_URL = "https://img.logo.dev"
    TIMEOUT = 30

    def __init__(
        self,
        secret_key: str | None = None,
        publishable_key: str | None = None,
    ):
        self.secret_key = secret_key or getattr(settings, "LOGO_DEV_SECRET_KEY", "") or ""
        self.publishable_key = (
            publishable_key or getattr(settings, "LOGO_DEV_PUBLISHABLE_KEY", "") or ""
        )
        if not self.secret_key and not self.publishable_key:
            raise LogoDevError(
                "LOGO_DEV_SECRET_KEY or LOGO_DEV_PUBLISHABLE_KEY must be configured"
            )

    def fetch_logo(
        self,
        *,
        domain: str | None = None,
        name: str | None = None,
        image_format: str = "webp",
        size: int = 256,
    ) -> LogoDevImage:
        if domain:
            return self._fetch_by_domain(domain.strip(), image_format, size)
        if name:
            return self._fetch_by_name(name.strip(), image_format, size)
        raise LogoDevError("domain or name is required")

    def _fetch_by_domain(self, domain: str, image_format: str, size: int) -> LogoDevImage:
        if self.secret_key:
            try:
                return self._fetch_via_api(domain=domain, image_format=image_format, size=size)
            except LogoDevNotReady:
                pass
            except LogoDevError:
                pass
        return self._fetch_via_cdn_path(domain, image_format, size, path_prefix="")

    def _fetch_by_name(self, name: str, image_format: str, size: int) -> LogoDevImage:
        if self.secret_key:
            try:
                return self._fetch_via_api(name=name, image_format=image_format, size=size)
            except LogoDevNotReady:
                pass
            except LogoDevError:
                pass

            search_hit = self.search_first(name)
            if search_hit:
                domain = search_hit.get("domain")
                logo_url = search_hit.get("logo_url")
                if domain:
                    try:
                        return self._fetch_via_api(
                            domain=domain, image_format=image_format, size=size
                        )
                    except LogoDevError:
                        try:
                            return self._fetch_via_cdn_path(
                                domain, image_format, size, path_prefix=""
                            )
                        except LogoDevError:
                            pass
                if logo_url and self.publishable_key:
                    try:
                        return self._download_url(
                            self._with_download_params(
                                self._ensure_cdn_token(logo_url),
                                image_format=image_format,
                                size=size,
                            )
                        )
                    except LogoDevError:
                        pass

        if not self.publishable_key:
            raise LogoDevError(
                "Logo.dev name lookup failed on API; set LOGO_DEV_PUBLISHABLE_KEY for CDN fallback"
            )
        return self._fetch_via_cdn_path(
            name, image_format, size, path_prefix="name/"
        )

    def search_first(self, query: str) -> dict | None:
        if not self.secret_key:
            return None

        response = requests.get(
            f"{self.API_BASE_URL}/search",
            params={"q": query.strip(), "method": "match", "limit": 5},
            headers={"Authorization": f"Bearer {self.secret_key}"},
            timeout=self.TIMEOUT,
        )
        if not response.ok:
            return None

        payload = response.json()
        results = payload.get("data") or []
        for item in results:
            if isinstance(item, dict) and item.get("domain"):
                return item
        return None

    def search_top_domain(self, query: str) -> str | None:
        hit = self.search_first(query)
        return hit.get("domain") if hit else None

    def _fetch_via_api(
        self,
        *,
        domain: str | None = None,
        name: str | None = None,
        image_format: str,
        size: int,
    ) -> LogoDevImage:
        if not self.secret_key:
            raise LogoDevError("LOGO_DEV_SECRET_KEY is not configured")

        if domain:
            params = {"domain": domain}
        elif name:
            params = {"name": name}
        else:
            raise LogoDevError("domain or name is required")

        response = requests.get(
            f"{self.API_BASE_URL}/brands/logo",
            params=params,
            headers={"Authorization": f"Bearer {self.secret_key}"},
            timeout=self.TIMEOUT,
        )
        if response.status_code == 202:
            raise LogoDevNotReady("Logo.dev is still indexing this brand")
        if not response.ok:
            raise LogoDevError(
                f"Logo.dev logo API failed ({response.status_code}): {response.text[:300]}"
            )

        payload = response.json()
        data = payload.get("data") or {}
        download_url = data.get("url")
        etag = data.get("etag") or ""
        if not download_url:
            raise LogoDevError("Logo.dev response missing download url")

        formatted_url = self._with_download_params(
            download_url,
            image_format=image_format,
            size=size,
        )
        image = self._download_url(formatted_url)
        if not etag:
            etag = hashlib.sha256(image.content).hexdigest()[:32]
        image.etag = etag
        return image

    def _fetch_via_cdn_path(
        self,
        identifier: str,
        image_format: str,
        size: int,
        *,
        path_prefix: str,
    ) -> LogoDevImage:
        if not self.publishable_key:
            raise LogoDevError("LOGO_DEV_PUBLISHABLE_KEY is not configured")

        segment = quote(identifier.strip(), safe="")
        path = f"{path_prefix}{segment}"
        query = urlencode(
            {
                "token": self.publishable_key,
                "format": image_format,
                "size": str(size),
            }
        )
        url = f"{self.CDN_BASE_URL}/{path}?{query}"
        image = self._download_url(url)
        image.etag = hashlib.sha256(image.content).hexdigest()[:32]
        return image

    def _download_url(self, url: str) -> LogoDevImage:
        file_response = requests.get(url, timeout=self.TIMEOUT)
        if not file_response.ok:
            raise LogoDevError(
                f"Logo.dev download failed ({file_response.status_code})"
            )

        content_type = (
            file_response.headers.get("Content-Type") or "image/webp"
        ).split(";")[0].strip()
        ext = ".webp"
        if "svg" in content_type:
            ext = ".svg"
        elif "png" in content_type:
            ext = ".png"
        elif "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        elif "gif" in content_type:
            ext = ".gif"

        return LogoDevImage(
            content=file_response.content,
            content_type=content_type,
            etag="",
            file_ext=ext,
        )

    def _ensure_cdn_token(self, logo_url: str) -> str:
        if "token=" in logo_url or not self.publishable_key:
            return logo_url
        parsed = urlparse(logo_url)
        query = dict(parse_qsl(parsed.query))
        query.setdefault("token", self.publishable_key)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(query),
                parsed.fragment,
            )
        )

    @staticmethod
    def _with_download_params(url: str, *, image_format: str, size: int) -> str:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query["format"] = image_format
        query["size"] = str(size)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(query),
                parsed.fragment,
            )
        )
