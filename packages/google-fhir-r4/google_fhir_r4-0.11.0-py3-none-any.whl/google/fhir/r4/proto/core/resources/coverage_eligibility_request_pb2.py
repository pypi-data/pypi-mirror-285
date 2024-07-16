# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/coverage_eligibility_request.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nFgoogle/fhir/r4/proto/core/resources/coverage_eligibility_request.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x8b!\n\x1a\x43overageEligibilityRequest\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12R\n\x06status\x18\x0b \x01(\x0b\x32:.google.fhir.r4.core.CoverageEligibilityRequest.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x36\n\x08priority\x18\x0c \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12T\n\x07purpose\x18\r \x03(\x0b\x32;.google.fhir.r4.core.CoverageEligibilityRequest.PurposeCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x44\n\x07patient\x18\x0e \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x13\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x07Patient\x12K\n\x08serviced\x18\x0f \x01(\x0b\x32\x39.google.fhir.r4.core.CoverageEligibilityRequest.ServicedX\x12\x36\n\x07\x63reated\x18\x10 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeB\x06\xf0\xd0\x87\xeb\x04\x01\x12Y\n\x07\x65nterer\x18\x11 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB(\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\x12l\n\x08provider\x18\x12 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB:\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\x0cOrganization\x12I\n\x07insurer\x18\x13 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x18\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x0cOrganization\x12@\n\x08\x66\x61\x63ility\x18\x14 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Location\x12^\n\x0fsupporting_info\x18\x15 \x03(\x0b\x32\x45.google.fhir.r4.core.CoverageEligibilityRequest.SupportingInformation\x12L\n\tinsurance\x18\x16 \x03(\x0b\x32\x39.google.fhir.r4.core.CoverageEligibilityRequest.Insurance\x12\x45\n\x04item\x18\x17 \x03(\x0b\x32\x37.google.fhir.r4.core.CoverageEligibilityRequest.Details\x1a\x95\x02\n\nStatusCode\x12\x45\n\x05value\x18\x01 \x01(\x0e\x32\x36.google.fhir.r4.core.FinancialResourceStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:d\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05&http://hl7.org/fhir/ValueSet/fm-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xa9\x02\n\x0bPurposeCode\x12G\n\x05value\x18\x01 \x01(\x0e\x32\x38.google.fhir.r4.core.EligibilityRequestPurposeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:u\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x37http://hl7.org/fhir/ValueSet/eligibilityrequest-purpose\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1aw\n\tServicedX\x12)\n\x04\x64\x61te\x18\x01 \x01(\x0b\x32\x19.google.fhir.r4.core.DateH\x00\x12-\n\x06period\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.PeriodH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xec\x02\n\x15SupportingInformation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x08sequence\x18\x04 \x01(\x0b\x32 .google.fhir.r4.core.PositiveIntB\x06\xf0\xd0\x87\xeb\x04\x01\x12I\n\x0binformation\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x14\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x08Resource\x12\x34\n\x0e\x61pplies_to_all\x18\x06 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x1a\xd3\x02\n\tInsurance\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12+\n\x05\x66ocal\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12\x46\n\x08\x63overage\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x14\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x08\x43overage\x12\x39\n\x14\x62usiness_arrangement\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x1a\xf4\t\n\x07\x44\x65tails\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x42\n\x18supporting_info_sequence\x18\x04 \x03(\x0b\x32 .google.fhir.r4.core.PositiveInt\x12\x36\n\x08\x63\x61tegory\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12@\n\x12product_or_service\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x36\n\x08modifier\x18\x07 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12Z\n\x08provider\x18\x08 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB(\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\x12\x35\n\x08quantity\x18\t \x01(\x0b\x32#.google.fhir.r4.core.SimpleQuantity\x12.\n\nunit_price\x18\n \x01(\x0b\x32\x1a.google.fhir.r4.core.Money\x12R\n\x08\x66\x61\x63ility\x18\x0b \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB \xf2\xff\xfc\xc2\x06\x08Location\xf2\xff\xfc\xc2\x06\x0cOrganization\x12T\n\tdiagnosis\x18\x0c \x03(\x0b\x32\x41.google.fhir.r4.core.CoverageEligibilityRequest.Details.Diagnosis\x12>\n\x06\x64\x65tail\x18\r \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x1a\xad\x03\n\tDiagnosis\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12_\n\tdiagnosis\x18\x04 \x01(\x0b\x32L.google.fhir.r4.core.CoverageEligibilityRequest.Details.Diagnosis.DiagnosisX\x1a\xa6\x01\n\nDiagnosisX\x12@\n\x10\x63odeable_concept\x18\x01 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00\x12\x44\n\treference\x18\x02 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tConditionH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:N\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x42http://hl7.org/fhir/StructureDefinition/CoverageEligibilityRequestJ\x04\x08\x07\x10\x08\x42\x86\x01\n\x17\x63om.google.fhir.r4.coreP\x01Zcgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/coverage_eligibility_request_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.coverage_eligibility_request_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Zcgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/coverage_eligibility_request_go_proto\230\306\260\265\007\004'
  _COVERAGEELIGIBILITYREQUEST_STATUSCODE._options = None
  _COVERAGEELIGIBILITYREQUEST_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005&http://hl7.org/fhir/ValueSet/fm-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _COVERAGEELIGIBILITYREQUEST_PURPOSECODE._options = None
  _COVERAGEELIGIBILITYREQUEST_PURPOSECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0057http://hl7.org/fhir/ValueSet/eligibilityrequest-purpose\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _COVERAGEELIGIBILITYREQUEST_SERVICEDX._options = None
  _COVERAGEELIGIBILITYREQUEST_SERVICEDX._serialized_options = b'\240\203\203\350\006\001'
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION.fields_by_name['sequence']._options = None
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION.fields_by_name['sequence']._serialized_options = b'\360\320\207\353\004\001'
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION.fields_by_name['information']._options = None
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION.fields_by_name['information']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\010Resource'
  _COVERAGEELIGIBILITYREQUEST_INSURANCE.fields_by_name['coverage']._options = None
  _COVERAGEELIGIBILITYREQUEST_INSURANCE.fields_by_name['coverage']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\010Coverage'
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX.fields_by_name['reference']._options = None
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\tCondition'
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX._options = None
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX._serialized_options = b'\240\203\203\350\006\001'
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['provider']._options = None
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['provider']._serialized_options = b'\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole'
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['facility']._options = None
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['facility']._serialized_options = b'\362\377\374\302\006\010Location\362\377\374\302\006\014Organization'
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['detail']._options = None
  _COVERAGEELIGIBILITYREQUEST_DETAILS.fields_by_name['detail']._serialized_options = b'\362\377\374\302\006\010Resource'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['status']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['purpose']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['purpose']._serialized_options = b'\360\320\207\353\004\001'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['patient']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['patient']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\007Patient'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['created']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['created']._serialized_options = b'\360\320\207\353\004\001'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['enterer']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['enterer']._serialized_options = b'\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['provider']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['provider']._serialized_options = b'\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\014Organization'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['insurer']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['insurer']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\014Organization'
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['facility']._options = None
  _COVERAGEELIGIBILITYREQUEST.fields_by_name['facility']._serialized_options = b'\362\377\374\302\006\010Location'
  _COVERAGEELIGIBILITYREQUEST._options = None
  _COVERAGEELIGIBILITYREQUEST._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006Bhttp://hl7.org/fhir/StructureDefinition/CoverageEligibilityRequest'
  _COVERAGEELIGIBILITYREQUEST._serialized_start=247
  _COVERAGEELIGIBILITYREQUEST._serialized_end=4482
  _COVERAGEELIGIBILITYREQUEST_STATUSCODE._serialized_start=1718
  _COVERAGEELIGIBILITYREQUEST_STATUSCODE._serialized_end=1995
  _COVERAGEELIGIBILITYREQUEST_PURPOSECODE._serialized_start=1998
  _COVERAGEELIGIBILITYREQUEST_PURPOSECODE._serialized_end=2295
  _COVERAGEELIGIBILITYREQUEST_SERVICEDX._serialized_start=2297
  _COVERAGEELIGIBILITYREQUEST_SERVICEDX._serialized_end=2416
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION._serialized_start=2419
  _COVERAGEELIGIBILITYREQUEST_SUPPORTINGINFORMATION._serialized_end=2783
  _COVERAGEELIGIBILITYREQUEST_INSURANCE._serialized_start=2786
  _COVERAGEELIGIBILITYREQUEST_INSURANCE._serialized_end=3125
  _COVERAGEELIGIBILITYREQUEST_DETAILS._serialized_start=3128
  _COVERAGEELIGIBILITYREQUEST_DETAILS._serialized_end=4396
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS._serialized_start=3967
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS._serialized_end=4396
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX._serialized_start=4230
  _COVERAGEELIGIBILITYREQUEST_DETAILS_DIAGNOSIS_DIAGNOSISX._serialized_end=4396
# @@protoc_insertion_point(module_scope)
