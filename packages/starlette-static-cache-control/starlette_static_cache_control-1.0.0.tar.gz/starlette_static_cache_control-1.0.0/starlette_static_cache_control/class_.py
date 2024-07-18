from starlette.staticfiles import StaticFiles as _StaticFiles


class NoCacheStaticFiles(_StaticFiles):
    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        resp.headers.setdefault("Cache-Control", "no-store")
        resp.headers.setdefault("Expires", "0")
        resp.headers.setdefault("Pragma", "no-cache")
        return resp
