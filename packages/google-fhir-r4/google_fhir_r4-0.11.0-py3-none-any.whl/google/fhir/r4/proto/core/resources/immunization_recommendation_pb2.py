# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/immunization_recommendation.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nEgoogle/fhir/r4/proto/core/resources/immunization_recommendation.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x8a\x14\n\x1aImmunizationRecommendation\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x44\n\x07patient\x18\x0b \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x13\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x07Patient\x12\x33\n\x04\x64\x61te\x18\x0c \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x45\n\tauthority\x18\r \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x12^\n\x0erecommendation\x18\x0e \x03(\x0b\x32>.google.fhir.r4.core.ImmunizationRecommendation.RecommendationB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xcb\r\n\x0eRecommendation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x0cvaccine_code\x18\x04 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12<\n\x0etarget_disease\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12J\n\x1c\x63ontraindicated_vaccine_code\x18\x06 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x45\n\x0f\x66orecast_status\x18\x07 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12=\n\x0f\x66orecast_reason\x18\x08 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x64\n\x0e\x64\x61te_criterion\x18\t \x03(\x0b\x32L.google.fhir.r4.core.ImmunizationRecommendation.Recommendation.DateCriterion\x12\x30\n\x0b\x64\x65scription\x18\n \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12+\n\x06series\x18\x0b \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12_\n\x0b\x64ose_number\x18\x0c \x01(\x0b\x32J.google.fhir.r4.core.ImmunizationRecommendation.Recommendation.DoseNumberX\x12\x61\n\x0cseries_doses\x18\r \x01(\x0b\x32K.google.fhir.r4.core.ImmunizationRecommendation.Recommendation.SeriesDosesX\x12o\n\x17supporting_immunization\x18\x0e \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB.\xf2\xff\xfc\xc2\x06\x0cImmunization\xf2\xff\xfc\xc2\x06\x16ImmunizationEvaluation\x12V\n\x1esupporting_patient_information\x18\x0f \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x1a\x99\x02\n\rDateCriterion\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x04\x63ode\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x34\n\x05value\x18\x05 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x96\x01\n\x0b\x44oseNumberX\x12\x38\n\x0cpositive_int\x18\x01 \x01(\x0b\x32 .google.fhir.r4.core.PositiveIntH\x00\x12;\n\x0cstring_value\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\x97\x01\n\x0cSeriesDosesX\x12\x38\n\x0cpositive_int\x18\x01 \x01(\x0b\x32 .google.fhir.r4.core.PositiveIntH\x00\x12;\n\x0cstring_value\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:4\x9a\x86\x93\xa0\x08.vaccineCode.exists() or targetDisease.exists():N\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x42http://hl7.org/fhir/StructureDefinition/ImmunizationRecommendationJ\x04\x08\x07\x10\x08\x42\x85\x01\n\x17\x63om.google.fhir.r4.coreP\x01Zbgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/immunization_recommendation_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.immunization_recommendation_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Zbgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/immunization_recommendation_go_proto\230\306\260\265\007\004'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION.fields_by_name['code']._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION.fields_by_name['code']._serialized_options = b'\360\320\207\353\004\001'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION.fields_by_name['value']._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION.fields_by_name['value']._serialized_options = b'\360\320\207\353\004\001'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DOSENUMBERX._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DOSENUMBERX._serialized_options = b'\240\203\203\350\006\001'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_SERIESDOSESX._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_SERIESDOSESX._serialized_options = b'\240\203\203\350\006\001'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['forecast_status']._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['forecast_status']._serialized_options = b'\360\320\207\353\004\001'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['supporting_immunization']._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['supporting_immunization']._serialized_options = b'\362\377\374\302\006\014Immunization\362\377\374\302\006\026ImmunizationEvaluation'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['supporting_patient_information']._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION.fields_by_name['supporting_patient_information']._serialized_options = b'\362\377\374\302\006\010Resource'
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION._options = None
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION._serialized_options = b'\232\206\223\240\010.vaccineCode.exists() or targetDisease.exists()'
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['patient']._options = None
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['patient']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\007Patient'
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['date']._options = None
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['date']._serialized_options = b'\360\320\207\353\004\001'
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['authority']._options = None
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['authority']._serialized_options = b'\362\377\374\302\006\014Organization'
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['recommendation']._options = None
  _IMMUNIZATIONRECOMMENDATION.fields_by_name['recommendation']._serialized_options = b'\360\320\207\353\004\001'
  _IMMUNIZATIONRECOMMENDATION._options = None
  _IMMUNIZATIONRECOMMENDATION._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006Bhttp://hl7.org/fhir/StructureDefinition/ImmunizationRecommendation'
  _IMMUNIZATIONRECOMMENDATION._serialized_start=207
  _IMMUNIZATIONRECOMMENDATION._serialized_end=2777
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION._serialized_start=952
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION._serialized_end=2691
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION._serialized_start=2049
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DATECRITERION._serialized_end=2330
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DOSENUMBERX._serialized_start=2333
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_DOSENUMBERX._serialized_end=2483
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_SERIESDOSESX._serialized_start=2486
  _IMMUNIZATIONRECOMMENDATION_RECOMMENDATION_SERIESDOSESX._serialized_end=2637
# @@protoc_insertion_point(module_scope)
