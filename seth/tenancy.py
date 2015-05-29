from contextlib import contextmanager

from pyramid.settings import asbool
from pyramid.interfaces import ISettings
from pyramid.threadlocal import get_current_registry
from seth import db


supported_dialects = [
    'postgresql'
]


def get_public_schema_info():
    registry = get_current_registry()
    settings = registry.getUtility(ISettings)
    public_schema = settings.get('seth.tenant_public_schema', 'public')
    public_include = asbool(settings.get('seth.tenant_public_schema', True))
    return public_schema, public_include


class Meta:
    TenantModel = None


@contextmanager
def schema_context(schema_name=None, domain_url=None):
    if schema_name is None and domain_url is None:
        raise ValueError(u"Gimme schema_name or domain_url")

    session = db.get_session()

    if schema_name:
        tenant = Meta.TenantModel.manager.get_or_404(schema_name=schema_name)

    else:
        tenant = Meta.TenantModel.manager.get_or_404(domain_url=domain_url)

    session.execute('SET search_path TO {0}'.format(tenant.schema_name))
    yield


def get_domain_url_from_request(request):
    domain = request.domain

    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


def set_schema_to_public(session, public_schema):
    session.execute('SET search_path TO {0}'.format(public_schema))


def register_tenant_schema(request, session, tenant):
    public_schema, public_include = get_public_schema_info()

    if tenant.schema_name == public_schema:
        paths = [
            public_schema
        ]
    elif public_include:
        paths = [
            tenant.schema_name, public_schema
        ]
    else:
        paths = [
            tenant.schema_name
        ]

    session.execute("SET search_path TO {0}".format(','.join(paths)))


def set_search_path(event):
    request = event.request
    public_schema, public_include = get_public_schema_info()

    session = db.get_session()
    set_schema_to_public(session=session, public_schema=public_schema)
    domain_url = get_domain_url_from_request(request)

    tenant = Meta.TenantModel.manager.get_or_404(domain_url=domain_url)
    request.tenant = tenant
    register_tenant_schema(request=request, session=session, tenant=tenant)


