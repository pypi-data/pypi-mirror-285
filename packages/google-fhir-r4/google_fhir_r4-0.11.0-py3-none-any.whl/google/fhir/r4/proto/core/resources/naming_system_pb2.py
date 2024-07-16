# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/naming_system.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.fhir.core.proto import annotations_pb2 as google_dot_fhir_dot_core_dot_proto_dot_annotations__pb2
from google.fhir.r4.proto.core import codes_pb2 as google_dot_fhir_dot_r4_dot_proto_dot_core_dot_codes__pb2
from google.fhir.r4.proto.core import datatypes_pb2 as google_dot_fhir_dot_r4_dot_proto_dot_core_dot_datatypes__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n7google/fhir/r4/proto/core/resources/naming_system.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xd2\x14\n\x0cNamingSystem\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x31\n\x04name\x18\n \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x44\n\x06status\x18\x0b \x01(\x0b\x32,.google.fhir.r4.core.NamingSystem.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12@\n\x04kind\x18\x0c \x01(\x0b\x32*.google.fhir.r4.core.NamingSystem.KindCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x33\n\x04\x64\x61te\x18\r \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeB\x06\xf0\xd0\x87\xeb\x04\x01\x12.\n\tpublisher\x18\x0e \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x33\n\x07\x63ontact\x18\x0f \x03(\x0b\x32\".google.fhir.r4.core.ContactDetail\x12\x30\n\x0bresponsible\x18\x10 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x32\n\x04type\x18\x11 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x0b\x64\x65scription\x18\x12 \x01(\x0b\x32\x1d.google.fhir.r4.core.Markdown\x12\x36\n\x0buse_context\x18\x13 \x03(\x0b\x32!.google.fhir.r4.core.UsageContext\x12:\n\x0cjurisdiction\x18\x14 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12*\n\x05usage\x18\x15 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x45\n\tunique_id\x18\x16 \x03(\x0b\x32*.google.fhir.r4.core.NamingSystem.UniqueIdB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x98\x02\n\nStatusCode\x12?\n\x05value\x18\x01 \x01(\x0e\x32\x30.google.fhir.r4.core.PublicationStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:m\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05/http://hl7.org/fhir/ValueSet/publication-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x94\x02\n\x08KindCode\x12>\n\x05value\x18\x01 \x01(\x0e\x32/.google.fhir.r4.core.NamingSystemTypeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:l\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05.http://hl7.org/fhir/ValueSet/namingsystem-type\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xd9\x05\n\x08UniqueId\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12I\n\x04type\x18\x04 \x01(\x0b\x32\x33.google.fhir.r4.core.NamingSystem.UniqueId.TypeCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x32\n\x05value\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12/\n\tpreferred\x18\x06 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12,\n\x07\x63omment\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12+\n\x06period\x18\x08 \x01(\x0b\x32\x1b.google.fhir.r4.core.Period\x1a\xa9\x02\n\x08TypeCode\x12H\n\x05value\x18\x01 \x01(\x0e\x32\x39.google.fhir.r4.core.NamingSystemIdentifierTypeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:w\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x39http://hl7.org/fhir/ValueSet/namingsystem-identifier-type\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code:\xe4\x01\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x34http://hl7.org/fhir/StructureDefinition/NamingSystem\x9a\x86\x93\xa0\x08.kind != \'root\' or uniqueId.all(type != \'uuid\')\x9a\x86\x93\xa0\x08:uniqueId.where(preferred = true).select(type).isDistinct()\x9a\xaf\xae\xa4\x0b*name.matches(\'[A-Z]([A-Za-z0-9_]){0,254}\')J\x04\x08\x07\x10\x08\x42w\n\x17\x63om.google.fhir.r4.coreP\x01ZTgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/naming_system_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.naming_system_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZTgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/naming_system_go_proto\230\306\260\265\007\004'
  _NAMINGSYSTEM_STATUSCODE._options = None
  _NAMINGSYSTEM_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005/http://hl7.org/fhir/ValueSet/publication-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _NAMINGSYSTEM_KINDCODE._options = None
  _NAMINGSYSTEM_KINDCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005.http://hl7.org/fhir/ValueSet/namingsystem-type\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _NAMINGSYSTEM_UNIQUEID_TYPECODE._options = None
  _NAMINGSYSTEM_UNIQUEID_TYPECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0059http://hl7.org/fhir/ValueSet/namingsystem-identifier-type\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _NAMINGSYSTEM_UNIQUEID.fields_by_name['type']._options = None
  _NAMINGSYSTEM_UNIQUEID.fields_by_name['type']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM_UNIQUEID.fields_by_name['value']._options = None
  _NAMINGSYSTEM_UNIQUEID.fields_by_name['value']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM.fields_by_name['name']._options = None
  _NAMINGSYSTEM.fields_by_name['name']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM.fields_by_name['status']._options = None
  _NAMINGSYSTEM.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM.fields_by_name['kind']._options = None
  _NAMINGSYSTEM.fields_by_name['kind']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM.fields_by_name['date']._options = None
  _NAMINGSYSTEM.fields_by_name['date']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM.fields_by_name['unique_id']._options = None
  _NAMINGSYSTEM.fields_by_name['unique_id']._serialized_options = b'\360\320\207\353\004\001'
  _NAMINGSYSTEM._options = None
  _NAMINGSYSTEM._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0064http://hl7.org/fhir/StructureDefinition/NamingSystem\232\206\223\240\010.kind != \'root\' or uniqueId.all(type != \'uuid\')\232\206\223\240\010:uniqueId.where(preferred = true).select(type).isDistinct()\232\257\256\244\013*name.matches(\'[A-Z]([A-Za-z0-9_]){0,254}\')'
  _NAMINGSYSTEM._serialized_start=232
  _NAMINGSYSTEM._serialized_end=2874
  _NAMINGSYSTEM_STATUSCODE._serialized_start=1346
  _NAMINGSYSTEM_STATUSCODE._serialized_end=1626
  _NAMINGSYSTEM_KINDCODE._serialized_start=1629
  _NAMINGSYSTEM_KINDCODE._serialized_end=1905
  _NAMINGSYSTEM_UNIQUEID._serialized_start=1908
  _NAMINGSYSTEM_UNIQUEID._serialized_end=2637
  _NAMINGSYSTEM_UNIQUEID_TYPECODE._serialized_start=2340
  _NAMINGSYSTEM_UNIQUEID_TYPECODE._serialized_end=2637
# @@protoc_insertion_point(module_scope)
