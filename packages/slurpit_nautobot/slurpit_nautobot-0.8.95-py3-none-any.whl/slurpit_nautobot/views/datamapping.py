from django.views.generic import View
from ..models import SlurpitImportedDevice, SlurpitMapping, SlurpitLog, SlurpitSetting, SlurpitIPAddress, SlurpitInterface, SlurpitPrefix
from .. import forms, importer, models, tables
from ..decorators import slurpit_plugin_registered
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from ..forms import SlurpitMappingForm, SlurpitDeviceForm, SlurpitDeviceStatusForm, SlurpitIPAddressForm, SlurpitInterfaceForm, SlurpitPrefixForm
from ..management.choices import *
from django.contrib import messages
from nautobot.dcim.models import Device
from django.forms.models import model_to_dict
import requests
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import CustomField
from nautobot.extras.models.tags import Tag
from urllib.parse import urlencode
from nautobot.core.forms.utils import restrict_form_fields
from django.db import transaction
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress, Namespace, get_default_namespace, VRF, Prefix

BATCH_SIZE = 128

def get_device_dict(instance):
    device_dict = model_to_dict(instance)
    # Assuming 'device_type' is a ForeignKey, for example.
    device_dict['device_type'] = str(instance.device_type) if instance.device_type is not None else None
    device_dict['platform'] = str(instance.platform) if instance.platform is not None else None
    device_dict['primary_ip4'] = str(instance.primary_ip4) if instance.primary_ip4 is not None else None
    device_dict['primary_ip6'] = str(instance.primary_ip6) if instance.primary_ip6 is not None else None


    for custom_field in device_dict['_custom_field_data']:
        device_dict[f'cf_{custom_field}'] = device_dict['_custom_field_data'][custom_field]

    return device_dict

def post_slurpit_device(row, item_name):
    try:
        setting = SlurpitSetting.objects.get()
        uri_base = setting.server_url
        headers = {
                        'Authorization': f'Bearer {setting.api_key}',
                        'useragent': 'nautobot/requests',
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                    }

        uri_devices = f"{uri_base}/api/devices/sync"
        
        try:
            # row["ignore_plugin"] = str(1)
            r = requests.post(uri_devices, headers=headers, json=row, timeout=15, verify=False)
            r = r.json()
            r["item_name"] = item_name
            return r
        except Exception as e:
            return {"error": str(e), "device_name": item_name}

    except ObjectDoesNotExist:
        setting = None
        log_message = "Need to set the setting parameter"
        SlurpitLog.failure(category=LogCategoryChoices.DATA_MAPPING, message=log_message)

        return {"error": "Need to set the setting parameter", "device_name": item_name}
    
    return None

@method_decorator(slurpit_plugin_registered, name='dispatch')
class DataMappingView(View):
    template_name = "slurpit_nautobot/data_mapping.html"
    app_label = "dcim"
    model_name = "device"
    action_buttons = []
    
    def get(self, request):
        sync = request.GET.get('sync', None)
        tab = request.GET.get('tab', None)
        subtab = request.GET.get('subtab', None)
        form = []
        
        connection_status = ''
        appliance_type = ''
        mapping_type = ''
        try:
            setting = SlurpitSetting.objects.get()
            appliance_type = setting.appliance_type
            connection_status = setting.connection_status
        except ObjectDoesNotExist:
            setting = None
        
        if tab == "nautobot_to_slurpit" or tab is None:
            mapping_type = "device"

            subtab = request.GET.get('subtab', None)
            if subtab == "ipam":
                mapping_type = "ipam"
            
            mappings = SlurpitMapping.objects.filter(mapping_type=mapping_type)
            for mapping in mappings:
                form.append({
                    "choice": mapping,
                    "form": SlurpitMappingForm(choice_name=mapping, mapping_type=mapping_type, initial={"target_field": mapping.target_field})
                })
        elif tab == 'slurpit_to_nautobot':

            if subtab == None or subtab == 'ipam':
                obj = SlurpitIPAddress.objects.filter(host=None)
                if obj:
                    obj = obj.first()
                    form = SlurpitIPAddressForm(instance=obj)
                else:
                    status = Status.objects.get(name='Active')
                    namespace = get_default_namespace()
                    form = SlurpitIPAddressForm(data={'enable_reconcile':True, 'status': status, 'type': 'host', 'namespace': namespace})
            elif subtab == 'interface':
                obj = SlurpitInterface.objects.filter(name='')
                if obj:
                    obj = obj.first()
                    form = SlurpitInterfaceForm(instance=obj)
                else:
                    status = Status.objects.get(name='Active')
                    form = SlurpitInterfaceForm(data={'type': 'other', 'enable_reconcile':True, 'status': status})
            elif subtab == 'prefix':
                obj = SlurpitPrefix.objects.filter(network=None)

                if obj:
                    obj = obj.first()
                    form = SlurpitPrefixForm(instance=obj)
                else:
                    status = Status.objects.get(name='Active')
                    namespace = get_default_namespace()
                    form = SlurpitPrefixForm(data={'enable_reconcile':True, 'status': status, 'type': 'network', 'namespace': namespace})

        new_form = SlurpitMappingForm(doaction="add", mapping_type=mapping_type)
        device_form = SlurpitDeviceForm()
        # iprange_form = SlurpitIPRangeForm()
        iprange_form = SlurpitDeviceForm()
        device_status_form = SlurpitDeviceStatusForm()
        # iprange_status_form = SlurpitIPRangeStatusForm()
        iprange_status_form = SlurpitDeviceForm()

        return render(
            request,
            self.template_name, 
            {
                "form": form,
                "new_form": new_form,
                "device_form": device_form,
                "iprange_form": iprange_form,
                "device_status_form": device_status_form,
                "iprange_status_form": iprange_status_form,
                "appliance_type": appliance_type,
                "connection_status": connection_status,
            }
        )
    
    def post(self, request):
        tab = request.GET.get('tab', None)
        mapping_type = ''

        if tab == "nautobot_to_slurpit" or tab is None:
            test = request.POST.get('test')
            item_id = request.POST.get('item_id')
            subtab = request.POST.get("subtab")

            if item_id is not None:
                if item_id == "":
                    return JsonResponse({})

                # if subtab == "device":
                device = Device.objects.get(id=item_id)
                mapping_values = get_device_dict(device)
                # else:
                #     # iprange = IPRange.objects.get(id=int(item_id))
                #     device = Device.objects.get(id=item_id)
                #     mapping_values = model_to_dict(device)
                
                row = {}
                objs = SlurpitMapping.objects.all()
                if objs:
                    for obj in objs:
                        target_field = obj.target_field.split('|')[1]
                        row[obj.source_field] = str(mapping_values[target_field]) if mapping_values[target_field] is not None else None

                        if obj.source_field == 'ipv4' or obj.source_field == 'fqdn':
                            row[obj.source_field] = row[obj.source_field].split('/')[0]
                if test is not None:
                    # if subtab == "device":
                    res = post_slurpit_device(row, device.name)
                    # else:
                    #     res = None

                    if res is None:
                        return JsonResponse({"error": "Server Internal Error."})
                    
                    return JsonResponse(res)

                return JsonResponse(row)
            
            action = request.POST.get("action")
            if action is None:
                source_field = request.POST.get("source_field")
                target_field = request.POST.get("target_field")

                try:
                    obj= SlurpitMapping.objects.create(source_field=source_field, target_field=target_field, mapping_type=subtab)
                    log_message =f'Added a mapping  which {source_field} field converts to {target_field} field.'      
                    SlurpitLog.objects.create(level=LogLevelChoices.LOG_SUCCESS, category=LogCategoryChoices.DATA_MAPPING, message=log_message)
                    messages.success(request, log_message)
                except Exception as e:
                    log_message =f'Failted to add a mapping which {source_field} field converts to {target_field} field.'      
                    SlurpitLog.objects.create(level=LogLevelChoices.LOG_FAILURE, category=LogCategoryChoices.DATA_MAPPING, message=log_message)
                    messages.error(request, log_message)
                    pass
                
                return redirect(f'{request.path}?tab={tab}')
            
            elif action == "delete":
                source_field_keys = request.POST.getlist('pk')
                SlurpitMapping.objects.filter(source_field__in=source_field_keys, mapping_type=subtab).delete()
                return redirect(f'{request.path}?tab={tab}')
            
            elif action == "save":
                source_fields = request.POST.getlist('source_field')
                target_fields = request.POST.getlist('target_field')
                count = len(source_fields)
                offset = 0
                qs = []
                for i in range(count):
                    mapping, created = SlurpitMapping.objects.get_or_create(
                        source_field=source_fields[i], 
                        mapping_type=subtab,
                        defaults={'target_field': target_fields[i]}
                    )
                    if not created:
                        # If the object was retrieved and not created, you will update its `target_field`
                        mapping.target_field = target_fields[i]
                    qs.append(mapping)

                while offset < count:
                    batch_qs = qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for maping in batch_qs:
                        to_import.append(maping)

                    SlurpitMapping.objects.bulk_update(to_import, fields={'target_field'})
                    offset += BATCH_SIZE
                    
                return redirect(f'{request.path}?tab={tab}')
            elif action == "sync":
                management_status = request.POST.get('status')
                items = []

                if subtab == "device":
                    if management_status == "":
                        nautobot_devices = Device.objects.all().values("id")
                    else:
                        nautobot_devices = Device.objects.filter(status=management_status).values("id")

                    if nautobot_devices:
                        for device in nautobot_devices:
                            items.append(device['id'])
                else:
                    slurpit_tag = Tag.objects.get(name="slurpit")

                    # if management_status == "":
                    #     nautobot_ipranges = IPRange.objects.filter(tags__in=[slurpit_tag]).values("id")
                    # else:
                    #     nautobot_ipranges = IPRange.objects.filter(tags__in=[slurpit_tag], status=management_status).values("id")

                    # if nautobot_ipranges:
                    #     for iprange in nautobot_ipranges:
                    #         items.append(iprange['id'])

                return JsonResponse({"items": items})
        elif tab == "slurpit_to_nautobot":
            mapping_type = request.POST.get('mappingtype')
            if mapping_type == 'ipam':
                obj = SlurpitIPAddress.objects.filter(host=None)
                if obj is not None:
                    obj = obj.first()
                else:
                    obj = SlurpitIPAddress()

                form = SlurpitIPAddressForm(data=request.POST, instance=obj)
                restrict_form_fields(form, request.user)

                if form.is_valid():
                    try:
                        with transaction.atomic():
                            obj = form.save()
                            messages.success(request, "Updated the Slurpit IP Address Default values successfully.")
                    except ValidationError as e:
                        # logger.debug(e.message)
                        form.add_error(None, e.message)
                else:
                    messages.error(request, "Slurpit IP Address Form Validation Failed.")
                    pass
            elif mapping_type == 'interface':
                obj = SlurpitInterface.objects.filter(name='')
                if obj is not None:
                    obj = obj.first()
                else:
                    obj = SlurpitInterface()
                
                form = SlurpitInterfaceForm(data=request.POST, instance=obj)
                restrict_form_fields(form, request.user)

                if form.is_valid():
                    try:
                        with transaction.atomic():
                            obj = form.save()
                            messages.success(request, "Updated the Slurpit Interface Default values successfully.")
                    except ValidationError as e:
                        form.add_error(None, e.message)
                else:
                    messages.error(request, "Slurpit Interface Form Validation Failed.")
                    pass
            elif mapping_type == 'prefix':
                obj = SlurpitPrefix.objects.filter(network=None)
                if obj is not None:
                    obj = obj.first()
                else:
                    obj = SlurpitPrefix()

                form = SlurpitPrefixForm(data=request.POST, instance=obj)
                restrict_form_fields(form, request.user)

                if form.is_valid():
                    try:
                        with transaction.atomic():
                            obj = form.save()
                            messages.success(request, "Updated the Slurpit Prefix Default values successfully.")
                    except ValidationError as e:
                        form.add_error(None, e.message)
                else:
                    print(form.errors.items())
                    messages.error(request, "Slurpit Prefix Form Validation Failed.")
                    pass

        base_url = request.path

        if mapping_type == "":
            query_string = urlencode({'tab': tab})
        else:
            query_string = urlencode({'tab': tab, 'subtab': mapping_type})
        url = f'{base_url}?{query_string}'
        return redirect(url)