# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/questionnaire_response.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n@google/fhir/r4/proto/core/resources/questionnaire_response.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x8c\x18\n\x15QuestionnaireResponse\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12T\n\x08\x62\x61sed_on\x18\x0b \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\"\xf2\xff\xfc\xc2\x06\x08\x43\x61rePlan\xf2\xff\xfc\xc2\x06\x0eServiceRequest\x12Q\n\x07part_of\x18\x0c \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB \xf2\xff\xfc\xc2\x06\x0bObservation\xf2\xff\xfc\xc2\x06\tProcedure\x12\x35\n\rquestionnaire\x18\r \x01(\x0b\x32\x1e.google.fhir.r4.core.Canonical\x12M\n\x06status\x18\x0e \x01(\x0b\x32\x35.google.fhir.r4.core.QuestionnaireResponse.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12?\n\x07subject\x18\x0f \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12\x42\n\tencounter\x18\x10 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0f\xf2\xff\xfc\xc2\x06\tEncounter\x12/\n\x08\x61uthored\x18\x11 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12\x96\x01\n\x06\x61uthor\x18\x12 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBf\xf2\xff\xfc\xc2\x06\x06\x44\x65vice\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\rRelatedPerson\xf2\xff\xfc\xc2\x06\x0cOrganization\x12x\n\x06source\x18\x13 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBH\xf2\xff\xfc\xc2\x06\x07Patient\xf2\xff\xfc\xc2\x06\x0cPractitioner\xf2\xff\xfc\xc2\x06\x10PractitionerRole\xf2\xff\xfc\xc2\x06\rRelatedPerson\x12=\n\x04item\x18\x14 \x03(\x0b\x32/.google.fhir.r4.core.QuestionnaireResponse.Item\x1a\xac\x02\n\nStatusCode\x12I\n\x05value\x18\x01 \x01(\x0e\x32:.google.fhir.r4.core.QuestionnaireResponseStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:w\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x39http://hl7.org/fhir/ValueSet/questionnaire-answers-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x93\x0b\n\x04Item\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x34\n\x07link_id\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12,\n\ndefinition\x18\x05 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12)\n\x04text\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x46\n\x06\x61nswer\x18\x07 \x03(\x0b\x32\x36.google.fhir.r4.core.QuestionnaireResponse.Item.Answer\x12=\n\x04item\x18\x08 \x03(\x0b\x32/.google.fhir.r4.core.QuestionnaireResponse.Item\x1a\xab\x07\n\x06\x41nswer\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12L\n\x05value\x18\x04 \x01(\x0b\x32=.google.fhir.r4.core.QuestionnaireResponse.Item.Answer.ValueX\x12=\n\x04item\x18\x05 \x03(\x0b\x32/.google.fhir.r4.core.QuestionnaireResponse.Item\x1a\xfb\x04\n\x06ValueX\x12/\n\x07\x62oolean\x18\x01 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanH\x00\x12/\n\x07\x64\x65\x63imal\x18\x02 \x01(\x0b\x32\x1c.google.fhir.r4.core.DecimalH\x00\x12/\n\x07integer\x18\x03 \x01(\x0b\x32\x1c.google.fhir.r4.core.IntegerH\x00\x12)\n\x04\x64\x61te\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.DateH\x00\x12\x32\n\tdate_time\x18\x05 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTimeH\x00\x12)\n\x04time\x18\x06 \x01(\x0b\x32\x19.google.fhir.r4.core.TimeH\x00\x12;\n\x0cstring_value\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string\x12\'\n\x03uri\x18\x08 \x01(\x0b\x32\x18.google.fhir.r4.core.UriH\x00\x12\x35\n\nattachment\x18\t \x01(\x0b\x32\x1f.google.fhir.r4.core.AttachmentH\x00\x12-\n\x06\x63oding\x18\n \x01(\x0b\x32\x1b.google.fhir.r4.core.CodingH\x00\x12\x31\n\x08quantity\x18\x0b \x01(\x0b\x32\x1d.google.fhir.r4.core.QuantityH\x00\x12\x43\n\treference\x18\x0c \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08ResourceH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:/\x9a\x86\x93\xa0\x08)(answer.exists() and item.exists()).not():I\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06=http://hl7.org/fhir/StructureDefinition/QuestionnaireResponseJ\x04\x08\x07\x10\x08\x42\x80\x01\n\x17\x63om.google.fhir.r4.coreP\x01Z]github.com/google/fhir/go/google/fhir/r4/proto/core/resources/questionnaire_response_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.questionnaire_response_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Z]github.com/google/fhir/go/google/fhir/r4/proto/core/resources/questionnaire_response_go_proto\230\306\260\265\007\004'
  _QUESTIONNAIRERESPONSE_STATUSCODE._options = None
  _QUESTIONNAIRERESPONSE_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0059http://hl7.org/fhir/ValueSet/questionnaire-answers-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX.fields_by_name['reference']._options = None
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\010Resource'
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX._options = None
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX._serialized_options = b'\240\203\203\350\006\001'
  _QUESTIONNAIRERESPONSE_ITEM.fields_by_name['link_id']._options = None
  _QUESTIONNAIRERESPONSE_ITEM.fields_by_name['link_id']._serialized_options = b'\360\320\207\353\004\001'
  _QUESTIONNAIRERESPONSE_ITEM._options = None
  _QUESTIONNAIRERESPONSE_ITEM._serialized_options = b'\232\206\223\240\010)(answer.exists() and item.exists()).not()'
  _QUESTIONNAIRERESPONSE.fields_by_name['based_on']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['based_on']._serialized_options = b'\362\377\374\302\006\010CarePlan\362\377\374\302\006\016ServiceRequest'
  _QUESTIONNAIRERESPONSE.fields_by_name['part_of']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['part_of']._serialized_options = b'\362\377\374\302\006\013Observation\362\377\374\302\006\tProcedure'
  _QUESTIONNAIRERESPONSE.fields_by_name['status']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _QUESTIONNAIRERESPONSE.fields_by_name['subject']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['subject']._serialized_options = b'\362\377\374\302\006\010Resource'
  _QUESTIONNAIRERESPONSE.fields_by_name['encounter']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['encounter']._serialized_options = b'\362\377\374\302\006\tEncounter'
  _QUESTIONNAIRERESPONSE.fields_by_name['author']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['author']._serialized_options = b'\362\377\374\302\006\006Device\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\007Patient\362\377\374\302\006\rRelatedPerson\362\377\374\302\006\014Organization'
  _QUESTIONNAIRERESPONSE.fields_by_name['source']._options = None
  _QUESTIONNAIRERESPONSE.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\007Patient\362\377\374\302\006\014Practitioner\362\377\374\302\006\020PractitionerRole\362\377\374\302\006\rRelatedPerson'
  _QUESTIONNAIRERESPONSE._options = None
  _QUESTIONNAIRERESPONSE._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006=http://hl7.org/fhir/StructureDefinition/QuestionnaireResponse'
  _QUESTIONNAIRERESPONSE._serialized_start=241
  _QUESTIONNAIRERESPONSE._serialized_end=3325
  _QUESTIONNAIRERESPONSE_STATUSCODE._serialized_start=1514
  _QUESTIONNAIRERESPONSE_STATUSCODE._serialized_end=1814
  _QUESTIONNAIRERESPONSE_ITEM._serialized_start=1817
  _QUESTIONNAIRERESPONSE_ITEM._serialized_end=3244
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER._serialized_start=2256
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER._serialized_end=3195
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX._serialized_start=2560
  _QUESTIONNAIRERESPONSE_ITEM_ANSWER_VALUEX._serialized_end=3195
# @@protoc_insertion_point(module_scope)
