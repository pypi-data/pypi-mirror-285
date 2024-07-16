# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/basic.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.fhir.core.proto import annotations_pb2 as google_dot_fhir_dot_core_dot_proto_dot_annotations__pb2
from google.fhir.r4.proto.core import datatypes_pb2 as google_dot_fhir_dot_r4_dot_proto_dot_core_dot_datatypes__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n/google/fhir/r4/proto/core/resources/basic.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xa6\x06\n\x05\x42\x61sic\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12:\n\x04\x63ode\x18\x0b \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12?\n\x07subject\x18\x0c \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12*\n\x07\x63reated\x18\r \x01(\x0b\x32\x19.google.fhir.r4.core.Date\x12\x8a\x01\n\x06\x61uthor\x18\x0e \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBZ\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\rRelatedPerson\xf2\xff\xfc\xc2\x06\x0cOrganization:9\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06-http://hl7.org/fhir/StructureDefinition/BasicJ\x04\x08\x07\x10\x08\x42o\n\x17\x63om.google.fhir.r4.coreP\x01ZLgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/basic_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.basic_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZLgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/basic_go_proto\230\306\260\265\007\004'
  _BASIC.fields_by_name['code']._options = None
  _BASIC.fields_by_name['code']._serialized_options = b'\360\320\207\353\004\001'
  _BASIC.fields_by_name['subject']._options = None
  _BASIC.fields_by_name['subject']._serialized_options = b'\362\377\374\302\006\010Resource'
  _BASIC.fields_by_name['author']._options = None
  _BASIC.fields_by_name['author']._serialized_options = b'\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\007Patient\362\377\374\302\006\rRelatedPerson\362\377\374\302\006\014Organization'
  _BASIC._options = None
  _BASIC._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006-http://hl7.org/fhir/StructureDefinition/Basic'
  _BASIC._serialized_start=185
  _BASIC._serialized_end=991
# @@protoc_insertion_point(module_scope)
