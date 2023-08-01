import hashlib

def get_uuid(*args):
    """ Generate a UUID based on the given parameters. """

    def check_value(v):
        if not isinstance(v, str):
            raise ValueError("%s value is not a string instance" % str(v))
        elif not v:
            raise ValueError("value cannot be None or empty")
        else:
            return v
    
    def uuid(*args):
        """Generate a UUID based on the given parameters.

        The UUID will be the SHA1 of the concatenation of the values
        from the list. The separator between these values is ':'.
        Each value must be a non-empty string, otherwise, the function
        will raise an exception.

        :param *args: list of arguments used to generate the UUID

        :returns: a universal unique identifier

        :raises ValueError: when anyone of the values is not a string,
            is empty or `None`.
        """
        s = ':'.join(map(check_value, args))

        sha1 = hashlib.sha1(s.encode('utf-8', errors='surrogateescape'))
        uuid_sha1 = sha1.hexdigest()

        return uuid_sha1
    
    args_list = []
    for arg in args:
        if arg is None or arg == '':
            continue
        args_list.append(arg)
    return uuid(*args_list)

