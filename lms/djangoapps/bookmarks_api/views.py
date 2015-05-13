"""
For more information, see:
https://openedx.atlassian.net/wiki/display/TNL/Bookmarks+API
"""
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import Http404

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey

from .models import Bookmark

from django.conf import settings
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.response import Response
from opaque_keys.edx.keys import CourseKey

from bookmarks_api import serializers
from openedx.core.lib.api.serializers import PaginationSerializer

from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.modulestore.django import modulestore


log = logging.getLogger(__name__)


class BookmarksView(ListCreateAPIView):
    """
    List all bookmarks or create.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    paginate_by = 10
    paginate_by_param = 'page_size'
    pagination_serializer_class = PaginationSerializer
    serializer_class = serializers.BookmarkSerializer

    def get_queryset(self):
        course_id = self.request.QUERY_PARAMS.get('course_id', None)

        if not course_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        course_key = CourseKey.from_string(course_id)

        results = Bookmark.objects.filter(course_key=course_key, user__id=self.request.user.id).order_by('-created')

        return results

    def post(self, request):
        """
        Create a new bookmark.

        Returns 400 request if bad payload is sent or it was empty object.
        """
        if not request.DATA:
            error_message = _("No data provided for bookmark")
            return Response(
                {
                    "developer_message": error_message,
                    "user_message": error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not getattr(request.DATA, "usage_id", None):
            error_message = _('No usage id provided for bookmark')
            return Response(
                {
                    "developer_message": error_message,
                    "user_message": error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        usage_id = self.request.DATA.get('usage_id', None)

        try:
            usage_key = UsageKey.from_string(usage_id)
            course_key = usage_key.course_key
        except InvalidKeyError:
            error_message = _(u"invalid usage id '{usage_id}'".format(usage_id=usage_id))
            return Response(
                {
                    "developer_message": error_message,
                    "user_message": error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            descriptor = modulestore().get_item(usage_key)
            descriptor_orig_usage_key, descriptor_orig_version = modulestore().get_block_original_usage(usage_key)
        except ItemNotFoundError:
            log.warn(
                "Invalid location for course id {course_id}: {usage_key}".format(
                    course_id=usage_key.course_key,
                    usage_key=usage_key
                )
            )
            raise Http404



        bookmarks_dict = {
            "usage_key": usage_key,
            "course_key": course_key,
            "user": request.user,
            "display_name": '',
            "_path": []
        }
        try:
            bookmark = Bookmark.create(bookmarks_dict)
        except ValidationError as error:
            log.debug(error, exc_info=True)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        bookmark.save()

        return Response(bookmark.as_dict(), status=status.HTTP_201_CREATED)

