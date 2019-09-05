import logging
import re
import warnings

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import smart_text

# third party
from analytics.models import Visitor, WebEvent
from analytics.settings import (
    TRACK_AJAX_REQUESTS, TRACK_ANONYMOUS_USERS, TRACK_IGNORE_STATUS_CODES,
    TRACK_IGNORE_URLS, TRACK_IGNORE_USER_AGENTS, TRACK_PAGEVIEWS,
)
from analytics.utils import total_seconds
from geoip2.errors import GeoIP2Error
from ipware.ip import get_real_ip


track_ignore_urls = [re.compile(x) for x in TRACK_IGNORE_URLS]
track_ignore_user_agents = [
    re.compile(x, re.IGNORECASE) for x in TRACK_IGNORE_USER_AGENTS
]

logger = logging.getLogger('analytics')


class UnSupportedMethodException(Exception):
    pass


def remap_keys(mapping):
    return [{'key': k, 'value': mapping[k]} for k in mapping]


class VisitorTrackingMiddleware(MiddlewareMixin):
    def _should_track(self, user, request, response):
        # Session framework not installed, nothing to see here..
        if not hasattr(request, 'session'):
            msg = ('VisitorTrackingMiddleware installed without'
                   'SessionMiddleware')
            warnings.warn(msg, RuntimeWarning)
            return False

        # Do not track AJAX requests
        if request.is_ajax() and not TRACK_AJAX_REQUESTS:
            return False

        # Do not track if HTTP HttpResponse status_code blacklisted
        if response.status_code in TRACK_IGNORE_STATUS_CODES:
            return False

        # Do not track anonymous users unless specified otherwise
        if user is None and not TRACK_ANONYMOUS_USERS:
            return False

        # Do not track certain HTTP METHODS
        if request.method.upper() in ('OPTIONS', 'HEAD', ):
            return False

        # Do not track ignored urls
        path = request.path_info.lstrip('/')
        for url in track_ignore_urls:
            if url.match(path):
                return False

        # Do not track ignored user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        for user_agent_pattern in track_ignore_user_agents:
            if user_agent_pattern.match(user_agent):
                return False

        # everything says we should track this hit
        return True

    def _refresh_visitor(self, user, request, visit_time):
        # A Visitor row is unique by session_key
        session_key = request.session.session_key

        try:
            visitor = Visitor.objects.get(session_key=session_key)
        except Visitor.DoesNotExist:
            # Log the ip address. Start time is managed via the field
            # `default` value
            visitor = Visitor(session_key=session_key, created=visit_time)
            visitor.landing_url = request.build_absolute_uri()[:Visitor._meta.get_field('landing_url').max_length]

        # Update the user field if the visitor user is not set. This
        # implies authentication has occured on this request and now
        # the user is object exists. Check using `user_id` to prevent
        # a database hit.

        if user and visitor.user_id != user.id:
            visitor.user_id = user.id

        # update some session expiration details
        visitor.expiry_age = request.session.get_expiry_age()
        visitor.expiry_time = request.session.get_expiry_date()

        # grab the latest User-Agent and store it
        user_agent = request.META.get('HTTP_USER_AGENT', None)
        if user_agent:
            visitor.user_agent = smart_text(
                user_agent, encoding='latin-1', errors='ignore')

        time_on_site = 0
        if visitor.created:
            time_on_site = total_seconds(visit_time - visitor.created)
        visitor.time_on_site = int(time_on_site)
        visitor.data = remap_keys(dict(request.session.items()))
        visitor.modified = visit_time

        try:
            with transaction.atomic():
                visitor.save()
        except IntegrityError:
            # there is a small chance a second response has saved this
            # Visitor already and a second save() at the same time (having
            # failed to UPDATE anything) will attempt to INSERT the same
            # session key (pk) again causing an IntegrityError
            # If this happens we'll just grab the "winner" and use that!
            visitor = Visitor.objects.get(session_key=session_key)

        return visitor

    def _add_webevent(self, visitor, request, view_time, response_data, status_code):
        if request.method.upper() == 'GET':
            method = WebEvent.METHOD_TYPES.GET
        elif request.method.upper() == 'POST':
            method = WebEvent.METHOD_TYPES.POST
        else:
            raise UnSupportedMethodException('Method not supported', request.method)

        if hasattr(request, 'user_agent'):
            device_type = {
                request.user_agent.is_mobile: WebEvent.DEVICE_TYPES.MOBILE,
                request.user_agent.is_tablet: WebEvent.DEVICE_TYPES.TABLET,
                request.user_agent.is_pc: WebEvent.DEVICE_TYPES.PC,
                request.user_agent.is_bot: WebEvent.DEVICE_TYPES.BOT,
            }.get(True, WebEvent.DEVICE_TYPES.UNKNOWN)
            browser = request.user_agent.browser.family
            browser_version = request.user_agent.browser.version_string
            os = request.user_agent.os.family
            os_version = request.user_agent.os.version_string
            device_model = request.user_agent.device.family
        else:
            device_type = WebEvent.DEVICE_TYPES.UNKNOWN
            browser = ''
            browser_version = ''
            os = ''
            os_version = ''
            device_model = ''

        city = {}

        # Get the IP address and so the geographical info, if available.
        ip_address = get_real_ip(request) or ''
        if not ip_address:
            logger.debug(
                'Could not determine IP address for request %s', request)
        else:
            try:
                geo = GeoIP2()
            except (GeoIP2Error, GeoIP2Exception):
                logger.exception(
                    'Unable to determine geolocation for address %s', ip_address)
            else:
                city = geo.city(ip_address)

        data = dict(getattr(request, request.method.upper(), {}))
        data.pop('csrfmiddlewaretoken', None)  # Dirty hack

        if request.resolver_match:
            url_name = request.resolver_match.view_name
            url_kwargs = request.resolver_match.kwargs
        else:
            url_name = ''
            url_kwargs = ''

        WebEvent.objects.create(
            visitor=visitor,
            data=data,
            # Sometimes the url can be huge, an easy way to break the site.
            url=request.build_absolute_uri()[:WebEvent._meta.get_field('url').max_length],
            url_name=url_name,
            url_kwargs=url_kwargs,
            method=method,
            response_data=response_data,
            status_code=status_code,
            referrer=request.META.get('HTTP_REFERER', '')[:WebEvent._meta.get_field('referrer').max_length],
            browser=browser,
            browser_version=browser_version,
            os=os,
            os_version=os_version,
            device_model=device_model,
            device_type=device_type,
            ip_address=ip_address,
            ip_country=city.get('country_code', '') or '',
            ip_region=city.get('region', '') or '',
            ip_city=city.get('city', '') or '',
        )

    def process_response(self, request, response):
        # If dealing with a non-authenticated user, we still should track the
        # session since if authentication happens, the `session_key` carries
        # over, thus having a more accurate start time of session
        user = getattr(request, 'user', None)
        if user and user.is_anonymous:
            # set AnonymousUsers to None for simplicity
            user = None

        # make sure this is a response we want to track
        if not self._should_track(user, request, response):
            return response

        # Force a save to generate a session key if one does not exist
        if not request.session.session_key:
            request.session.save()

        # Be conservative with the determining time on site since simply
        # increasing the session timeout could greatly skew results. This
        # is the only time we can guarantee.
        now = timezone.now()

        # update/create the visitor object for this request
        visitor = self._refresh_visitor(user, request, now)

        if TRACK_PAGEVIEWS:
            self._add_webevent(visitor, request, now, response_data=dict(response.items()), status_code=response.status_code)

        return response
