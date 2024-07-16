# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/risk_assessment.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n9google/fhir/r4/proto/core/resources/risk_assessment.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x9e\x17\n\x0eRiskAssessment\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12@\n\x08\x62\x61sed_on\x18\x0b \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12>\n\x06parent\x18\x0c \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12\x46\n\x06status\x18\r \x01(\x0b\x32..google.fhir.r4.core.RiskAssessment.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x34\n\x06method\x18\x0e \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x04\x63ode\x18\x0f \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12O\n\x07subject\x18\x10 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1e\xf0\xd0\x87\xeb\x04\x01\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\x05Group\x12\x42\n\tencounter\x18\x11 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tEncounter\x12\x43\n\noccurrence\x18\x12 \x01(\x0b\x32/.google.fhir.r4.core.RiskAssessment.OccurrenceX\x12\x42\n\tcondition\x18\x13 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tCondition\x12g\n\tperformer\x18\x14 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB4\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\x06\x44\x65vice\x12\x39\n\x0breason_code\x18\x15 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x87\x01\n\x10reason_reference\x18\x16 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBM\xf2\xff\xfc\xc2\x06\tCondition\xf2\xff\xfc\xc2\x06\x0bObservation\xf2\xff\xfc\xc2\x06\x10\x44iagnosticReport\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12=\n\x05\x62\x61sis\x18\x17 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12\x42\n\nprediction\x18\x18 \x03(\x0b\x32..google.fhir.r4.core.RiskAssessment.Prediction\x12/\n\nmitigation\x18\x19 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12-\n\x04note\x18\x1a \x03(\x0b\x32\x1f.google.fhir.r4.core.Annotation\x1a\x98\x02\n\nStatusCode\x12?\n\x05value\x18\x01 \x01(\x0e\x32\x30.google.fhir.r4.core.ObservationStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:m\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05/http://hl7.org/fhir/ValueSet/observation-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x82\x01\n\x0bOccurrenceX\x12\x32\n\tdate_time\x18\x01 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeH\x00\x12-\n\x06period\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.PeriodH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\x96\x07\n\nPrediction\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x35\n\x07outcome\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12P\n\x0bprobability\x18\x05 \x01(\x0b\x32;.google.fhir.r4.core.RiskAssessment.Prediction.ProbabilityX\x12>\n\x10qualitative_risk\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x33\n\rrelative_risk\x18\x07 \x01(\x0b\x32\x1c.google.fhir.r4.core.Decimal\x12\x42\n\x04when\x18\x08 \x01(\x0b\x32\x34.google.fhir.r4.core.RiskAssessment.Prediction.WhenX\x12.\n\trationale\x18\t \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x1a\x86\x02\n\x0cProbabilityX\x12/\n\x07\x64\x65\x63imal\x18\x01 \x01(\x0b\x32\x1c.google.fhir.r4.core.DecimalH\x00\x12+\n\x05range\x18\x02 \x01(\x0b\x32\x1a.google.fhir.r4.core.RangeH\x00:\x8d\x01\x9a\x86\x93\xa0\x08\x80\x01(low.empty() or ((low.code = \'%\') and (low.system = %ucum))) and (high.empty() or ((high.code = \'%\') and (high.system = %ucum)))\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1au\n\x05WhenX\x12-\n\x06period\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.PeriodH\x00\x12+\n\x05range\x18\x02 \x01(\x0b\x32\x1a.google.fhir.r4.core.RangeH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:B\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x36http://hl7.org/fhir/StructureDefinition/RiskAssessmentJ\x04\x08\x07\x10\x08\x42y\n\x17\x63om.google.fhir.r4.coreP\x01ZVgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/risk_assessment_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.risk_assessment_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZVgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/risk_assessment_go_proto\230\306\260\265\007\004'
  _RISKASSESSMENT_STATUSCODE._options = None
  _RISKASSESSMENT_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005/http://hl7.org/fhir/ValueSet/observation-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _RISKASSESSMENT_OCCURRENCEX._options = None
  _RISKASSESSMENT_OCCURRENCEX._serialized_options = b'\240\203\203\350\006\001'
  _RISKASSESSMENT_PREDICTION_PROBABILITYX._options = None
  _RISKASSESSMENT_PREDICTION_PROBABILITYX._serialized_options = b'\232\206\223\240\010\200\001(low.empty() or ((low.code = \'%\') and (low.system = %ucum))) and (high.empty() or ((high.code = \'%\') and (high.system = %ucum)))\240\203\203\350\006\001'
  _RISKASSESSMENT_PREDICTION_WHENX._options = None
  _RISKASSESSMENT_PREDICTION_WHENX._serialized_options = b'\240\203\203\350\006\001'
  _RISKASSESSMENT.fields_by_name['based_on']._options = None
  _RISKASSESSMENT.fields_by_name['based_on']._serialized_options = b'\362\377\374\302\006\010Resource'
  _RISKASSESSMENT.fields_by_name['parent']._options = None
  _RISKASSESSMENT.fields_by_name['parent']._serialized_options = b'\362\377\374\302\006\010Resource'
  _RISKASSESSMENT.fields_by_name['status']._options = None
  _RISKASSESSMENT.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _RISKASSESSMENT.fields_by_name['subject']._options = None
  _RISKASSESSMENT.fields_by_name['subject']._serialized_options = b'\360\320\207\353\004\001\362\377\374\302\006\007Patient\362\377\374\302\006\005Group'
  _RISKASSESSMENT.fields_by_name['encounter']._options = None
  _RISKASSESSMENT.fields_by_name['encounter']._serialized_options = b'\362\377\374\302\006\tEncounter'
  _RISKASSESSMENT.fields_by_name['condition']._options = None
  _RISKASSESSMENT.fields_by_name['condition']._serialized_options = b'\362\377\374\302\006\tCondition'
  _RISKASSESSMENT.fields_by_name['performer']._options = None
  _RISKASSESSMENT.fields_by_name['performer']._serialized_options = b'\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\006Device'
  _RISKASSESSMENT.fields_by_name['reason_reference']._options = None
  _RISKASSESSMENT.fields_by_name['reason_reference']._serialized_options = b'\362\377\374\302\006\tCondition\362\377\374\302\006\013Observation\362\377\374\302\006\020DiagnosticReport\362\377\374\302\006\021DocumentReference'
  _RISKASSESSMENT.fields_by_name['basis']._options = None
  _RISKASSESSMENT.fields_by_name['basis']._serialized_options = b'\362\377\374\302\006\010Resource'
  _RISKASSESSMENT._options = None
  _RISKASSESSMENT._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0066http://hl7.org/fhir/StructureDefinition/RiskAssessment'
  _RISKASSESSMENT._serialized_start=234
  _RISKASSESSMENT._serialized_end=3208
  _RISKASSESSMENT_STATUSCODE._serialized_start=1800
  _RISKASSESSMENT_STATUSCODE._serialized_end=2080
  _RISKASSESSMENT_OCCURRENCEX._serialized_start=2083
  _RISKASSESSMENT_OCCURRENCEX._serialized_end=2213
  _RISKASSESSMENT_PREDICTION._serialized_start=2216
  _RISKASSESSMENT_PREDICTION._serialized_end=3134
  _RISKASSESSMENT_PREDICTION_PROBABILITYX._serialized_start=2753
  _RISKASSESSMENT_PREDICTION_PROBABILITYX._serialized_end=3015
  _RISKASSESSMENT_PREDICTION_WHENX._serialized_start=3017
  _RISKASSESSMENT_PREDICTION_WHENX._serialized_end=3134
# @@protoc_insertion_point(module_scope)
