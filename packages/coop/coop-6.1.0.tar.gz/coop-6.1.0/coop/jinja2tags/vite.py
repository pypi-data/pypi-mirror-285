import jinja2.ext
from django_vite.templatetags.django_vite import vite_asset, vite_hmr_client


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update(
            {
                "vite_hmr_client": vite_hmr_client,
                "vite_asset": vite_asset,
            }
        )
