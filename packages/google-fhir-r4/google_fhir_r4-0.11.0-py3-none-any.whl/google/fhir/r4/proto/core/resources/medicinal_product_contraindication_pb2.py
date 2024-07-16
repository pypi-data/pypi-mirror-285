# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/medicinal_product_contraindication.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nLgoogle/fhir/r4/proto/core/resources/medicinal_product_contraindication.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xbf\x0c\n MedicinalProductContraindication\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12W\n\x07subject\x18\n \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB&\xf2\xff\xfc\xc2\x06\x10MedicinalProduct\xf2\xff\xfc\xc2\x06\nMedication\x12\x35\n\x07\x64isease\x18\x0b \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12<\n\x0e\x64isease_status\x18\x0c \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x39\n\x0b\x63omorbidity\x18\r \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12`\n\x16therapeutic_indication\x18\x0e \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB \xf2\xff\xfc\xc2\x06\x1aMedicinalProductIndication\x12Y\n\rother_therapy\x18\x0f \x03(\x0b\x32\x42.google.fhir.r4.core.MedicinalProductContraindication.OtherTherapy\x12\x33\n\npopulation\x18\x10 \x03(\x0b\x32\x1f.google.fhir.r4.core.Population\x1a\xd0\x04\n\x0cOtherTherapy\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12O\n\x19therapy_relationship_type\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12j\n\nmedication\x18\x05 \x01(\x0b\x32N.google.fhir.r4.core.MedicinalProductContraindication.OtherTherapy.MedicationXB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xea\x01\n\x0bMedicationX\x12@\n\x10\x63odeable_concept\x18\x01 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00\x12\x86\x01\n\treference\x18\x02 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceBQ\xf2\xff\xfc\xc2\x06\x10MedicinalProduct\xf2\xff\xfc\xc2\x06\nMedication\xf2\xff\xfc\xc2\x06\tSubstance\xf2\xff\xfc\xc2\x06\x16SubstanceSpecificationH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:T\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06Hhttp://hl7.org/fhir/StructureDefinition/MedicinalProductContraindicationJ\x04\x08\x07\x10\x08\x42\x8c\x01\n\x17\x63om.google.fhir.r4.coreP\x01Zigithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_contraindication_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.medicinal_product_contraindication_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Zigithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_contraindication_go_proto\230\306\260\265\007\004'
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX.fields_by_name['reference']._options = None
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\020MedicinalProduct\362\377\374\302\006\nMedication\362\377\374\302\006\tSubstance\362\377\374\302\006\026SubstanceSpecification'
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX._options = None
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX._serialized_options = b'\240\203\203\350\006\001'
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY.fields_by_name['therapy_relationship_type']._options = None
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY.fields_by_name['therapy_relationship_type']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY.fields_by_name['medication']._options = None
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY.fields_by_name['medication']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTCONTRAINDICATION.fields_by_name['subject']._options = None
  _MEDICINALPRODUCTCONTRAINDICATION.fields_by_name['subject']._serialized_options = b'\362\377\374\302\006\020MedicinalProduct\362\377\374\302\006\nMedication'
  _MEDICINALPRODUCTCONTRAINDICATION.fields_by_name['therapeutic_indication']._options = None
  _MEDICINALPRODUCTCONTRAINDICATION.fields_by_name['therapeutic_indication']._serialized_options = b'\362\377\374\302\006\032MedicinalProductIndication'
  _MEDICINALPRODUCTCONTRAINDICATION._options = None
  _MEDICINALPRODUCTCONTRAINDICATION._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006Hhttp://hl7.org/fhir/StructureDefinition/MedicinalProductContraindication'
  _MEDICINALPRODUCTCONTRAINDICATION._serialized_start=214
  _MEDICINALPRODUCTCONTRAINDICATION._serialized_end=1813
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY._serialized_start=1129
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY._serialized_end=1721
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX._serialized_start=1487
  _MEDICINALPRODUCTCONTRAINDICATION_OTHERTHERAPY_MEDICATIONX._serialized_end=1721
# @@protoc_insertion_point(module_scope)
