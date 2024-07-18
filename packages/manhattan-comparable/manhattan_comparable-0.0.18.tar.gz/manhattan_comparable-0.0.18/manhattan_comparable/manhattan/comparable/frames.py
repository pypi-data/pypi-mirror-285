from mongoframes import *
from mongoframes.frames import _FrameMeta
from datetime import datetime, date, timezone

from manhattan.comparable.change_log import ChangeLogEntry

__all__ = ['ComparableFrame']


class _ComparableFrameMeta(_FrameMeta):
    """
    Meta class for `ComparableFrame`s to ensure that `created` and `modified`
    are present in any defined set of fields (along with `_id`).
    """

    def __new__(meta, name, bases, dct):

        # If a set of fields is defined ensure it contains `created` and
        # `modified`.
        if '_fields' in dct:
            if not 'created' in dct['_fields']:
                dct['_fields'].update({'created'})

            if not 'modified' in dct['_fields']:
                dct['_fields'].update({'modified'})

        return super(_ComparableFrameMeta, meta).__new__(meta, name, bases, dct)


class ComparableFrame(Frame, metaclass=_ComparableFrameMeta):
    """
    A Frame-like base class that provides support for tracking changes to
    documents.

    Some important rules for creating comparable frames:

    - Override the `__str__` method of the class to return a human friendly
      identity as this method is called when generating a sticky label for the
      class.
    - Define which fields are references and which `Frame` class they reference
      in the `_compared_refs` dictionary if you don't you'll only be able to see
      that the ID has changed there will be nothing human identifiable.
    """

    # The class that will be used to store changes
    _change_log_cls = ChangeLogEntry

    # A set of fields that should be exluded from comparisons/tracking
    _uncompared_fields = {'_id', 'created', 'modified'}

    # A map of reference fields and the frames they reference
    _compared_refs = {}

    @property
    def comparable(self):
        """Return a dictionary that can be compared"""
        document_dict = self.compare_safe(self._document)

        # Remove uncompared fields
        self._remove_keys(document_dict, self._uncompared_fields)

        clean_document_dict = {}
        for k, v in document_dict.items():

            # Remove any empty values
            if not v and not isinstance(v, (int, float)):
                continue

            # Convert date/time values to UTC
            if isinstance(v, datetime):
                if v.tzinfo is None:
                    v = v.replace(tzinfo=timezone.utc)

            # Convert sub frames to dictionaries
            if isinstance(v, SubFrame):
                v = v._document

            clean_document_dict[k] = v

        # Convert any referenced fields to Frames
        for ref_field, ref_cls in self._compared_refs.items():
            ref = getattr(self, ref_field)
            if not ref:
                continue

            # Check for fields which contain a list of references
            if isinstance(ref, list):
                if isinstance(ref[0], Frame):
                    continue

                # Dereference the list of reference IDs (retaining the order)
                docs = ref_cls.many(In(Q._id, ref))
                docs_map = {d._id: d for d in docs}
                docs = [docs_map[id] for id in ref if id in docs_map]
                clean_document_dict[ref_field] = docs

            else:
                if isinstance(ref, Frame):
                    continue

                # Dereference the reference ID
                clean_document_dict[ref_field] = ref_cls.by_id(ref)

        return clean_document_dict

    def logged_delete(self, user, **kwargs):
        """Delete the document and log the event in the change log"""

        # Dete the frame's document
        self.delete(**kwargs)

        # Log the change
        entry = self.__class__._change_log_cls({
            'type': 'DELETED',
            'documents': [self],
            'user': user
            })
        entry.insert(**kwargs)

        return entry

    def logged_insert(self, user, **kwargs):
        """Create and insert the document and log the event in the change log"""

        # Timestamp
        Frame.timestamp_insert(self, [self])

        # Insert the frame's document
        self.insert(**kwargs)

        # Log the insert
        entry = self.__class__._change_log_cls({
            'type': 'ADDED',
            'documents': [self],
            'user': user
            })
        entry.insert(**kwargs)

        return entry

    def logged_update(self, user, data, *fields, **kwargs):
        """
        Update the document with the dictionary of data provided and log the
        event in the change log.
        """

        # Get a copy of the frames comparable data before the update
        original = self.comparable

        # Update the frame
        _fields = fields
        if len(fields) == 0:
             _fields = data.keys()

        for field in _fields:
            if field in data:
                setattr(self, field, data[field])

        # Timestamp
        Frame.timestamp_update(self, [self])
        if fields and 'modified' not in fields:

            # Ensure the modified field is specified for any logged update
            fields = ['modified'] + list(fields)

        self.update(*fields, **kwargs)

        # Create an entry and perform a diff
        entry = self.__class__._change_log_cls({
            'type': 'UPDATED',
            'documents': [self],
            'user': user
            })
        entry.add_diff(original, self.comparable)

        # Check there's a change to apply/log
        if not entry.is_diff:
            return
        entry.insert(**kwargs)

        return entry

    @classmethod
    def compare_safe(cls, value):
        """Return a value that can be safely compared"""

        # Date
        if type(value) == date:
            return str(value)

        # Date/time values to UTC
        if type(value) == datetime:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value

        # Lists
        elif isinstance(value, (list, tuple)):
            return [cls.compare_safe(v) for v in value]

        # Dictionaries
        elif isinstance(value, dict):
            return {k: cls.compare_safe(v) for k, v in value.items()}

        # SubFrames
        if isinstance(value, SubFrame):
            return cls.compare_safe(value._document)

        return value

    @classmethod
    def logged_insert_many(cls, user, frames, **kwargs):
        """
        Insert multiple documents and log the event in the changes log for each
        document.
        """

        if not frames:
            return

        # Timestamp
        cls.timestamp_insert(cls, frames)

        # Insert the documents
        cls.insert_many(frames, **kwargs)

        # Log the inserts
        entries = []

        for frame in frames:
            entries.append(
                cls._change_log_cls({
                    'type': 'ADDED',
                    'documents': [frame],
                    'user': user
                })
            )

        cls._change_log_cls.insert_many(entries, **kwargs)

        return entries

    @classmethod
    def logged_update_many(cls, user, document_data, *fields, **kwargs):
        """
        Update multiple documents using the table of data provided and log the
        event in the changes log for each document.
        """

        assert len(fields) > 0, 'At least one field must be specified to update'

        documents = []
        entries = []
        entry_map = {}

        for document, data in document_data.items():

            # Get a copy of the frames comparable data before the update
            original = document.comparable

            # Update the frame
            for field in fields:
                if field in data:
                    setattr(document, field, data[field])

            # Timestamp
            cls.timestamp_update(document, [document])
            if fields and 'modified' not in fields:

                # Ensure the modified field is specified for any logged update
                fields = ['modified'] + list(fields)

            # Create an entry and perform a diff
            entry = cls._change_log_cls({
                'type': 'UPDATED',
                'documents': [document],
                'user': user
                })
            entry.add_diff(original, document.comparable)

            # Check there's a change to apply/log
            if entry.is_diff:
                documents.append(document)
                entries.append(entry)
                entry_map[document._id] = entry

        if entries:
            cls.update_many(documents, *fields, **kwargs)
            cls._change_log_cls.insert_many(entries, **kwargs)

        return entry_map

    @classmethod
    def logged_delete_many(cls, user, frames, **kwargs):
        """
        Delete multiple documents and log the event in the changes log for each
        document.
        """

        if not frames:
            return

        # Delete the documents
        self.delete_many(frames, **kwargs)

        # Log the deletes
        entries = []

        for frame in frames:
            entries.append(
                cls._change_log_cls({
                    'type': 'DELETED',
                    'documents': [frame],
                    'user': user
                })
            )

        cls._change_log_cls.insert_many(entries, **kwargs)

        return entries
