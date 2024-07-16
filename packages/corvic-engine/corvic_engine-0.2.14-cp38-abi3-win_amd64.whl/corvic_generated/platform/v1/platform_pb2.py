# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: corvic/platform/v1/platform.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from buf.validate import validate_pb2 as buf_dot_validate_dot_validate__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!corvic/platform/v1/platform.proto\x12\x12\x63orvic.platform.v1\x1a\x1b\x62uf/validate/validate.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x8c\x02\n\x03Org\x12\x1b\n\x04name\x18\x01 \x01(\tB\x07\xbaH\x04r\x02\x10\x01R\x04name\x12p\n\x02id\x18\x02 \x01(\tB`\xbaH]\xba\x01Z\n\x0estring.pattern\x12\x16value must be a number\x1a\x30this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')R\x02id\x12\x39\n\ncreated_at\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\tcreatedAt\x12;\n\x0bmodified_at\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\nmodifiedAt\"\xc8\x01\n\x04User\x12p\n\x02id\x18\x01 \x01(\tB`\xbaH]\xba\x01Z\n\x0estring.pattern\x12\x16value must be a number\x1a\x30this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')R\x02id\x12\"\n\x08org_name\x18\x02 \x01(\tB\x07\xbaH\x04r\x02\x10\x01R\x07orgName\x12\x14\n\x05\x65mail\x18\x03 \x01(\tR\x05\x65mail\x12\x14\n\x05roles\x18\x04 \x03(\tR\x05roles\"/\n\x10\x43reateOrgRequest\x12\x1b\n\x04name\x18\x01 \x01(\tB\x07\xbaH\x04r\x02\x10\x01R\x04name\">\n\x11\x43reateOrgResponse\x12)\n\x03org\x18\x01 \x01(\x0b\x32\x17.corvic.platform.v1.OrgR\x03org\"#\n\rGetOrgRequest\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\";\n\x0eGetOrgResponse\x12)\n\x03org\x18\x01 \x01(\x0b\x32\x17.corvic.platform.v1.OrgR\x03org\"\x11\n\x0fListOrgsRequest\"?\n\x10ListOrgsResponse\x12+\n\x04orgs\x18\x01 \x03(\x0b\x32\x17.corvic.platform.v1.OrgR\x04orgs\"9\n\x13ListOrgUsersRequest\x12\"\n\x08org_name\x18\x01 \x01(\tB\x07\xbaH\x04r\x02\x10\x01R\x07orgName\"F\n\x14ListOrgUsersResponse\x12.\n\x05users\x18\x01 \x03(\x0b\x32\x18.corvic.platform.v1.UserR\x05users\"}\n\x11\x41\x64\x64OrgUserRequest\x12\x14\n\x05\x65mail\x18\x01 \x01(\tR\x05\x65mail\x12\"\n\x08org_name\x18\x02 \x01(\tB\x07\xbaH\x04r\x02\x10\x01R\x07orgName\x12.\n\x05roles\x18\x03 \x03(\x0e\x32\x18.corvic.platform.v1.RoleR\x05roles\"B\n\x12\x41\x64\x64OrgUserResponse\x12,\n\x04user\x18\x01 \x01(\x0b\x32\x18.corvic.platform.v1.UserR\x04user\"\x85\x01\n\x11GetOrgUserRequest\x12p\n\x02id\x18\x01 \x01(\tB`\xbaH]\xba\x01Z\n\x0estring.pattern\x12\x16value must be a number\x1a\x30this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')R\x02id\"B\n\x12GetOrgUserResponse\x12,\n\x04user\x18\x01 \x01(\x0b\x32\x18.corvic.platform.v1.UserR\x04user*C\n\x04Role\x12\x14\n\x10ROLE_UNSPECIFIED\x10\x00\x12\x12\n\x0eROLE_ORG_ADMIN\x10\x01\x12\x11\n\rROLE_ORG_USER\x10\x02\x32\xb7\x04\n\nOrgService\x12Q\n\x06GetOrg\x12!.corvic.platform.v1.GetOrgRequest\x1a\".corvic.platform.v1.GetOrgResponse\"\x00\x12Z\n\tCreateOrg\x12$.corvic.platform.v1.CreateOrgRequest\x1a%.corvic.platform.v1.CreateOrgResponse\"\x00\x12W\n\x08ListOrgs\x12#.corvic.platform.v1.ListOrgsRequest\x1a$.corvic.platform.v1.ListOrgsResponse\"\x00\x12]\n\nGetOrgUser\x12%.corvic.platform.v1.GetOrgUserRequest\x1a&.corvic.platform.v1.GetOrgUserResponse\"\x00\x12]\n\nAddOrgUser\x12%.corvic.platform.v1.AddOrgUserRequest\x1a&.corvic.platform.v1.AddOrgUserResponse\"\x00\x12\x63\n\x0cListOrgUsers\x12\'.corvic.platform.v1.ListOrgUsersRequest\x1a(.corvic.platform.v1.ListOrgUsersResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'corvic.platform.v1.platform_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ORG'].fields_by_name['name']._options = None
  _globals['_ORG'].fields_by_name['name']._serialized_options = b'\272H\004r\002\020\001'
  _globals['_ORG'].fields_by_name['id']._options = None
  _globals['_ORG'].fields_by_name['id']._serialized_options = b'\272H]\272\001Z\n\016string.pattern\022\026value must be a number\0320this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')'
  _globals['_USER'].fields_by_name['id']._options = None
  _globals['_USER'].fields_by_name['id']._serialized_options = b'\272H]\272\001Z\n\016string.pattern\022\026value must be a number\0320this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')'
  _globals['_USER'].fields_by_name['org_name']._options = None
  _globals['_USER'].fields_by_name['org_name']._serialized_options = b'\272H\004r\002\020\001'
  _globals['_CREATEORGREQUEST'].fields_by_name['name']._options = None
  _globals['_CREATEORGREQUEST'].fields_by_name['name']._serialized_options = b'\272H\004r\002\020\001'
  _globals['_LISTORGUSERSREQUEST'].fields_by_name['org_name']._options = None
  _globals['_LISTORGUSERSREQUEST'].fields_by_name['org_name']._serialized_options = b'\272H\004r\002\020\001'
  _globals['_ADDORGUSERREQUEST'].fields_by_name['org_name']._options = None
  _globals['_ADDORGUSERREQUEST'].fields_by_name['org_name']._serialized_options = b'\272H\004r\002\020\001'
  _globals['_GETORGUSERREQUEST'].fields_by_name['id']._options = None
  _globals['_GETORGUSERREQUEST'].fields_by_name['id']._serialized_options = b'\272H]\272\001Z\n\016string.pattern\022\026value must be a number\0320this.matches(\'^[0-9]+$\') && !this.endsWith(\'\\n\')'
  _globals['_ROLE']._serialized_start=1418
  _globals['_ROLE']._serialized_end=1485
  _globals['_ORG']._serialized_start=120
  _globals['_ORG']._serialized_end=388
  _globals['_USER']._serialized_start=391
  _globals['_USER']._serialized_end=591
  _globals['_CREATEORGREQUEST']._serialized_start=593
  _globals['_CREATEORGREQUEST']._serialized_end=640
  _globals['_CREATEORGRESPONSE']._serialized_start=642
  _globals['_CREATEORGRESPONSE']._serialized_end=704
  _globals['_GETORGREQUEST']._serialized_start=706
  _globals['_GETORGREQUEST']._serialized_end=741
  _globals['_GETORGRESPONSE']._serialized_start=743
  _globals['_GETORGRESPONSE']._serialized_end=802
  _globals['_LISTORGSREQUEST']._serialized_start=804
  _globals['_LISTORGSREQUEST']._serialized_end=821
  _globals['_LISTORGSRESPONSE']._serialized_start=823
  _globals['_LISTORGSRESPONSE']._serialized_end=886
  _globals['_LISTORGUSERSREQUEST']._serialized_start=888
  _globals['_LISTORGUSERSREQUEST']._serialized_end=945
  _globals['_LISTORGUSERSRESPONSE']._serialized_start=947
  _globals['_LISTORGUSERSRESPONSE']._serialized_end=1017
  _globals['_ADDORGUSERREQUEST']._serialized_start=1019
  _globals['_ADDORGUSERREQUEST']._serialized_end=1144
  _globals['_ADDORGUSERRESPONSE']._serialized_start=1146
  _globals['_ADDORGUSERRESPONSE']._serialized_end=1212
  _globals['_GETORGUSERREQUEST']._serialized_start=1215
  _globals['_GETORGUSERREQUEST']._serialized_end=1348
  _globals['_GETORGUSERRESPONSE']._serialized_start=1350
  _globals['_GETORGUSERRESPONSE']._serialized_end=1416
  _globals['_ORGSERVICE']._serialized_start=1488
  _globals['_ORGSERVICE']._serialized_end=2055
# @@protoc_insertion_point(module_scope)
