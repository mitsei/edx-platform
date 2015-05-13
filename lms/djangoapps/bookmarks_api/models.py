import json
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from xmodule_django.models import CourseKeyField, LocationKeyField


class Bookmark(models.Model):
    """
    Unit Bookmarks model.
    """
    user = models.ForeignKey(User)
    course_key = CourseKeyField(max_length=255, db_index=True)
    usage_key = LocationKeyField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255, default="", help_text="Display name of XBlock")
    _path = models.TextField(db_column='path', null=True, blank=True, help_text="JSON, breadcrumbs to the XBlock")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def path(self):
        """
        Jsonify the path
        """
        return json.loads(self._path)

    @path.setter
    def path(self, value):
        """
        Un-Jsonify the path
        """
        self._path = json.dumps(value)

    @classmethod
    def create(cls, bookmark_dict):
        """
        Create the bookmark object.
        """
        if not isinstance(bookmark_dict, dict):
            raise ValidationError('Bookmark must be a dictionary.')

        if len(bookmark_dict) == 0:
            raise ValidationError('Bookmark must have a body.')

        path = bookmark_dict.get('path', list())

        if len(path) < 1:
            raise ValidationError('Bookmark must contain at least one path.')

        bookmark_dict['path'] = json.dumps(path)
        bookmark_dict['user'] = bookmark_dict.pop('user', None)

        return cls(**bookmark_dict)

    def as_dict(self):
        """
        Returns the note object as a dictionary.
        """
        created = self.created.isoformat() if self.created else None
        updated = self.updated.isoformat() if self.updated else None

        return {
            'id': str(self.pk),
            'user': self.user_id,
            'course_id': self.course_id,
            'usage_id': self.usage_id,
            'display_name': self.display_name,
            'path': json.loads(self.path),
            'created': created,
            'updated': updated,
        }
