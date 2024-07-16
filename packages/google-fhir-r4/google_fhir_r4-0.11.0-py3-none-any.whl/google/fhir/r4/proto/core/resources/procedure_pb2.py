# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/procedure.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n3google/fhir/r4/proto/core/resources/procedure.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x82\x1e\n\tProcedure\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12>\n\x16instantiates_canonical\x18\x0b \x03(\x0b\x32\x1e.google.fhir.r4.core.Canonical\x12\x32\n\x10instantiates_uri\x18\x0c \x03(\x0b\x32\x18.google.fhir.r4.core.Uri\x12T\n\x08\x62\x61sed_on\x18\r \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\"\xf2\xff\xfc\xc2\x06\x08\x43\x61rePlan\xf2\xff\xfc\xc2\x06\x0eServiceRequest\x12o\n\x07part_of\x18\x0e \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB>\xf2\xff\xfc\xc2\x06\tProcedure\xf2\xff\xfc\xc2\x06\x0bObservation\xf2\xff\xfc\xc2\x06\x18MedicationAdministration\x12\x41\n\x06status\x18\x0f \x01(\x0b\x32).google.fhir.r4.core.Procedure.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12;\n\rstatus_reason\x18\x10 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x36\n\x08\x63\x61tegory\x18\x11 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x04\x63ode\x18\x12 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12O\n\x07subject\x18\x13 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1e\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\x05Group\x12\x42\n\tencounter\x18\x14 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tEncounter\x12<\n\tperformed\x18\x15 \x01(\x0b\x32).google.fhir.r4.core.Procedure.PerformedX\x12z\n\x08recorder\x18\x16 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBH\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\rRelatedPerson\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\x12z\n\x08\x61sserter\x18\x17 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBH\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\rRelatedPerson\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\x12;\n\tperformer\x18\x18 \x03(\x0b\x32(.google.fhir.r4.core.Procedure.Performer\x12@\n\x08location\x18\x19 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Location\x12\x39\n\x0breason_code\x18\x1a \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x96\x01\n\x10reason_reference\x18\x1b \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\\\xf2\xff\xfc\xc2\x06\tCondition\xf2\xff\xfc\xc2\x06\x0bObservation\xf2\xff\xfc\xc2\x06\tProcedure\xf2\xff\xfc\xc2\x06\x10\x44iagnosticReport\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12\x37\n\tbody_site\x18\x1c \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x35\n\x07outcome\x18\x1d \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12n\n\x06report\x18\x1e \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB>\xf2\xff\xfc\xc2\x06\x10\x44iagnosticReport\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\xf2\xff\xfc\xc2\x06\x0b\x43omposition\x12:\n\x0c\x63omplication\x18\x1f \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12L\n\x13\x63omplication_detail\x18  \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tCondition\x12\x37\n\tfollow_up\x18! \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12-\n\x04note\x18\" \x03(\x0b\x32\x1f.google.fhir.r4.core.Annotation\x12@\n\x0c\x66ocal_device\x18# \x03(\x0b\x32*.google.fhir.r4.core.Procedure.FocalDevice\x12\x63\n\x0eused_reference\x18$ \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB+\xf2\xff\xfc\xc2\x06\x06\x44\x65vice\xf2\xff\xfc\xc2\x06\nMedication\xf2\xff\xfc\xc2\x06\tSubstance\x12\x37\n\tused_code\x18% \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x1a\x8c\x02\n\nStatusCode\x12\x39\n\x05value\x18\x01 \x01(\x0e\x32*.google.fhir.r4.core.EventStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:g\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05)http://hl7.org/fhir/ValueSet/event-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x94\x02\n\nPerformedX\x12\x32\n\tdate_time\x18\x01 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeH\x00\x12-\n\x06period\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.PeriodH\x00\x12;\n\x0cstring_value\x18\x03 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string\x12\'\n\x03\x61ge\x18\x04 \x01(\x0b\x32\x18.google.fhir.r4.core.AgeH\x00\x12+\n\x05range\x18\x05 \x01(\x0b\x32\x1a.google.fhir.r4.core.RangeH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xc3\x03\n\tPerformer\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x36\n\x08\x66unction\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x9b\x01\n\x05\x61\x63tor\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBl\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\x0cOrganization\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\rRelatedPerson\xf2\xff\xfc\xc2\x06\x06\x44\x65vice\x12H\n\x0con_behalf_of\x18\x06 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x1a\xa4\x02\n\x0b\x46ocalDevice\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x34\n\x06\x61\x63tion\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12G\n\x0bmanipulated\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x06\x44\x65vice:=\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x31http://hl7.org/fhir/StructureDefinition/ProcedureJ\x04\x08\x07\x10\x08\x42s\n\x17\x63om.google.fhir.r4.coreP\x01ZPgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/procedure_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.procedure_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZPgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/procedure_go_proto\230\306\260\265\007\004'
  _PROCEDURE_STATUSCODE._options = None
  _PROCEDURE_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005)http://hl7.org/fhir/ValueSet/event-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _PROCEDURE_PERFORMEDX._options = None
  _PROCEDURE_PERFORMEDX._serialized_options = b'\240\203\203\350\006\001'
  _PROCEDURE_PERFORMER.fields_by_name['actor']._options = None
  _PROCEDURE_PERFORMER.fields_by_name['actor']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\014Organization\362\377\374\302\006\007Patient\362\377\374\302\006\rRelatedPerson\362\377\374\302\006\006Device'
  _PROCEDURE_PERFORMER.fields_by_name['on_behalf_of']._options = None
  _PROCEDURE_PERFORMER.fields_by_name['on_behalf_of']._serialized_options = b'\362\377\374\302\006\014Organization'
  _PROCEDURE_FOCALDEVICE.fields_by_name['manipulated']._options = None
  _PROCEDURE_FOCALDEVICE.fields_by_name['manipulated']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\006Device'
  _PROCEDURE.fields_by_name['based_on']._options = None
  _PROCEDURE.fields_by_name['based_on']._serialized_options = b'\362\377\374\302\006\010CarePlan\362\377\374\302\006\016ServiceRequest'
  _PROCEDURE.fields_by_name['part_of']._options = None
  _PROCEDURE.fields_by_name['part_of']._serialized_options = b'\362\377\374\302\006\tProcedure\362\377\374\302\006\013Observation\362\377\374\302\006\030MedicationAdministration'
  _PROCEDURE.fields_by_name['status']._options = None
  _PROCEDURE.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _PROCEDURE.fields_by_name['subject']._options = None
  _PROCEDURE.fields_by_name['subject']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\007Patient\362\377\374\302\006\005Group'
  _PROCEDURE.fields_by_name['encounter']._options = None
  _PROCEDURE.fields_by_name['encounter']._serialized_options = b'\362\377\374\302\006\tEncounter'
  _PROCEDURE.fields_by_name['recorder']._options = None
  _PROCEDURE.fields_by_name['recorder']._serialized_options = b'\362\377\374\302\006\007Patient\362\377\374\302\006\rRelatedPerson\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole'
  _PROCEDURE.fields_by_name['asserter']._options = None
  _PROCEDURE.fields_by_name['asserter']._serialized_options = b'\362\377\374\302\006\007Patient\362\377\374\302\006\rRelatedPerson\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole'
  _PROCEDURE.fields_by_name['location']._options = None
  _PROCEDURE.fields_by_name['location']._serialized_options = b'\362\377\374\302\006\010Location'
  _PROCEDURE.fields_by_name['reason_reference']._options = None
  _PROCEDURE.fields_by_name['reason_reference']._serialized_options = b'\362\377\374\302\006\tCondition\362\377\374\302\006\013Observation\362\377\374\302\006\tProcedure\362\377\374\302\006\020DiagnosticReport\362\377\374\302\006\021DocumentReference'
  _PROCEDURE.fields_by_name['report']._options = None
  _PROCEDURE.fields_by_name['report']._serialized_options = b'\362\377\374\302\006\020DiagnosticReport\362\377\374\302\006\021DocumentReference\362\377\374\302\006\013Composition'
  _PROCEDURE.fields_by_name['complication_detail']._options = None
  _PROCEDURE.fields_by_name['complication_detail']._serialized_options = b'\362\377\374\302\006\tCondition'
  _PROCEDURE.fields_by_name['used_reference']._options = None
  _PROCEDURE.fields_by_name['used_reference']._serialized_options = b'\362\377\374\302\006\006Device\362\377\374\302\006\nMedication\362\377\374\302\006\tSubstance'
  _PROCEDURE._options = None
  _PROCEDURE._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0061http://hl7.org/fhir/StructureDefinition/Procedure'
  _PROCEDURE._serialized_start=228
  _PROCEDURE._serialized_end=4070
  _PROCEDURE_STATUSCODE._serialized_start=2705
  _PROCEDURE_STATUSCODE._serialized_end=2973
  _PROCEDURE_PERFORMEDX._serialized_start=2976
  _PROCEDURE_PERFORMEDX._serialized_end=3252
  _PROCEDURE_PERFORMER._serialized_start=3255
  _PROCEDURE_PERFORMER._serialized_end=3706
  _PROCEDURE_FOCALDEVICE._serialized_start=3709
  _PROCEDURE_FOCALDEVICE._serialized_end=4001
# @@protoc_insertion_point(module_scope)
