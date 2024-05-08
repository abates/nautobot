from django_tables2 import RequestConfig

from nautobot.circuits.models import Circuit
from nautobot.core.views import generic
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count
from nautobot.dcim.models import Device, Location, Rack, RackReservation
from nautobot.extras.models import StaticGroup
from nautobot.ipam.models import IPAddress, Prefix, VLAN, VRF
from nautobot.virtualization.models import Cluster, VirtualMachine

from . import filters, forms, tables
from .models import Tenant, TenantGroup

#
# Tenant groups
#


class TenantGroupListView(generic.ObjectListView):
    queryset = TenantGroup.objects.all()
    filterset = filters.TenantGroupFilterSet
    table = tables.TenantGroupTable


class TenantGroupView(generic.ObjectView):
    queryset = TenantGroup.objects.all()

    def get_extra_context(self, request, instance):
        # Tenants
        tenants = Tenant.objects.restrict(request.user, "view").filter(
            tenant_group__in=instance.descendants(include_self=True)
        )

        tenant_table = tables.TenantTable(tenants)
        tenant_table.columns.hide("tenant_group")

        paginate = {
            "paginator_class": EnhancedPaginator,
            "per_page": get_paginate_count(request),
        }
        RequestConfig(request, paginate).configure(tenant_table)

        return {
            "tenant_table": tenant_table,
        }


class TenantGroupEditView(generic.ObjectEditView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupForm


class TenantGroupDeleteView(generic.ObjectDeleteView):
    queryset = TenantGroup.objects.all()


class TenantGroupBulkImportView(generic.BulkImportView):  # 3.0 TODO: remove, unused
    queryset = TenantGroup.objects.all()
    table = tables.TenantGroupTable


class TenantGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = TenantGroup.objects.all()
    table = tables.TenantGroupTable
    filterset = filters.TenantGroupFilterSet


#
#  Tenants
#


class TenantListView(generic.ObjectListView):
    queryset = Tenant.objects.all()
    filterset = filters.TenantFilterSet
    filterset_form = forms.TenantFilterForm
    table = tables.TenantTable


class TenantView(generic.ObjectView):
    queryset = Tenant.objects.select_related("tenant_group")

    def get_extra_context(self, request, instance):
        stats = {
            "circuit_count": Circuit.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "cluster_count": Cluster.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "device_count": Device.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "ipaddress_count": IPAddress.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            # TODO: Should we include child locations of the filtered locations in the location_count below?
            "location_count": Location.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "prefix_count": Prefix.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "rack_count": Rack.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "rackreservation_count": RackReservation.objects.restrict(request.user, "view")
            .filter(tenant=instance)
            .count(),
            "staticgroup_count": StaticGroup.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "virtualmachine_count": VirtualMachine.objects.restrict(request.user, "view")
            .filter(tenant=instance)
            .count(),
            "vlan_count": VLAN.objects.restrict(request.user, "view").filter(tenant=instance).count(),
            "vrf_count": VRF.objects.restrict(request.user, "view").filter(tenant=instance).count(),
        }

        return {
            "stats": stats,
        }


class TenantEditView(generic.ObjectEditView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantForm
    template_name = "tenancy/tenant_edit.html"


class TenantDeleteView(generic.ObjectDeleteView):
    queryset = Tenant.objects.all()


class TenantBulkImportView(generic.BulkImportView):  # 3.0 TODO: remove, unused
    queryset = Tenant.objects.all()
    table = tables.TenantTable


class TenantBulkEditView(generic.BulkEditView):
    queryset = Tenant.objects.select_related("tenant_group")
    filterset = filters.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(generic.BulkDeleteView):
    queryset = Tenant.objects.select_related("tenant_group")
    filterset = filters.TenantFilterSet
    table = tables.TenantTable
