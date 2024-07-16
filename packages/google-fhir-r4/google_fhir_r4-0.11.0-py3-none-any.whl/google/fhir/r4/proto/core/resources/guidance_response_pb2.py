# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/guidance_response.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n;google/fhir/r4/proto/core/resources/guidance_response.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xec\x0f\n\x10GuidanceResponse\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12;\n\x12request_identifier\x18\n \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x33\n\nidentifier\x18\x0b \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x45\n\x06module\x18\x0c \x01(\x0b\x32-.google.fhir.r4.core.GuidanceResponse.ModuleXB\x06\xf0\xd0\x87\xeb\x04\x01\x12H\n\x06status\x18\r \x01(\x0b\x32\x30.google.fhir.r4.core.GuidanceResponse.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12I\n\x07subject\x18\x0e \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x18\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\x05Group\x12\x42\n\tencounter\x18\x0f \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tEncounter\x12;\n\x14occurrence_date_time\x18\x10 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12?\n\tperformer\x18\x11 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0c\xf2\xff\xfc\xc2\x06\x06\x44\x65vice\x12\x39\n\x0breason_code\x18\x12 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x87\x01\n\x10reason_reference\x18\x13 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBM\xf2\xff\xfc\xc2\x06\tCondition\xf2\xff\xfc\xc2\x06\x0bObservation\xf2\xff\xfc\xc2\x06\x10\x44iagnosticReport\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12-\n\x04note\x18\x14 \x03(\x0b\x32\x1f.google.fhir.r4.core.Annotation\x12R\n\x12\x65valuation_message\x18\x15 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x16\xf2\xff\xfc\xc2\x06\x10OperationOutcome\x12K\n\x11output_parameters\x18\x16 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x10\xf2\xff\xfc\xc2\x06\nParameters\x12P\n\x06result\x18\x17 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB \xf2\xff\xfc\xc2\x06\x08\x43\x61rePlan\xf2\xff\xfc\xc2\x06\x0cRequestGroup\x12>\n\x10\x64\x61ta_requirement\x18\x18 \x03(\x0b\x32$.google.fhir.r4.core.DataRequirement\x1a\xbb\x01\n\x07ModuleX\x12\'\n\x03uri\x18\x01 \x01(\x0b\x32\x18.google.fhir.r4.core.UriH\x00\x12\x33\n\tcanonical\x18\x02 \x01(\x0b\x32\x1e.google.fhir.r4.core.CanonicalH\x00\x12@\n\x10\x63odeable_concept\x18\x03 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xa3\x02\n\nStatusCode\x12\x44\n\x05value\x18\x01 \x01(\x0e\x32\x35.google.fhir.r4.core.GuidanceResponseStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:s\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x35http://hl7.org/fhir/ValueSet/guidance-response-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code:D\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x38http://hl7.org/fhir/StructureDefinition/GuidanceResponseJ\x04\x08\x07\x10\x08\x42{\n\x17\x63om.google.fhir.r4.coreP\x01ZXgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/guidance_response_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.guidance_response_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZXgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/guidance_response_go_proto\230\306\260\265\007\004'
  _GUIDANCERESPONSE_MODULEX._options = None
  _GUIDANCERESPONSE_MODULEX._serialized_options = b'\240\203\203\350\006\001'
  _GUIDANCERESPONSE_STATUSCODE._options = None
  _GUIDANCERESPONSE_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0055http://hl7.org/fhir/ValueSet/guidance-response-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _GUIDANCERESPONSE.fields_by_name['module']._options = None
  _GUIDANCERESPONSE.fields_by_name['module']._serialized_options = b'\360\320\207\353\004\001'
  _GUIDANCERESPONSE.fields_by_name['status']._options = None
  _GUIDANCERESPONSE.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _GUIDANCERESPONSE.fields_by_name['subject']._options = None
  _GUIDANCERESPONSE.fields_by_name['subject']._serialized_options = b'\362\377\374\302\006\007Patient\362\377\374\302\006\005Group'
  _GUIDANCERESPONSE.fields_by_name['encounter']._options = None
  _GUIDANCERESPONSE.fields_by_name['encounter']._serialized_options = b'\362\377\374\302\006\tEncounter'
  _GUIDANCERESPONSE.fields_by_name['performer']._options = None
  _GUIDANCERESPONSE.fields_by_name['performer']._serialized_options = b'\362\377\374\302\006\006Device'
  _GUIDANCERESPONSE.fields_by_name['reason_reference']._options = None
  _GUIDANCERESPONSE.fields_by_name['reason_reference']._serialized_options = b'\362\377\374\302\006\tCondition\362\377\374\302\006\013Observation\362\377\374\302\006\020DiagnosticReport\362\377\374\302\006\021DocumentReference'
  _GUIDANCERESPONSE.fields_by_name['evaluation_message']._options = None
  _GUIDANCERESPONSE.fields_by_name['evaluation_message']._serialized_options = b'\362\377\374\302\006\020OperationOutcome'
  _GUIDANCERESPONSE.fields_by_name['output_parameters']._options = None
  _GUIDANCERESPONSE.fields_by_name['output_parameters']._serialized_options = b'\362\377\374\302\006\nParameters'
  _GUIDANCERESPONSE.fields_by_name['result']._options = None
  _GUIDANCERESPONSE.fields_by_name['result']._serialized_options = b'\362\377\374\302\006\010CarePlan\362\377\374\302\006\014RequestGroup'
  _GUIDANCERESPONSE._options = None
  _GUIDANCERESPONSE._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0068http://hl7.org/fhir/StructureDefinition/GuidanceResponse'
  _GUIDANCERESPONSE._serialized_start=236
  _GUIDANCERESPONSE._serialized_end=2264
  _GUIDANCERESPONSE_MODULEX._serialized_start=1707
  _GUIDANCERESPONSE_MODULEX._serialized_end=1894
  _GUIDANCERESPONSE_STATUSCODE._serialized_start=1897
  _GUIDANCERESPONSE_STATUSCODE._serialized_end=2188
# @@protoc_insertion_point(module_scope)
