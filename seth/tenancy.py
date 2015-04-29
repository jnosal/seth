from pyramid.settings import asbool

from seth import db


supported_dialects = [
    'postgresql'
]


class Meta:
    TenantModel = None


def get_domain_url_from_request(request):
    domain = request.domain

    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


def set_schema_to_public(session, public_schema):
    session.execute('SET search_path TO {0}'.format(public_schema))


def register_tenant_schema(request, session, tenant):
    settings = request.registry.settings
    public_schema = settings.get('seth.tenant_public_schema', 'public')
    public_include = asbool(settings.get('seth.tenant_public_schema', True))

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
    settings = request.registry.settings
    public_schema = settings.get('seth.tenant_public_schema', 'public')

    session = db.get_session()
    set_schema_to_public(session, public_schema=public_schema)
    domain_url = get_domain_url_from_request(request)
    print domain_url
    tenant = Meta.TenantModel.manager.get_or_404(domain_url=domain_url)

    request.tenant = tenant
    register_tenant_schema(request=request, session=session, tenant=tenant)


