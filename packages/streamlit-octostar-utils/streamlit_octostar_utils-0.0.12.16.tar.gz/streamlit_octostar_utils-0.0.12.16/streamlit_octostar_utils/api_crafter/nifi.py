import os
from copy import copy, deepcopy
import uuid
import time
import jwt
from typing import List, Union, Optional
from dateutil import parser as dt_parser
import datetime as dt
import base64
from pydantic import BaseModel, ConfigDict
import json
import hashlib
import itertools
from enum import Enum
from typing import Dict, Any

from octostar.utils.workspace import read_file, upsert_entities, write_file
from octostar.utils.ontology import fetch_ontology_data, query_ontology
from octostar.utils.workspace.permissions import get_permissions, PermissionLevel
from octostar.client import AuthenticatedClient, check_required_env_vars

from ..core.dict import recursive_update_dict, travel_dict, jsondict_hash
from ..core.timestamp import now, string_to_unix
from ..octostar.annotations import merge_annotations, write_annotations, generate_annotation_uuid, ANNOTATION_CONCEPT_NAME, ANNOTATION_RELATIONSHIP
from .fastapi import DefaultErrorRoute
from ..ontology.inheritance import is_child_concept as is_child_concept_fn

METADATA_FIELD_NAME = 'os_item_content'
RELATIONSHIP_ENTITY_NAME = 'os_workspace_relationship'
FILE_ENTITY_NAME = 'os_file'
GENERIC_RELATIONSHIP_NAME = 'related_to'
FILE_RELATIONSHIP_NAME = 'generator_of'
TAG_RELATIONSHIP_NAME = 'has_tag'
TAG_ENTITY_NAME = 'os_tag'

class NifiProxyEntityModel(BaseModel):
    entity_id: str
    entity_type: str
    
class NifiOTMRelationshipProxyModel(BaseModel):
    os_entity_uid_from: str
    os_entity_type_from: str
    os_entity_uid_to: str
    os_entity_type_to: str
    os_relationship_name: str

class NifiEntityModel(BaseModel):
    class RequestModel(BaseModel):
        class OntologyInfoModel(BaseModel):
            parents: List[str]
            relationships: List[str]
        jwt: str
        ontology_name: str
        ontology_info: OntologyInfoModel
        sync_params: dict = {}
        nifi_attributes: dict = {}
        config: dict = {}
        is_temporary: bool = False
        exception: dict = {}
        last_processor_name: Optional[str] = None
        fallback_os_workspace: Optional[str] = None
    class RecordModel(BaseModel):
        model_config = ConfigDict(extra='allow')
        entity_id: str
        os_entity_uid: str
        entity_type: str
        os_concept: str
        os_workspace: Optional[str] = None
        entity_label: Optional[str] = None
    request: RequestModel
    record: RecordModel
    children: List[Union[NifiOTMRelationshipProxyModel, NifiProxyEntityModel, 'NifiEntityModel']] = []
    contents: Optional[bytes] = None
NifiEntityModel.model_rebuild()

class NifiOTMRelationshipProxy(object):
    def __init__(self, uid_from, type_from, uid_to, type_to, relationship_name, drop_on_output=False):
        self.record = {
            'os_entity_uid_from': uid_from,
            'os_entity_type_from': type_from,
            'os_entity_uid_to': uid_to,
            'os_entity_type_to': type_to,
            'os_relationship_name': relationship_name
        }
        self.drop_on_output = drop_on_output

class NifiEntityProxy(object):
    def __init__(self, context, uid, entity_type, output_as_child, output_as_independent, drop_on_output, proxy=None):
        self.context = context
        self.uid = uid
        self.entity_type = entity_type
        self.output_as_child = output_as_child
        self.output_as_independent = output_as_independent
        self.drop_on_output = drop_on_output
        self._proxy = proxy
    
    def __eq__(self, other):
        if isinstance(other, NifiEntity):
            return self.uid == other.record['entity_id']
        elif isinstance(other, NifiEntityProxy):
            return self.uid == other.uid
        else:
            return False
    
    def fetch_proxy(self):
        def _recursive_search_expanded_proxy(entity, uid_to_search):
            found_entity = None
            for child_entity in entity.children_entities:
                if child_entity._proxy:
                    if child_entity.uid == uid_to_search:
                        found_entity = child_entity
                    else:
                        found_entity = _recursive_search_expanded_proxy(child_entity._proxy, uid_to_search)
                if found_entity:
                    return found_entity
        if not self._proxy:
            main_entities = itertools.chain(*[b.entities for b in self.context.in_batches])
            main_entities = {e.record['entity_id']: e for e in main_entities}
            if main_entities.get(self.uid):
                self._proxy = main_entities.get(self.uid)
                return self._proxy
            for entity in main_entities.values():
                found_entity = _recursive_search_expanded_proxy(entity, self.uid)
                if found_entity:
                    self._proxy = found_entity._proxy
                    return self._proxy
            ## TODO: Try to get the entity from the database with query_ontology()
            raise AttributeError(f"Cannot find children with UUID {self.uid}! It may exist in the database?")
    
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            if not self._proxy:
               self.fetch_proxy()
            return getattr(self._proxy, name)

    def __setattr__(self, name, value):
        if name in ('context', 'uid', 'entity_type', 'output_as_child', 'output_as_independent', 'drop_on_output', '_proxy'):
            super().__setattr__(name, value)
        else:
            if not self._proxy:
                self.fetch_proxy()
            setattr(self._proxy, name, value)

class NifiFragmenter(object):
    def as_nifi_fragments(fragments, fragmenter_keylist):
        count = len(fragments)
        identifier = str(uuid.uuid4())
        for i, entity in enumerate(fragments):
            travel_dict(entity.request['nifi_attributes'], fragmenter_keylist.split("."), 'w')({
                'identifier': identifier,
                'count': count,
                'index': i 
            })
            if 'fragment' not in entity.request['config']:
                entity.request['config']['fragment'] = {}
            if 'fragments_stack' not in entity.request['config']['fragment']:
                entity.request['config']['fragment']['fragments_stack'] = []
            entity.request['config']['fragment']['fragments_stack'].insert(0, fragmenter_keylist)
            entity.request['nifi_attributes']['fragments_stack'] = entity.request['config']['fragment']['fragments_stack']
            travel_dict(entity.request['config']['fragment'], fragmenter_keylist.split("."), 'w')({
                'identifier': identifier,
                'count': count,
                'index': i 
            })

    def push_defragment_strategy(fragment, defragmenter_config):
        pointer = fragment.request['config']
        last_fragmenter_keylist = fragment.request['config']['fragment']['fragments_stack'][0]
        for k in ("fragment." + last_fragmenter_keylist).split("."):
            if not pointer.get(k):
                pointer[k] = {}
            pointer = pointer[k]
        pointer['merge_params'] = recursive_update_dict(pointer.get('merge_params') or {}, defragmenter_config, lambda _, v2: v2)

class NifiEntityBatch(object):
    def __init__(self, entities, config, config_key):
        self.config = config
        self.entities = entities
        self.config_key = config_key

class NifiContextManager(object):
    class SyncFlag(Enum):
        UPSERT_ENTITY_ALL = 0               # bool
        UPSERT_ENTITY_SPECIFIC_FIELDS = 1   # 'fields': list of record fields
        UPSERT_ENTITY_METADATA = 2          # bool
        #WRITE_ENTITY_ANNOTATIONS = 2        # 'overwrite': whether to merge and overwrite per producer
        WRITE_CONTENTS = 10                 # bool
        FETCH_RELATIONSHIPS = 20            # 'relationships': list of relationship names
    
    def __init__(self, json_data, lazy_sync=True):
        self.permissions = {}
        self.in_batches = None
        self.out_entities = None
        self.nonlazy_sync_ids = set()
        self.lazy_sync = lazy_sync
        self.client, self.ontology_name = self.get_client(json_data)
        self.ontology = fetch_ontology_data.sync(client=self.client)
        #self.producer_name = None
    
    def _config_get(entity, keylist=None):
        config = entity.request['config']
        return travel_dict(config, keylist.split("."), mode='r')
    
    def get_client(self, json_data):
        all_entities = copy(json_data)
        all_jwts = [e['request'].get('jwt') for e in all_entities]
        all_jwts = [j for j in all_jwts if j]
        assert(len(set(all_jwts)) == 1) # jwt must be unique
        all_ontology_names = [e['request'].get('ontology_name') for e in all_entities]
        all_ontology_names = [j for j in all_ontology_names if j]
        assert(len(set(all_ontology_names)) == 1) # ontology name must be unique
        curr_user_jwt = all_jwts[0]
        curr_user_ontology = all_ontology_names[0]
        ancestor = os.environ.get("OS_ANCESTOR")
        current_pod_name = os.environ.get("OS_CURRENT_POD_NAME")
        if not ancestor and current_pod_name:
            ancestor = current_pod_name[:-6]
        if not ancestor:
            ancestor = "local-dev"
        check_required_env_vars(["OS_API_ENDPOINT"])
        client = AuthenticatedClient(
            fixed_token = curr_user_jwt,
            timeout = 90,
            base_url = os.environ.get("OS_API_ENDPOINT"),
            headers = {
                "x-ontology": curr_user_ontology,
                "x-app-name": os.environ.get("OS_APP_NAME", "unknown-local-app"),
                "x-ancestor": ancestor,
            },
            follow_redirects = True,
            verify_ssl = True,
            raise_on_unexpected_status = False,
        )
        return client, curr_user_ontology
    
    def receive_input(self, json_data, processor_name, producer_name=None) -> List["NifiEntity"]:
        def _safe_decode(contents):
            return base64.b64decode(contents) if contents else None
        entities = []
        all_independent_uids = [e['record']['entity_id'] for e in json_data]
        for elem in json_data:
            entities.append(NifiEntity(self,
                elem['request'],
                elem['record'],
                all_independent_uids,
                elem['children'],
                _safe_decode(elem.get('contents'))))
        entities = sorted(entities, key=lambda x: string_to_unix(x.record.get('os_last_updated_at')))
        entities = list({e.record['entity_id']: e for e in entities}.values())
        entities = [(jsondict_hash(NifiContextManager._config_get(entity, processor_name)), entity) for entity in entities]
        entities = sorted(entities, key=lambda x: x[0])
        grouped_entities = []
        for _, group in itertools.groupby(entities, key=lambda x: x[0]):
            group = [e[1] for e in group]
            grouped_entities.append(NifiEntityBatch(group, NifiContextManager._config_get(group[0], processor_name), processor_name))
        self.in_batches = grouped_entities
        #self.producer_name = producer_name
        return self.in_batches

    def __enter__(self):
        return self
    
    def get_workspaces_permissions(self, workspace_ids):
        permissions_to_fetch = list(set(workspace_ids).difference(set(list(self.permissions.keys()))))
        if permissions_to_fetch:
            permissions = get_permissions.sync(permissions_to_fetch, client=self.client)
            self.permissions.update(permissions)
        permissions = {}
        for k in workspace_ids:
            permissions[k] = self.permissions.get(k, PermissionLevel.NONE)
        return permissions
        
    def request_entity_sync(self, entity, parametrized_flags: Dict[SyncFlag, Any], merge_method=lambda _, v2: v2, now=False):
        entity.sync_params = recursive_update_dict(entity.request.get('sync_params') or {}, parametrized_flags, merge_method)
        if now:
            self.nonlazy_sync_ids.add(entity.request['entity_id'])
    
    def send_output(self, entity_batches, processor_name, producer_name=None):
        def _process_entity(entity, processor_name):
            entities = []
            entity.request['last_processor_name'] = processor_name
            entities.append(entity)
            for child_entity in entity.children_entities:
                if not child_entity.drop_on_output:
                    if child_entity.output_as_independent or child_entity.output_as_child:
                        child_entity.request['last_processor_name'] = processor_name
                    if child_entity.output_as_independent:
                        if not child_entity._proxy:
                            child_entity.fetch_proxy()
                        entities.extend(_process_entity(child_entity._proxy, processor_name))
            return entities
        entities = itertools.chain(*[b.entities for b in entity_batches])
        all_entities = []
        for entity in entities:
            all_entities.extend(_process_entity(entity, processor_name))
        all_entities = sorted(all_entities, key=lambda x: dt_parser.parse(x.record.get('os_last_updated_at') or dt.datetime.fromtimestamp(0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
        self.out_entities = list({e.record['entity_id']: e for e in all_entities}.values())
        self.sync_entities()
        return self.out_entities
    
    def raise_exception(self, entity, exc):
        error_response = DefaultErrorRoute.format_error(exc)
        entity.config['exception']['code'] = error_response.status_code
        entity.config['exception']['body'] = error_response.body['message']
        travel_dict(entity.config['nifi_attributes'], ['invokehttp', 'response', 'body'], 'w')(error_response.body['message'])
        travel_dict(entity.config['nifi_attributes'], ['invokehttp', 'response', 'code'], 'w')(error_response.status_code)
        entity.config['nifi_attributes']['raised_exc'] = True
    
    def sync_entities(self):
        if not self.lazy_sync:
            entities = self.out_entities
        else:
            entities = [e for e in self.out_entities if e.record['entity_id'] in self.nonlazy_sync_ids]    
        if not entities:
            return
        reserved_fields = ['os_entity_uid', 'entity_id', 'entity_type', 'os_concept', 'entity_label', 'os_created_at', 'os_created_by', 'os_last_updated_at', 'os_last_updated_by']
        entities_to_upsert = []
        files_to_write = []
        #annotations_to_write = {True: [], False: []}
        fetch_relationships_entities = {}
        # FIND ENTITIES TO UPSERT
        for entity in entities:
            fields = set()
            if entity.sync_params.get(NifiContextManager.SyncFlag.UPSERT_ENTITY_ALL) or entity.request['is_temporary']:
                fields = fields.union(set(list(entity.record.keys())))
            if entity.sync_params.get(NifiContextManager.SyncFlag.UPSERT_ENTITY_SPECIFIC_FIELDS):
                fields = fields.union(set(entity.sync_params.get(NifiContextManager.SyncFlag.UPSERT_ENTITY_SPECIFIC_FIELDS, {}).get('fields') or []))
            if entity.sync_params.get(NifiContextManager.SyncFlag.UPSERT_ENTITY_METADATA):
                fields.add(METADATA_FIELD_NAME)
            if fields:
                entities_to_upsert.append((
                    entity,
                    [f for f in list(fields) if f not in reserved_fields]
                ))
        # FIND FILES TO WRITE
        for entity in entities:
            if entity.is_child_concept('os_file') and entity.sync_params.get(NifiContextManager.SyncFlag.WRITE_CONTENTS):
                files_to_write.append(entity)
        '''
        # FIND ANNOTATIONS TO WRITE
        for entity in entities:
            if entity.sync_params.get(NifiContextManager.SyncFlag.WRITE_ENTITY_ANNOTATIONS):
                annotations_per_producer = entity.sync_params.get(NifiContextManager.SyncFlag.WRITE_ENTITY_ANNOTATIONS) or {}
                for producer_name, params in annotations_per_producer:
                    valid_ids = params['ids']
                    overwrite = params['overwrite']
                    producer_annotations = list(filter(lambda x: x.record['producer_name'] == producer_name and x.record['entity_id'] in valid_ids, entity.annotations))
                    producer_annotations = sorted(producer_annotations, key=lambda x: string_to_unix(x.record.get('os_last_updated_at')))
                    if producer_annotations and overwrite:
                        producer_annotations = [producer_annotations[-1]]
                    for producer_annotation in producer_annotations:
                        annotations_to_write[overwrite] = producer_annotation
        '''
        # FIND RELATIONSHIPS TO FETCH
        for entity in entities:
            if entity.sync_params.get(NifiContextManager.SyncFlag.FETCH_RELATIONSHIPS):
                rels_to_fetch = entity.sync_params.get(NifiContextManager.SyncFlag.FETCH_RELATIONSHIPS, {}).get('relationships') or []
                for rel in rels_to_fetch:
                    fetch_relationships_entities[rel] = fetch_relationships_entities.get(rel, []).append(entity)
        # UPSERT ENTITIES
        if entities_to_upsert:
            new_entities = upsert_entities.sync([entity.write_os_workspace for entity, _ in entities_to_upsert],
                [{
                    'entity_type': entity.record['os_concept'],
                    'os_entity_uid': entity.record['os_entity_uid'],
                    'fields': {k: entity.record.get(k) for k in fields}
                } for entity, fields in entities_to_upsert], client=self.client)
            new_entities = {e['os_entity_uid']: e for e in new_entities}
            for entity, _ in entities_to_upsert:
                entity.record = {**entity.record, **new_entities[entity.record['os_entity_uid']]}
                entity.record['entity_id'] = entity.record['os_entity_uid']
                entity.record['entity_type'] = entity.record['os_concept']
                entity.record['entity_label'] = entity.label
                entity.request['is_temporary'] = False
        # WRITE FILES
        for file in files_to_write:
            new_file_record = write_file.sync(file.write_os_workspace,
                                              file.filepath, file.record['os_item_content_type'],
                                              file.contents, file.record['os_entity_uid'],
                                              client=self.client)
            file.record = {**file.record, **new_file_record}
            file.record['entity_id'] = file.record['os_entity_uid']
            file.record['entity_type'] = file.record['os_concept']
            file.record['entity_label'] = file.label
            file.request['is_temporary'] = False
        '''
        # WRITE ANNOTATIONS
        if annotations_to_write:
            new_annotations = {}
            for overwrite, annotations in annotations_to_write.items():
                new_these_annotations = write_annotations(
                    [a.record['source_entity_uid'] for a in annotations],
                    [a.record['source_entity_type'] for a in annotations],
                    [a.record['os_workspace'] for a in annotations],
                    [a.record['producer_name'] for a in annotations],
                    [a.record['os_item_content'] for a in annotations],
                    overwrite,
                    [a.record['entity_id'] for a in annotations],
                    client=self.client
                )
                new_annotations = {**new_annotations, **{a['os_entity_uid']: a for a in new_these_annotations}}
        for annotation, overwrite in annotations_to_write:
            annotation.record = {**annotation.record, **new_annotations[annotation.record['entity_id']]}
            # TODO: Discard old annotations if overwrite is True
            annotation.record['entity_id'] = annotation.record['os_entity_uid']
            annotation.record['entity_type'] = annotation.record['os_concept']
            annotation.record['entity_label'] = annotation.label
            annotation.request['is_temporary'] = False
        '''
        # FETCH RELATIONSHIPS
        entities_by_id = {e.record['os_entity_uid']: e for e in entities}
        if fetch_relationships_entities:
            sql_query = []
            for rel, rel_entities in fetch_relationships_entities.items():
                ontology_rel = list(filter(lambda x: x, self.ontology['relationships']))[0]
                is_mtm = ontology_rel['is_mtm']
                rel_prefix = f"{rel}[{ontology_rel['target_concept']}]"
                rel_entities = sorted(rel_entities, key=lambda x: x.record['entity_type'])
                for entity_type, rel_entities_ss in itertools.groupby(rel_entities, key=lambda x: x.record['entity_type']):
                    ids = ["'" + e.record['os_entity_uid'] + "'" for e in rel_entities_ss]
                    sql_query.append(f"""SELECT
    `os_entity_uid` AS `os_entity_uid_from`, `{rel_prefix}.os_entity_uid` AS `os_entity_uid_to`,
    `os_concept` AS `os_entity_type_from`, `{rel_prefix}.os_concept` AS `os_entity_type_to`,
    '{rel}' AS `os_relationship_name`, """ +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_entity_uid") + " AS `os_entity_uid`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_entity_type") + " AS `entity_type`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_workspace") + " AS `os_workspace`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_last_updated_at") + " AS `os_last_updated_at`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_last_updated_by") + " AS `os_last_updated_by`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_created_at") + " AS `os_created_at`, " +\
    ("NULL" if not is_mtm else f"{rel_prefix}_os_created_by") + " AS `os_created_by` " +\
    f" FROM `dtimbr`.`{entity_type}` WHERE `os_entity_uid` IN ({ids})")
            sql_query = " UNION ALL ".join(sql_query)
            rels = query_ontology.sync(sql_query, client=self.client)
            for rel in rels:
                if rel['os_entity_uid_from'] not in entities_by_id:
                    continue
                if rel['os_entity_uid']:
                    entities_by_id[rel['os_entity_uid_from']].add_mtm_relationship(
                        
                    )
                    rel_request = {
                        'jwt': entities_by_id[rel['os_entity_uid_from']].request['jwt'],
                        'ontology_name': entities_by_id[rel['os_entity_uid_from']].request['ontology_name'],
                        'ontology_info': {
                            'parents': self.ontology['concepts'][entity_type]['parents'],
                            'relationships': self.ontology['concepts'][entity_type]['relationships']
                        },
                        'sync_params': {},
                        'nifi_attributes': {},
                        'config': deepcopy(entities_by_id[rel['os_entity_uid_from']].request['config']),
                        'fallback_os_workspace': entities_by_id[rel['os_entity_uid_from']].request['fallback_os_workspace'],
                        'is_temporary': False
                    }
                    rel = {**rel, 'entity_id': rel['os_entity_uid'], 'os_concept': rel['entity_type']}
                    entities_by_id[rel['os_entity_uid_from']].children.append(
                        NifiEntityProxy(
                            entities_by_id[rel['os_entity_uid_from']].context,
                            rel['os_entity_uid'],
                            rel['os_entity_type'],
                            True, False, False, NifiEntity(
                                self, rel_request, rel, []
                            )
                        )
                    )
                else:
                    entities_by_id[rel['os_entity_uid_from']].children.append(
                        NifiOTMRelationshipProxy(
                            rel['os_entity_uid_from'], rel['os_entity_type_from'],
                            rel['os_entity_uid_to'], rel['os_entity_type_to'],
                            rel['os_relationship_name'])
                    )
            rels = sorted(rels, key=lambda x: x['os_entity_type_to'])
            for os_entity_type_to, group in itertools.groupby(rels, key=lambda x: x['os_entity_type_to']):
                group = list(group)
                uids_str = ",".join("'" + rel['os_entity_uid_to'] + "'" for rel in group)
                linked_entities = query_ontology.sync(f"SELECT * FROM `dtimbr`.`{os_entity_type_to}` WHERE `os_entity_uid` IN ({uids_str})", client=self.client)
                for linked_entity in linked_entities:
                    linked_rels = [r for r in group if r['os_entity_uid_to']]
                    # TODO: Link new entities with their source entities
                    '''
                    new_request = {
                        'jwt': entities_by_id[rel['os_entity_uid_from']].request['jwt'],
                        'ontology_name': entities_by_id[rel['os_entity_uid_from']].request['ontology_name'],
                        'ontology_info': {
                            'parents': self.ontology['concepts'][entity_type]['parents'],
                            'relationships': self.ontology['concepts'][entity_type]['relationships']
                        },
                        'sync_params': {},
                        'nifi_attributes': {},
                        'config': deepcopy(entities_by_id[rel['os_entity_uid_from']].request['config']),
                        'fallback_os_workspace': entities_by_id[rel['os_entity_uid_from']].request['fallback_os_workspace'],
                        'is_temporary': False
                    }
                    rel = {**rel, 'entity_id': rel['os_entity_uid'], 'os_concept': rel['entity_type']}
                    entities_by_id[rel['os_entity_uid_from']].children.append(
                        NifiEntityProxy(
                            entities_by_id[rel['os_entity_uid_from']].context,
                            rel['os_entity_uid'],
                            rel['os_entity_type'],
                            True, False, False, NifiEntity(
                                self, rel_request, rel, []
                            )
                        )
                    )
                    '''
        # CLEAN SYNC PARAMS
        for entity in entities:
            entity.sync_params = {}
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            return False
        if self.out_entities is None:
            raise AssertionError("Entities must be returned to the nifi context!")
    
    def jsonify(self, entities):
        def _recursive_collect_proxies(entities):
            children = []
            for entity in entities:
                if isinstance(entity, NifiEntityProxy):
                    children.extend(entity.children_entities)
                    children.extend(_recursive_collect_proxies(entity.children_entities))
            return children
        all_proxies = _recursive_collect_proxies(entities)
        banned_entities = [e for e in all_proxies if not e.output_as_independent]
        entities = [e for e in entities if e not in banned_entities]
        return {
            'content': [e for e in [entity.to_json() for entity in entities] if e],
            'media_type': 'application/json'
        }
            
class NifiEntity(object):
    def __init__(self, context, request, record, all_independent_uids, children=[], contents=None):
        self.context = context
        self.request = request
        self.request['nifi_attributes'] = {}
        self.record = record
        assert(self.record.get('os_entity_uid') and self.record.get('entity_id'))
        assert(self.record.get('os_concept') and self.record.get('entity_type'))
        if 'entity_label' not in self.record:
            self.record['entity_label'] = self.label
        children = [c for c in children if isinstance(c, (str, dict))]
        full_entity_children = []
        proxy_otm_children = []
        proxy_entity_children = []
        for child in children:
            if 'os_relationship_name' in child:
                proxy_otm_children.append(child)
            elif 'request' in child:
                full_entity_children.append(child)
            else:
                proxy_entity_children.append(child)
        child_uids = [c['entity_id'] for c in proxy_entity_children] + [c['record']['entity_id'] for c in full_entity_children]
        child_types = [c['entity_type'] for c in proxy_entity_children] + [c['record']['entity_type'] for c in full_entity_children]
        output_as_child = [False]*len(proxy_entity_children) + [True]*len(full_entity_children)
        output_as_independent = [uid in all_independent_uids for uid in child_uids]
        child_proxies = [None]*len(proxy_entity_children) + full_entity_children
        self.children = [NifiEntityProxy(
            self.context,
            child_uids[i],
            child_types[i],
            output_as_child[i],
            output_as_independent[i],
            False,
            child_proxies[i]) for i in range(len(child_uids))]
        self.children.extend([
            NifiOTMRelationshipProxy(**otm_child) for otm_child in proxy_otm_children
        ])
        self._contents = contents
        self.drop_on_output = False
    def __eq__(self, other):
        if isinstance(other, NifiEntity):
            return self.record['entity_id'] == other.record['entity_id']
        elif isinstance(other, NifiEntityProxy):
            return self.record['entity_id'] == other.uid
        else:
            return False
    @property
    def sync_params(self):
        return {NifiContextManager.SyncFlag[k]: v for k, v in (self.request.get('sync_params') or {}).items()}
    @sync_params.setter
    def sync_params(self, new_params):
        self.request['sync_params'] = {(k.name if isinstance(k, NifiContextManager.SyncFlag) else k): v for k, v in new_params.items()}     
    @property
    def metadata(self):
        return self.record.get(METADATA_FIELD_NAME) or {}
    @metadata.setter
    def metadata(self, new_metadata):
        self.record[METADATA_FIELD_NAME] = new_metadata       
    @property
    def contents(self):
        if not self._contents:
            self._contents = read_file.sync(self.record['os_workspace'], self.record['os_entity_uid'], False,
                                            client=self.context.client)
        return self._contents
    @contents.setter
    def contents(self, new_contents):
        self._contents = new_contents
    @property
    def children_entities(self):
        return list(filter(lambda x: isinstance(x, NifiEntityProxy), self.children))
    @property
    def relationships(self):
        return list(filter(lambda x: isinstance(x, NifiOTMRelationshipProxy) or is_child_concept_fn(x.entity_type, RELATIONSHIP_ENTITY_NAME, self.context.ontology), self.children))
    '''
    @property
    def annotations(self):
        list(filter(lambda x: isinstance(x, NifiEntityProxy) and x.is_child_concept(ANNOTATION_CONCEPT_NAME), self.children)) 
    '''
    @property
    def write_os_workspace(self):
        permissions = self.context.get_workspaces_permissions([e for e in [self.record.get('os_workspace'), self.request.get('fallback_os_workspace')] if e])
        if self.record.get('os_workspace') and (permissions.get(self.record.get('os_workspace')) or PermissionLevel.NONE) >= PermissionLevel.WRITE:
            return self.record['os_workspace']
        elif self.request.get('fallback_os_workspace') and (permissions.get(self.request.get('fallback_os_workspace')) or PermissionLevel.NONE) >= PermissionLevel.WRITE:
            return self.request['fallback_os_workspace']
        else:
            return None
    @property
    def label(self):
        if not self.context.ontology:
            return None
        label_fields = self.context.ontology['concepts'][self.record.get('os_concept') or self.record.get('entity_type')]['labelKeys']
        label_fields = [field for field in label_fields if field]
        label = " ".join([(self.record.get(field) or "") for field in label_fields]).strip()
        if not label:
            label = None
        return label
    @property
    def filepath(self):
        return self.record.get('#path') or self.label
    @property
    def jwt_data(self):
        return jwt.decode(
            self.request['jwt'],
            algorithms=["ES256"],
            options={'verify_signature': False}
        )
    def update_last_timestamp(self):
        self.record['os_last_updated_at'] = now()
    def is_child_concept(self, type):
        entity_type = None
        if isinstance(self, NifiEntityProxy):
            entity_type = self.entity_type
        else:
            entity_type = self.record['entity_type']
        return is_child_concept_fn(entity_type, type, self.context.ontology)
    def is_fragmented(self):
        return bool(self.request['config'].get('fragment', {}).get('fragments_stack'))
    def to_json(self):
        def _safe_encode(contents):
            return base64.b64encode(contents) if contents else None
        if self.drop_on_output:
            return
        proxy_entity_children = []
        proxy_otm_children = []
        full_entity_children = []
        for child in self.children:
            if isinstance(child, NifiOTMRelationshipProxy):
                proxy_otm_children.append(child)
            else:
                if child.drop_on_output:
                    pass
                elif child.output_as_child:
                    child.fetch_proxy()
                    full_entity_children.append(child)
                else:
                    proxy_entity_children.append(child)
        proxy_entity_children = list({c.uid: c for c in proxy_entity_children}.values())
        proxy_entity_children = [{'entity_id': c.uid, 'entity_type': c.entity_type} for c in proxy_entity_children]
        proxy_otm_children = list({c.record['os_entity_uid_from'] + "|" + c.record['os_relationship_name'] + "|" + c.record['os_entity_uid_to']: c for c in proxy_otm_children}.values())
        proxy_otm_children = [c.record for c in proxy_otm_children]
        full_entity_children = sorted(full_entity_children, key=lambda x: string_to_unix(x.record.get('os_last_updated_at')))
        full_entity_children = list({c.uid: c for c in full_entity_children}.values())
        children = full_entity_children + proxy_entity_children + proxy_otm_children
        return {
            'request': self.request,
            'record': self.record,
            'children': children,
            'contents': _safe_encode(self._contents)
        }
    def _add_entity(self, os_workspace, entity_type, fields):
        now_time = now()
        random_id = str(uuid.uuid4())
        username = self.jwt_data['username']
        child_request = {
            'jwt': self.request['jwt'],
            'ontology_name': self.request['ontology_name'],
            'ontology_info': {
                'parents': self.context.ontology['concepts'][entity_type]['parents'],
                'relationships': self.context.ontology['concepts'][entity_type]['relationships']
            },
            'sync_params': {},
            'nifi_attributes': {},
            'config': deepcopy(self.request['config']),
            'fallback_os_workspace': self.request['fallback_os_workspace'],
            'is_temporary': True
        }
        child_entity = NifiEntity(self.context, child_request, {
            **fields,
            'os_workspace': os_workspace,
            'os_concept': entity_type,
            'entity_type': entity_type,
            'os_entity_uid': random_id,
            'entity_id': random_id,
            'os_created_at': now_time,
            'os_created_by': username,
            'os_last_updated_at': now_time,
            'os_last_updated_by': username
        }, [])
        child_entity.record['entity_label'] = child_entity.label
        child_entity_proxy = NifiEntityProxy(self.context, child_entity.record['entity_id'], child_entity.record['entity_type'], True, False, False, child_entity)
        self.children.append(child_entity_proxy)
        return child_entity_proxy
    def add_mtm_relationship(self, os_entity_uid_from, entity_type_from, os_entity_uid_to, entity_type_to,
                         os_relationship_name, os_relationship_workspace, relationship_fields):
        return self._add_entity(
            os_relationship_workspace, RELATIONSHIP_ENTITY_NAME,
            {
                **relationship_fields,
                'os_entity_uid_from': os_entity_uid_from,
                'os_entity_type_from': entity_type_from,
                'os_entity_uid_to': os_entity_uid_to,
                'os_entity_type_to': entity_type_to,
                'os_relationship_name': os_relationship_name,
            }
        )
    def add_otm_relationship(self, os_entity_uid_from, entity_type_from, os_entity_uid_to, entity_type_to,
                             os_relationship_name):
        self.children.append(NifiOTMRelationshipProxy(
            os_entity_uid_from, entity_type_from, os_entity_uid_to, entity_type_to, os_relationship_name
        ))
    def add_child_entity(self, os_workspace, entity_type, fields, os_relationship_name=GENERIC_RELATIONSHIP_NAME, os_relationship_type='mtm'):
        child_entity = self._add_entity(os_workspace, entity_type, fields)
        if os_relationship_type == 'mtm':
            child_rel = self.add_mtm_relationship(self.record['os_entity_uid'], self.record['os_concept'],
                                child_entity.record['os_entity_uid'], child_entity.record['os_concept'],
                                os_relationship_name, os_workspace, {})
        elif os_relationship_type == 'otm':
            child_rel = self.add_otm_relationship(self.record['os_entity_uid'], self.record['os_concept'],
                                child_entity.record['os_entity_uid'], child_entity.record['os_concept'],
                                os_relationship_name)
        return child_entity, child_rel
    def add_child_file(self, os_workspace, full_filename, filetype, file, os_relationship_name=FILE_RELATIONSHIP_NAME, os_relationship_type='mtm'):
        child_entity, child_rel = self.add_child_entity(os_workspace, FILE_ENTITY_NAME,
            {
                'os_item_name': full_filename.rsplit("/", 1)[-1],
                'os_item_content_type': filetype,
                '#path': full_filename,
            }, os_relationship_name, os_relationship_type
        )
        child_entity._contents = file
        return child_entity, child_rel
    def add_tag(self, os_workspace, name, group, order, color):
        return self.add_child_entity(
            os_workspace, 'os_tag',
            {
                'name': name,
                'group': group,
                'order': order,
                'color': color
            }, TAG_RELATIONSHIP_NAME, 'mtm'
        )
    '''
    def get_annotation(self, producer_names=None):
        if not producer_names:
            producer_names = [self.context.producer_name]
        if producer_names == 'all':
            annotations = self.annotations
        else:
            annotations = list(filter(lambda x: x.record['producer_name'] in producer_names, self.annotations))
        annotations = sorted(annotations, lambda x: string_to_unix(x.record.get('os_last_updated_at')))
        merged_annotation = merge_annotations(
            [a.record['os_item_content'] for a in annotations],
            {'op': lambda _, v2: v2}
        )
        return merged_annotation
    def add_annotation(self, contents, overwrite=True, os_workspace=None, sync=True):
        if not os_workspace:
            os_workspace = self.write_os_workspace
        if overwrite:
            annotations_to_remove = list(filter(lambda x: x.record['producer_name'] == self.context.producer_name, self.annotations))
            annotations_to_remove = {a.record['os_entity_uid']: a for a in annotations_to_remove}
            self.children = list(filter(lambda x: x not in annotations_to_remove.values(), self.children))
            self.children = list(filter(lambda x: not isinstance(x, NifiOTMRelationshipProxy) or x.record['os_entity_uid_to'] in annotations_to_remove.keys(),
                                        self.children))
        annotation_id = generate_annotation_uuid(self.record['entity_id'])
        child_entity, child_rel = self.add_child_entity(os_workspace, ANNOTATION_CONCEPT_NAME, {
            'os_item_content': contents,
            'producer_name': self.context.producer_name,
            'source_entity_uid': self.record['entity_id'],
            'source_entity_type': self.record['entity_type'],
            'os_has_attachment': False
        }, ANNOTATION_RELATIONSHIP[0], 'otm')
        child_entity.record['os_entity_uid'] = annotation_id
        child_entity.record['entity_id'] = annotation_id
        child_rel.record['os_entity_uid_to'] = annotation_id
        if sync:
            self.context.request_entity_sync(self, {NifiContextManager.SyncFlag.WRITE_ENTITY_ANNOTATIONS: {
                self.context.producer_name: {
                    'overwrite': overwrite
                }
            }}, merge_method=lambda v1, v2: v1 or v2)
            self.context.request_entity_sync(self, {NifiContextManager.SyncFlag.WRITE_ENTITY_ANNOTATIONS: {
                self.context.producer_name: {
                    'ids': [annotation_id]
                }
            }}, merge_method=lambda v1, v2: (v1 or []) + v2)
        return child_entity, child_rel
    def update_annotation(self, new_contents, merge_params={'op': lambda _, v2: v2}):
        old_annotation = self.get_annotation(None)
        return self.add_annotation(merge_annotations([old_annotation, new_contents], merge_params))
    '''
    def add_metadata(self, json, recurse: Union[bool, int]=False, merge_method=lambda _, v2: v2):
        self.metadata = recursive_update_dict(self.metadata, json, merge_method, recurse)
        self.context.request_entity_sync(self, {NifiContextManager.SyncFlag.UPSERT_ENTITY_METADATA: True})
    def propagate_metadata(self, to_entity, fields=None, merge_method=lambda _, v2: v2):
        metadata_to_propagate = deepcopy(self.metadata)
        if fields:
            metadata_to_propagate = {k:v for k, v in self.metadata if k in fields}
        to_entity.metadata = recursive_update_dict(to_entity.metadata, metadata_to_propagate, merge_method)
        to_entity.context.request_entity_sync(self, {NifiContextManager.SyncFlag.UPSERT_ENTITY_METADATA: True})

def more_recent_than(record_a, record_b):
    return string_to_unix(record_a.get('os_last_updated_at')) >= string_to_unix(record_b.get('os_last_updated_at'))