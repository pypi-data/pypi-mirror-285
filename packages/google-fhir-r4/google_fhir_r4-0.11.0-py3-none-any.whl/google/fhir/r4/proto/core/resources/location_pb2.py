# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/location.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n2google/fhir/r4/proto/core/resources/location.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xa5\x17\n\x08Location\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x38\n\x06status\x18\x0b \x01(\x0b\x32(.google.fhir.r4.core.Location.StatusCode\x12\x37\n\x12operational_status\x18\x0c \x01(\x0b\x32\x1b.google.fhir.r4.core.Coding\x12)\n\x04name\x18\r \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12*\n\x05\x61lias\x18\x0e \x03(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x30\n\x0b\x64\x65scription\x18\x0f \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x34\n\x04mode\x18\x10 \x01(\x0b\x32&.google.fhir.r4.core.Location.ModeCode\x12\x32\n\x04type\x18\x11 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x07telecom\x18\x12 \x03(\x0b\x32!.google.fhir.r4.core.ContactPoint\x12-\n\x07\x61\x64\x64ress\x18\x13 \x01(\x0b\x32\x1c.google.fhir.r4.core.Address\x12;\n\rphysical_type\x18\x14 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x38\n\x08position\x18\x15 \x01(\x0b\x32&.google.fhir.r4.core.Location.Position\x12Q\n\x15managing_organization\x18\x16 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x12?\n\x07part_of\x18\x17 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Location\x12J\n\x12hours_of_operation\x18\x18 \x03(\x0b\x32..google.fhir.r4.core.Location.HoursOfOperation\x12<\n\x17\x61vailability_exceptions\x18\x19 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12@\n\x08\x65ndpoint\x18\x1a \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08\x45ndpoint\x1a\x92\x02\n\nStatusCode\x12<\n\x05value\x18\x01 \x01(\x0e\x32-.google.fhir.r4.core.LocationStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:j\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05,http://hl7.org/fhir/ValueSet/location-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x8c\x02\n\x08ModeCode\x12:\n\x05value\x18\x01 \x01(\x0e\x32+.google.fhir.r4.core.LocationModeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:h\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05*http://hl7.org/fhir/ValueSet/location-mode\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xc3\x02\n\x08Position\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x37\n\tlongitude\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.DecimalB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x36\n\x08latitude\x18\x05 \x01(\x0b\x32\x1c.google.fhir.r4.core.DecimalB\x06\xf0\xd0\x87\xeb\x04\x01\x12.\n\x08\x61ltitude\x18\x06 \x01(\x0b\x32\x1c.google.fhir.r4.core.Decimal\x1a\xa2\x05\n\x10HoursOfOperation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12S\n\x0c\x64\x61ys_of_week\x18\x04 \x03(\x0b\x32=.google.fhir.r4.core.Location.HoursOfOperation.DaysOfWeekCode\x12-\n\x07\x61ll_day\x18\x05 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12/\n\x0copening_time\x18\x06 \x01(\x0b\x32\x19.google.fhir.r4.core.Time\x12/\n\x0c\x63losing_time\x18\x07 \x01(\x0b\x32\x19.google.fhir.r4.core.Time\x1a\x8f\x02\n\x0e\x44\x61ysOfWeekCode\x12\x38\n\x05value\x18\x01 \x01(\x0e\x32).google.fhir.r4.core.DaysOfWeekCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:g\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05)http://hl7.org/fhir/ValueSet/days-of-week\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code:<\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x30http://hl7.org/fhir/StructureDefinition/LocationJ\x04\x08\x07\x10\x08\x42r\n\x17\x63om.google.fhir.r4.coreP\x01ZOgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/location_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.location_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZOgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/location_go_proto\230\306\260\265\007\004'
  _LOCATION_STATUSCODE._options = None
  _LOCATION_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005,http://hl7.org/fhir/ValueSet/location-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _LOCATION_MODECODE._options = None
  _LOCATION_MODECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005*http://hl7.org/fhir/ValueSet/location-mode\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _LOCATION_POSITION.fields_by_name['longitude']._options = None
  _LOCATION_POSITION.fields_by_name['longitude']._serialized_options = b'\360\320\207\353\004\001'
  _LOCATION_POSITION.fields_by_name['latitude']._options = None
  _LOCATION_POSITION.fields_by_name['latitude']._serialized_options = b'\360\320\207\353\004\001'
  _LOCATION_HOURSOFOPERATION_DAYSOFWEEKCODE._options = None
  _LOCATION_HOURSOFOPERATION_DAYSOFWEEKCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005)http://hl7.org/fhir/ValueSet/days-of-week\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _LOCATION.fields_by_name['managing_organization']._options = None
  _LOCATION.fields_by_name['managing_organization']._serialized_options = b'\362\377\374\302\006\014Organization'
  _LOCATION.fields_by_name['part_of']._options = None
  _LOCATION.fields_by_name['part_of']._serialized_options = b'\362\377\374\302\006\010Location'
  _LOCATION.fields_by_name['endpoint']._options = None
  _LOCATION.fields_by_name['endpoint']._serialized_options = b'\362\377\374\302\006\010Endpoint'
  _LOCATION._options = None
  _LOCATION._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0060http://hl7.org/fhir/StructureDefinition/Location'
  _LOCATION._serialized_start=227
  _LOCATION._serialized_end=3208
  _LOCATION_STATUSCODE._serialized_start=1592
  _LOCATION_STATUSCODE._serialized_end=1866
  _LOCATION_MODECODE._serialized_start=1869
  _LOCATION_MODECODE._serialized_end=2137
  _LOCATION_POSITION._serialized_start=2140
  _LOCATION_POSITION._serialized_end=2463
  _LOCATION_HOURSOFOPERATION._serialized_start=2466
  _LOCATION_HOURSOFOPERATION._serialized_end=3140
  _LOCATION_HOURSOFOPERATION_DAYSOFWEEKCODE._serialized_start=2869
  _LOCATION_HOURSOFOPERATION_DAYSOFWEEKCODE._serialized_end=3140
# @@protoc_insertion_point(module_scope)
