from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "showcase:home",
            "showcase:about",
            "showcase:services",
            "showcase:products",
            "showcase:training",
            "showcase:contact",
            "showcase:mentions_legales",
            "showcase:privacy",
        ]

    def location(self, item):
        return reverse(item)

