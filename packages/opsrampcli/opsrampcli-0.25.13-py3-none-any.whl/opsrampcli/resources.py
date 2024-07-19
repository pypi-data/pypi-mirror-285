import json
import pandas as pd
import re
import xlsxwriter
from opsrampcli.opsrampenv import OpsRampEnv
from opsrampcli import servicenow
import sys
import yaml
import logging
import importlib.util

logger = logging.getLogger(__name__)

RESOURCE_FILE_REQUIRED_FIELDS = ['client.uniqueId', 'client.name','resourceName','resourceType']
ALL_RESOURCE_FIELDS = [
    "id",
    "name",
    "type",
    "aliasName",
    "resourceName",
    "hostName",
    "make",
    "model",
    "ipAddress",
    "alternateIpAddress",
    "os",
    "serialNumber",
    "clientId",
    "partnerId",
    "entityType",
    "nativeType",
    "dnsName",
    "moId",
    "internalId",
    "state",
    "macAddress",
    "agentInstalled",
    "monitorable",
    "tags",
    "timezone",
    "osType"
  ]


def assign_via_flattened_attribute_name(orig_object:dict, flatattr_name:str, value):
    if not orig_object:
        orig_object = {}

    if flatattr_name.startswith('tags.'):
        tagname = flatattr_name.split('.')[1]
        if 'tags' not in orig_object:
            orig_object['tags'] = []
        tag = {
                "name": tagname,
                "value": value,
                "metricLabel": False,
                "scope": "CLIENT"
        }
        orig_object['tags'].append(tag)
        return orig_object

    if flatattr_name.find('.') < 0:
        orig_object[flatattr_name] = value
        return orig_object
    
    attr_elements = flatattr_name.split('.')
    attrname = attr_elements.pop(0)
    if attrname in orig_object:
        subobject = orig_object[attrname]
    else:
        subobject = None
    orig_object[attrname] =  assign_via_flattened_attribute_name(subobject, ".".join(attr_elements), value)
    return orig_object






def do_cmd_import_resources(ops: OpsRampEnv, args):
    filename = args.filename
    if not re.match(".*\.xlsx$", filename):
        filename = filename + ".xlsx"
    df =  pd.read_excel(io=filename, engine="openpyxl", dtype=str)
    return import_resources_from_dataframe(ops, args, df)


def import_resources_from_dataframe(ops: OpsRampEnv, args, df: pd.DataFrame, job: dict=None):
    customattrs = ops.get_objects(obtype="customAttributes")
    if 'code' in customattrs:
        logger.error("Error encountered retrieving custom attributes: %s" % customattrs)
        raise    

    attrinfo = {}
    for attr in customattrs:
        attrname = attr['name']
        attrinfo[attrname] = {}
        attrinfo[attrname]['id'] = attr['id']
        attrinfo[attrname]['values'] = {}

    errors = []
    for required_col in RESOURCE_FILE_REQUIRED_FIELDS:
        if required_col not in set(df.columns):
            errors.append('Required column "' + required_col + '" is missing from the spreadsheet.')
            continue
        if (len(df[df[required_col] == '']) > 0) or (len(df[pd.isna(df[required_col])]) > 0):
            errors.append('Column "' + required_col + '" has blank values which is not permitted.')
        if required_col=='name' and df['name'].duplicated().any():
            errors.append('Column "name" has duplicate values which is not permitted.')
    quertString = None
    if 'resourceType' in df:
        if len(df['resourceType'].unique()) == 1:
            rtype = df['resourceType'].unique()[0]
            queryString = f'resourceType:{rtype}'
    resources = ops.get_objects(obtype="resources", queryString=queryString, countonly=False)
    if 'code' in resources:
        logger.error("Error encountered retrieving resources: %s" % resources)
        raise    

    existing_resources_by_type_name = {}
    existing_resources_by_id = {}
    for resource in resources:
        existing_resources_by_id[resource['id']] = resource
        if resource['resourceType'] not in existing_resources_by_type_name:
            existing_resources_by_type_name[resource['resourceType']] = {}
        existing_resources_by_type_name[resource['resourceType']][resource['name'].lower()] = resource

    vals_to_add = {}
    customattr_names_in_file = []
    for columnhead in df.columns:
        df[columnhead] = df[columnhead].str.strip()
        if columnhead.startswith('tags.'):
            df[columnhead] = df[columnhead].str[0:255]
            column = columnhead.split('.')[1]
            customattr_names_in_file.append(column)
        else:
            continue
        if column not in attrinfo:
            errors.append(f'Column header tags.{column} indicates a non-existent custom attribute name of {column} for the specified client.  Please create this custom attribute name in the OpsRamp UI first.' )
        else:
            attrvalues = ops.get_tag_values(attrinfo[column]['id'])
            for value in attrvalues:
                attrinfo[column]['values'][value['value']] = value['uniqueId']
            attrvalues_values = [obj['value'] for obj in attrvalues]
            for val in df[columnhead].unique():
                if pd.notna(val) and val != "" and str(val) not in attrvalues_values:
                    if args.addvalues:
                        strval = str(val)
                        if column not in vals_to_add:
                            vals_to_add[column] = []
                        vals_to_add[column].append(strval)
                    else:
                        errors.append('Value "' + str(val) + '" specified for custom attribute "' + column + '" is not a valid value.')

    if len(errors) > 0:
        logger.error("Errors exist in the spreadsheet.  No updates to the platform have been made, please correct these errors before commiting:\n")
        for i,error in enumerate(errors):
            logger.error("%s  %s" % (str(i+1).rjust(5),error))
        #logger.error("If you want to auto-add new custom attr value definitions on the fly, use the --addvalues option otherwise undefined values will be treated as an error.\n")
        sys.exit(1)

    elif not args.commit:
        logger.info("No errors were found in the spreadsheet.  To apply the changes to the platform, rerun the command with the --commit option added.")
        sys.exit(0)


    updateresults = {
        "updatesuccess": 0,
        "updatefail": 0,
        "updatenotneeded": 0,
        "clearskipped": 0,
        "clearsuccess": 0,
        "clearfail": 0,
        "rawresults": [],
        "errors": []
    }
    

    for column in vals_to_add.keys():
        newvalsarray = []
        for val in vals_to_add[column]:
            newvalsarray.append(val)
        ismetriclabel = False
        if job and 'tag_as_metric_label' in job and column in job['tag_as_metric_label'] and job['tag_as_metric_label'][column]:
            ismetriclabel = True
        newvals = ops.add_custom_attr_value(attrinfo[column]['id'], newvalsarray, is_metric_label=ismetriclabel)
        for value in newvals:
            attrinfo[column]['values'][value['value']] = value['id']

    for idx,resource in df.iterrows():

        # See if it is a new resource or already existing
        if resource['resourceType'] in existing_resources_by_type_name and resource['resourceName'].lower() in existing_resources_by_type_name[resource['resourceType']]:
            resourceId = existing_resources_by_type_name[resource['resourceType']][resource['resourceName'].lower()]['id']
            is_new = False
        else:
            is_new = True

        # Handle delete action if specified
        if 'Processing Action' in resource and resource['Processing Action'] == 'Delete':
            if is_new:
                logger.warn(f'Delete action specified but there is no such resource name:{resource["resourceName"]} of specified type.')
            else:
                response = ops.delete_resource(resourceId)
                logger.info(f'Deleted resource name:{resource["resourceName"]} with id:{resourceId}')
            continue

        # Build the resource create/update payload
        resource_dict = {}
        for columnhead in df.columns:
            if columnhead.startswith('tags.'):
                column = columnhead.split('.')[1]
            else:
                column = columnhead
            resource_dict = assign_via_flattened_attribute_name(resource_dict, columnhead, resource[columnhead])
        if is_new:
            if args.nocreate:
                logger.info(f'Unmatched resource name:{resource_dict["resourceName"]} not created because --nocreate option is set.')
                continue
            else:
                response = ops.create_resource(resource_dict)
                if 'resourceUUID' in response:
                    resourceId = response['resourceUUID']
                    logger.info(f'Created resource name:{resource_dict["resourceName"]} with id:{resourceId}')
                else:
                    logger.error(f'Unable to create resource {resource_dict["resourceName"]}.  Please check the data for this item.')
                    continue
        else:
            response = ops.update_resource(resourceId, resource_dict)
            if 'success' in response and response['success']:
                logger.info(f'Updated resource name:{resource_dict["resourceName"]} with id:{resourceId}')
            else:
                logger.error(f'Unable to update resource {resource_dict["resourceName"]} - {response["message"]}.  Please check the data for this item.')
                continue                


        for attrname in customattr_names_in_file:
            columnhead = f'tags.{attrname}'
            column = attrname
            if pd.isnull(resource[columnhead]) or pd.isna(resource[columnhead]) or resource[columnhead]=='' :
                if args.writeblanks:
                    if is_new:
                        continue
                    if "tags" in existing_resources_by_id[resourceId] and any(attr['name']==column for attr in existing_resources_by_id[resourceId]['tags']):
                        # There are one or more values and we need to remove it/them
                        remove_values = [obj['value'] for obj in existing_resources_by_id[resourceId]['tags'] if obj['name'] == column]
                        for remove_value in remove_values:
                            ops.unset_custom_attr_on_devices(attrinfo[attrname]['id'], resourceId)
                        updateresults['clearsuccess'] +=1
                    else:
                        # There is already no value so nothing to remove
                        updateresults['clearskipped'] +=1
                else:
                    updateresults['clearskipped'] +=1
                    continue
            elif not is_new and "tags" in existing_resources_by_id[resourceId] and any(attr['name']==column and attr['value']==resource[columnhead] for attr in existing_resources_by_id[resourceId]['tags']):
                # It already has the same value for this attr, no need to update
                updateresults['rawresults'].append({
                    "rownum": idx+1,
                    "resourceid": resourceId,
                    "attr_name": column,
                    "attr_value": resource[columnhead],
                    "attr_id": attrinfo[attrname]['id'],
                    "attr_value_id": attrinfo[attrname]['values'][resource[columnhead]],
                    "action": "update not needed"
                })
                updateresults['updatenotneeded'] +=1
                continue
            else:
                # It has no value or a different value for this attr so we need to update

                # If it has a different value we need to remove it first
                if not is_new and "tags" in existing_resources_by_id[resourceId] and any(attr['name']==column for attr in existing_resources_by_id[resourceId]['tags']):
                    ops.unset_custom_attr_on_devices(attrinfo[attrname]['id'], resourceId)

                result = ops.set_custom_attr_on_devices(attrinfo[attrname]['id'], attrinfo[attrname]['values'][str(resource[columnhead])], resourceId)
                updateresults['rawresults'].append({
                    "rownum": idx+1,
                    "resourceid": resourceId,
                    "attr_name": column,
                    "attr_value": resource[columnhead],
                    "attr_id": attrinfo[attrname]['id'],
                    "attr_value_id": attrinfo[attrname]['values'][str(resource[columnhead])],
                    "action": "updated"
                })
                if type(result) == list and len(result) == 1 and 'entityId' in result[0] and result[0]['entityId'] == resourceId:
                    updateresults['updatesuccess'] +=1
                else:
                    updateresults['updatefail'] +=1
                    updateresults['errors'].append({
                        "rownum": idx+1,
                        "resourceid": resourceId,
                        "attr_name": column,
                        "attr_value": resource[columnhead],
                        "attr_id": attrinfo[attrname]['id'],
                        "attr_value_id": attrinfo[attrname]['values'][str(resource[columnhead])],
                        "action": "updatefail",
                        "response": result
                    })             
    
    logger.info("Done") 

def do_cmd_get_resources(ops,args):
    if args.search:
        if args.count:
            aggregate="count"
            groupBy = []
            fields = None
        else:
            aggregate=None
            groupBy=None
            fields = ALL_RESOURCE_FIELDS

        result = ops.do_opsql_query("resource", fields, args.search, aggregate, groupBy)
        if args.count:
            result = result[0]["count"]
    else:
        result = ops.get_objects(obtype="resources", queryString=args.query, countonly=args.count)

    if args.delete:
        confirm_delete = 'NO'
        confirm_delete = input(f'This will result in the deletion of {len(result)} resources.  Enter YES (upper case) to confirm deletion or enter anything else to just print a list of the resources that would be deleted: ')
    
        if confirm_delete == 'YES':
            for (idx, resource) in enumerate(result):
                if "resourceType" not in resource:
                    if "type" in resource:
                        resource["resourceType"] = resource["type"]
                    else:
                        resource["resourceType"] = "NONE"
                logger.info(f'Deleting resource #{idx+1} - {resource["name"]} ({resource["resourceType"]}) with uniqueId {resource["id"]}')
                try:
                    logger.info(ops.delete_resource(resource['id']))
                except Exception as e:
                    logger.error(f'Error ocurred deleting ressource with id {resource["id"]}', exc_info=e)
        else:
            return result

    elif args.manage:
        confirm_manage = 'NO'
        confirm_manage = input(f'This will result in managing {len(result)} resources.  Enter YES (upper case) to confirm or enter anything else to just print a list of the resources that would be managed: ')
    
        if confirm_manage == 'YES':
            for (idx, resource) in enumerate(result):
                logger.info(f'Managing resource #{idx+1} - {resource["name"]}')
                try:
                    logger.info(ops.do_resource_action("manage", resource['id']))
                except Exception as e:
                    logger.error(f'Exception occurred attempting to manage resource {resource["name"]} with id {resource["id"]}', exc_info=e)

        else:
            return result      


    else:
         return result

def do_cmd_importfromdatasource(ops, args):

    with open(args.job, 'r') as jobfile:
        job = yaml.safe_load(jobfile)
        #sourcemodulename = list(job['source'])[0]

        """
        spec = importlib.util.spec_from_file_location(sourcemodulename, 'opsrampcli/'+sourcemodulename+'.py')
        sourcemodule = importlib.util.module_from_spec(spec)
        sys.modules[sourcemodulename] = sourcemodule
        spec.loader.exec_module(sourcemodule)
        """
        df = servicenow.get_resources_df(job)
        return import_resources_from_dataframe(ops, args, df, job)