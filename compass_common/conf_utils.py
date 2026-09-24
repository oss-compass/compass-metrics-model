"""Reading conf.yaml, the configuration file of the entry scripts.

``run.py`` and the other entry points receive all of their inputs - index
names, analysis window, community and so on - from the ``params`` section of a
``conf.yaml`` file that the user writes by hand.  The helpers below keep that
reading in one place:

* :func:`normalize_param` maps the different "no value" spellings to ``None``,
* :func:`build_kwargs` builds the keyword arguments of a metrics model and
  reports the parameters that the file does not define,
* :func:`read_conf` loads the file and turns the usual setup mistakes (missing
  file, invalid YAML, no ``params`` section, no ``url``) into one readable
  error message.

Before this module existed every entry script did ``params[item]`` lookups in
its ``__main__`` block, so a configuration file that did not mention one of the
parameters aborted the run with a bare ``KeyError``; a ``conf.yaml`` written
from the example in the README was enough to trigger it.
"""
import logging
import os

import yaml

logger = logging.getLogger(__name__)

# Name of the reference configuration shipped with the repository; it is used
# in the error messages so that users know where to look for a complete file.
CONF_TEMPLATE = 'conf-github.yaml'

# conf.yaml is written by hand, so "no value" is spelled in several ways: the
# YAML null literal (``key:``), an empty string, or the quoted string copied
# from the README (``'None'``).  The metrics models use ``None`` to mean "not
# configured, keep the default", so all of these spellings have to be mapped to
# ``None`` before the values are forwarded as keyword arguments.
NULL_PARAM_STRINGS = ('none', 'null', '~')


class ConfError(ValueError):
    """Raised when conf.yaml is missing or does not provide a usable config."""


def normalize_param(value):
    """Map the different "no value" spellings of conf.yaml to None.

    :param value: raw value read from the ``params`` section of conf.yaml.
    :return: None for an empty value and for the strings 'None'/'null'/'~',
        the value itself otherwise.
    """
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() in NULL_PARAM_STRINGS:
            return None
    return value


def build_kwargs(params, keys, required_keys=(), conf_url='conf.yaml'):
    """Build the keyword arguments of a metrics model from conf.yaml.

    :param params: mapping read from the ``params`` section of conf.yaml.
    :param keys: every parameter the caller knows how to forward.
    :param required_keys: the subset of ``keys`` that conf.yaml has to provide
        a value for; a missing or empty entry raises ConfError.
    :param conf_url: path of the configuration file, used in the messages.
    :return: dict with one entry per key of ``keys``.
    :raises ConfError: when ``params`` is not a mapping or when a required
        parameter has no value.
    """
    if not isinstance(params, dict):
        raise ConfError("%s does not define a 'params' mapping" % conf_url)

    unset_required = [item for item in required_keys
                      if normalize_param(params.get(item)) is None]
    if unset_required:
        raise ConfError("%s has to provide a value for %s in its 'params' section; see the "
                        "'Configuration' section of README.md for the meaning of each "
                        "parameter" % (conf_url, ', '.join(unset_required)))

    kwargs = {}
    unset_optional = []
    for item in keys:
        if item in params:
            kwargs[item] = normalize_param(params[item])
        else:
            kwargs[item] = None
            unset_optional.append(item)
    if unset_optional:
        logger.warning("%s does not mention %s; the metrics models will use their own "
                       "defaults for these parameters", conf_url, ', '.join(unset_optional))
    return kwargs


def read_conf(conf_url):
    """Read conf.yaml and return the cluster url and the params mapping.

    :param conf_url: path of the configuration file, e.g. './conf.yaml'.
    :return: tuple (elastic_url, params).
    :raises ConfError: when the file is missing, is not valid YAML, has no
        'params' mapping or does not define 'url'.
    """
    if not os.path.exists(conf_url):
        raise ConfError("%s not found; copy %s to %s and fill in the cluster url and the "
                        "params (see README.md, section 'Configuration')"
                        % (conf_url, CONF_TEMPLATE, conf_url))
    try:
        with open(conf_url) as conf_file:
            conf = yaml.safe_load(conf_file)
    except yaml.YAMLError as error:
        raise ConfError("%s is not valid YAML: %s" % (conf_url, error))
    if not isinstance(conf, dict) or not isinstance(conf.get('params'), dict):
        raise ConfError("%s has to be a mapping with a 'params' section; see %s for a working "
                        "example" % (conf_url, CONF_TEMPLATE))
    elastic_url = conf.get('url')
    if not elastic_url:
        raise ConfError("%s does not define 'url'; it has to point at the Elasticsearch/"
                        "OpenSearch instance that holds the enriched indices" % conf_url)
    return elastic_url, conf['params']
