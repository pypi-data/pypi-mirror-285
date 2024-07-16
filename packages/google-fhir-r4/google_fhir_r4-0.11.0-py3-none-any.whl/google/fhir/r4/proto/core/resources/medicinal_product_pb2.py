# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/medicinal_product.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n;google/fhir/r4/proto/core/resources/medicinal_product.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xeb!\n\x10MedicinalProduct\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x32\n\x04type\x18\x0b \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12+\n\x06\x64omain\x18\x0c \x01(\x0b\x32\x1b.google.fhir.r4.core.Coding\x12O\n!combined_pharmaceutical_dose_form\x18\r \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x44\n\x16legal_status_of_supply\x18\x0e \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12M\n\x1f\x61\x64\x64itional_monitoring_indicator\x18\x0f \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x35\n\x10special_measures\x18\x10 \x03(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x46\n\x18paediatric_use_indicator\x18\x11 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x44\n\x16product_classification\x18\x12 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12>\n\x10marketing_status\x18\x13 \x03(\x0b\x32$.google.fhir.r4.core.MarketingStatus\x12\x64\n\x16pharmaceutical_product\x18\x14 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB$\xf2\xff\xfc\xc2\x06\x1eMedicinalProductPharmaceutical\x12\x62\n\x1apackaged_medicinal_product\x18\x15 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1e\xf2\xff\xfc\xc2\x06\x18MedicinalProductPackaged\x12R\n\x11\x61ttached_document\x18\x16 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12L\n\x0bmaster_file\x18\x17 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12Y\n\x07\x63ontact\x18\x18 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB(\xf2\xff\xfc\xc2\x06\x0cOrganization\xf2\xff\xfc\xc2\x06\x10PractitionerRole\x12K\n\x0e\x63linical_trial\x18\x19 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x13\xf2\xff\xfc\xc2\x06\rResearchStudy\x12@\n\x04name\x18\x1a \x03(\x0b\x32*.google.fhir.r4.core.MedicinalProduct.NameB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x38\n\x0f\x63ross_reference\x18\x1b \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12n\n manufacturing_business_operation\x18\x1c \x03(\x0b\x32\x44.google.fhir.r4.core.MedicinalProduct.ManufacturingBusinessOperation\x12U\n\x13special_designation\x18\x1d \x03(\x0b\x32\x38.google.fhir.r4.core.MedicinalProduct.SpecialDesignation\x1a\xe9\x07\n\x04Name\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x39\n\x0cproduct_name\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x46\n\tname_part\x18\x05 \x03(\x0b\x32\x33.google.fhir.r4.core.MedicinalProduct.Name.NamePart\x12T\n\x10\x63ountry_language\x18\x06 \x03(\x0b\x32:.google.fhir.r4.core.MedicinalProduct.Name.CountryLanguage\x1a\x88\x02\n\x08NamePart\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x31\n\x04part\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x31\n\x04type\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.CodingB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xe4\x02\n\x0f\x43ountryLanguage\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12=\n\x07\x63ountry\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12:\n\x0cjurisdiction\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12>\n\x08language\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xd0\x04\n\x1eManufacturingBusinessOperation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12<\n\x0eoperation_type\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12G\n\x1e\x61uthorisation_reference_number\x18\x05 \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x35\n\x0e\x65\x66\x66\x65\x63tive_date\x18\x06 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12G\n\x19\x63onfidentiality_indicator\x18\x07 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12H\n\x0cmanufacturer\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x12\x45\n\tregulator\x18\t \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x1a\x80\x06\n\x12SpecialDesignation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\x04 \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x32\n\x04type\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12:\n\x0cintended_use\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12X\n\nindication\x18\x07 \x01(\x0b\x32\x44.google.fhir.r4.core.MedicinalProduct.SpecialDesignation.IndicationX\x12\x34\n\x06status\x18\x08 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12+\n\x04\x64\x61te\x18\t \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12\x35\n\x07species\x18\n \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x1a\xb8\x01\n\x0bIndicationX\x12@\n\x10\x63odeable_concept\x18\x01 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00\x12U\n\treference\x18\x02 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB \xf2\xff\xfc\xc2\x06\x1aMedicinalProductIndicationH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:D\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x38http://hl7.org/fhir/StructureDefinition/MedicinalProductJ\x04\x08\x07\x10\x08\x42{\n\x17\x63om.google.fhir.r4.coreP\x01ZXgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.medicinal_product_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZXgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_go_proto\230\306\260\265\007\004'
  _MEDICINALPRODUCT_NAME_NAMEPART.fields_by_name['part']._options = None
  _MEDICINALPRODUCT_NAME_NAMEPART.fields_by_name['part']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT_NAME_NAMEPART.fields_by_name['type']._options = None
  _MEDICINALPRODUCT_NAME_NAMEPART.fields_by_name['type']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE.fields_by_name['country']._options = None
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE.fields_by_name['country']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE.fields_by_name['language']._options = None
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE.fields_by_name['language']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT_NAME.fields_by_name['product_name']._options = None
  _MEDICINALPRODUCT_NAME.fields_by_name['product_name']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION.fields_by_name['manufacturer']._options = None
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION.fields_by_name['manufacturer']._serialized_options = b'\362\377\374\302\006\014Organization'
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION.fields_by_name['regulator']._options = None
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION.fields_by_name['regulator']._serialized_options = b'\362\377\374\302\006\014Organization'
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX.fields_by_name['reference']._options = None
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\032MedicinalProductIndication'
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX._options = None
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX._serialized_options = b'\240\203\203\350\006\001'
  _MEDICINALPRODUCT.fields_by_name['pharmaceutical_product']._options = None
  _MEDICINALPRODUCT.fields_by_name['pharmaceutical_product']._serialized_options = b'\362\377\374\302\006\036MedicinalProductPharmaceutical'
  _MEDICINALPRODUCT.fields_by_name['packaged_medicinal_product']._options = None
  _MEDICINALPRODUCT.fields_by_name['packaged_medicinal_product']._serialized_options = b'\362\377\374\302\006\030MedicinalProductPackaged'
  _MEDICINALPRODUCT.fields_by_name['attached_document']._options = None
  _MEDICINALPRODUCT.fields_by_name['attached_document']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _MEDICINALPRODUCT.fields_by_name['master_file']._options = None
  _MEDICINALPRODUCT.fields_by_name['master_file']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _MEDICINALPRODUCT.fields_by_name['contact']._options = None
  _MEDICINALPRODUCT.fields_by_name['contact']._serialized_options = b'\362\377\374\302\006\014Organization\362\377\374\302\006\020PractitionerRole'
  _MEDICINALPRODUCT.fields_by_name['clinical_trial']._options = None
  _MEDICINALPRODUCT.fields_by_name['clinical_trial']._serialized_options = b'\362\377\374\302\006\rResearchStudy'
  _MEDICINALPRODUCT.fields_by_name['name']._options = None
  _MEDICINALPRODUCT.fields_by_name['name']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCT._options = None
  _MEDICINALPRODUCT._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0068http://hl7.org/fhir/StructureDefinition/MedicinalProduct'
  _MEDICINALPRODUCT._serialized_start=197
  _MEDICINALPRODUCT._serialized_end=4528
  _MEDICINALPRODUCT_NAME._serialized_start=2085
  _MEDICINALPRODUCT_NAME._serialized_end=3086
  _MEDICINALPRODUCT_NAME_NAMEPART._serialized_start=2463
  _MEDICINALPRODUCT_NAME_NAMEPART._serialized_end=2727
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE._serialized_start=2730
  _MEDICINALPRODUCT_NAME_COUNTRYLANGUAGE._serialized_end=3086
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION._serialized_start=3089
  _MEDICINALPRODUCT_MANUFACTURINGBUSINESSOPERATION._serialized_end=3681
  _MEDICINALPRODUCT_SPECIALDESIGNATION._serialized_start=3684
  _MEDICINALPRODUCT_SPECIALDESIGNATION._serialized_end=4452
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX._serialized_start=4268
  _MEDICINALPRODUCT_SPECIALDESIGNATION_INDICATIONX._serialized_end=4452
# @@protoc_insertion_point(module_scope)
