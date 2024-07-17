import os
import sys
import hashlib
import importlib
import tempfile


def dai_instance_connect(api, id, use_h2oai_client=False, use_own_client=False, backend_version_override=None):
    if sys.version_info < (3, 6):
        raise Exception("Driverless AI Python client only supports Python 3.6 and above")

    if use_own_client is True and use_h2oai_client is True:
        raise Exception("Use either use_h2oai_client=True or use_own_client=True, not both.")

    instance = api.get_driverless_instance_by_id(id)
    if instance['status'] != "running":
        raise Exception("Cannot connect to Driverless AI instance. Instance in in %s state." % instance['status'])

    token_provider = api.get_oidc_token_provider()
    if token_provider['enabled'] and use_h2oai_client is True:
        raise Exception("OpenID is not supported for use_h2oai_client=True")

    if use_h2oai_client is True:
        h2oai = importlib.import_module("h2oai_client")
    elif use_own_client is True:
        h2oai = importlib.import_module("driverlessai")
    else:
        whl_file = os.path.join(tempfile.gettempdir(), "steam", "driverlessai.whl")
        os.makedirs(os.path.dirname(whl_file), exist_ok=True)
        open(whl_file, 'a').close()
        h = hashlib.md5(open(whl_file, 'rb').read()).hexdigest()

        api.download('/download/driverless/client/%s' % h, whl_file)

        os.chmod(whl_file, 0o777)
        sys.path.insert(0, whl_file)
        h2oai = importlib.import_module("driverlessai")

    if token_provider['enabled']:
        return h2oai.Client('%s://%s:%s%s/proxy/driverless/%d' % (api.scheme, api.host, api.port, api.path, id),
                            verify=api.requests_verify(),
                            token_provider=lambda: api.get_oidc_token_provider()['access_token'],
                            backend_version_override=backend_version_override)

    return h2oai.Client('%s://%s:%s%s/proxy/driverless/%d' % (api.scheme, api.host, api.port, api.path, id),
                        username=instance['created_by'],
                        password=instance['password'],
                        verify=api.requests_verify(),
                        backend_version_override=backend_version_override)
