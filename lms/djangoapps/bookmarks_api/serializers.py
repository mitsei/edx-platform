from rest_framework import serializers
from openedx.core.djangoapps.user_api.serializers import ReadOnlyFieldsSerializerMixin

from .models import Bookmark


class BookmarkSerializer(serializers.HyperlinkedModelSerializer, ReadOnlyFieldsSerializerMixin):
    """
    Class that serializes the Bookmark model.
    """
    id = serializers.SerializerMethodField('get_id')
    path = serializers.CharField(source='_path')

    class Meta:
        model = Bookmark
        fields = ("id", "course_key", "usage_key", "display_name", "path", "created")
        read_only_fields = ("display_name", "course_key", "usage_key", "user")

    def get_id(self, bookmark):
        """ Gets the course org """
        return "%s, %s" % (bookmark.user.username, bookmark.usage_key)
