from os import environ


def print_profile_value(name, val):
    print('%s: MIN=%s MAX=%s' % (name, val['min'], val['max']))


def print_val(name, val):
    print('%s: %s' % (name, val))


def set_env_no_proxy(host):
    environ["no_proxy"] = host if environ.get('no_proxy') is None else environ.get('no_proxy') + "," + host
    environ["NO_PROXY"] = host if environ.get('NO_PROXY') is None else environ.get('NO_PROXY') + "," + host
