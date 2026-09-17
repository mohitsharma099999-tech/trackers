from .amazon import AmazonTracker

# All Amazon domains / short-link domains
AMAZON_DOMAINS = (
    'amazon.',
    'amzn.in',
    'amzn.to',
    'amzn.eu',
    'a.co',
)


def get_tracker(url):
    url_lower = url.lower()
    if any(domain in url_lower for domain in AMAZON_DOMAINS):
        return AmazonTracker()
    raise Exception(f"No tracker available for URL: {url}")