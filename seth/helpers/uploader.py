import os
import uuid
import imghdr


class RandomNameGenerator(object):

    @classmethod
    def generate_name(cls, file_handler, filename):
        identifier = uuid.uuid4().hex
        file_name_chunks = filename.split('.')
        if len(file_name_chunks) > 1:
            identifier += u".{0}".format(file_name_chunks[-1])
        return identifier


class FileUploader(object):
    namer = RandomNameGenerator

    def __init__(self, request, key='file', as_document=True):
        self.request = request
        self.settings = self.request.registry.settings
        self.key = key
        self.as_document = as_document
        self.error = u''

    def _validate_size(self, size):
        return self.settings['uploader.min_size'] <= size <= self.settings['uploader.max_size']

    def validate(self, filehandler):
        valid_types = self.settings['uploader.valid_types']
        size = self.get_file_size(filehandler)

        if not self._validate_size(size):
            self.error = u"Incorrect file size"
            return False

        if not self.as_document:
            if not imghdr.what(filehandler) in valid_types:
                self.error = u"Incorrect file type"
                return False

        return True

    def get_file_size(self, filehandler):
        filehandler.seek(0, 2)
        size = filehandler.tell()
        filehandler.seek(0)
        return size

    def upload_file(self, inputfile, filepath):
        # Generate temporary file
        temp_filepath = "{0}~".format(filepath)
        with open(temp_filepath, 'wb') as f:
            while True:
                data = inputfile.read(2 << 16)
                if not data:
                    break
                f.write(data)
        os.rename(temp_filepath, filepath)
        inputfile.seek(0)

    def push(self):
        # Get filename and file obj from request
        # :key - key used to access file and filename from POST dictionary
        if not self.key in self.request.POST:
            return False

        try:
            filename = self.request.POST[self.key].filename
            inputfile = self.request.POST[self.key].file
        except AttributeError:
            return False
        # Generate random identifier to store file under
        identifier = self.namer.generate_name(
            file_handler=inputfile, filename=filename
        )
        new_path = os.path.join(
            self.settings['uploader.root_path'],
            identifier
        )
        if self.validate(inputfile):
            try:
                # Try to save file under path
                self.upload_file(inputfile, new_path)
            except IOError:
                return False

            return identifier

        return False

    def pop(self, identifier):
        try:
            file_path = os.path.join(
                self.settings['uploader.root_path'],
                identifier
            )
            os.remove(file_path)
        except (IOError, OSError):
            return False

        return True