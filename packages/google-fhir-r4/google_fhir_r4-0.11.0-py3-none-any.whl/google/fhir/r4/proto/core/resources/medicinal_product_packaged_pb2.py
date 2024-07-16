# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/medicinal_product_packaged.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nDgoogle/fhir/r4/proto/core/resources/medicinal_product_packaged.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\x86\x13\n\x18MedicinalProductPackaged\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12G\n\x07subject\x18\x0b \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x16\xf2\xff\xfc\xc2\x06\x10MedicinalProduct\x12\x30\n\x0b\x64\x65scription\x18\x0c \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x44\n\x16legal_status_of_supply\x18\r \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12>\n\x10marketing_status\x18\x0e \x03(\x0b\x32$.google.fhir.r4.core.MarketingStatus\x12\x64\n\x17marketing_authorization\x18\x0f \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB#\xf2\xff\xfc\xc2\x06\x1dMedicinalProductAuthorization\x12H\n\x0cmanufacturer\x18\x10 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization\x12W\n\x10\x62\x61tch_identifier\x18\x11 \x03(\x0b\x32=.google.fhir.r4.core.MedicinalProductPackaged.BatchIdentifier\x12W\n\x0cpackage_item\x18\x12 \x03(\x0b\x32\x39.google.fhir.r4.core.MedicinalProductPackaged.PackageItemB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xa9\x02\n\x0f\x42\x61tchIdentifier\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12@\n\x0fouter_packaging\x18\x04 \x01(\x0b\x32\x1f.google.fhir.r4.core.IdentifierB\x06\xf0\xd0\x87\xeb\x04\x01\x12<\n\x13immediate_packaging\x18\x05 \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x1a\xde\x07\n\x0bPackageItem\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\x04 \x03(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12:\n\x04type\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x37\n\x08quantity\x18\x06 \x01(\x0b\x32\x1d.google.fhir.r4.core.QuantityB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x36\n\x08material\x18\x07 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12@\n\x12\x61lternate_material\x18\x08 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x46\n\x06\x64\x65vice\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x16\xf2\xff\xfc\xc2\x06\x10\x44\x65viceDefinition\x12]\n\x11manufactured_item\x18\n \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\"\xf2\xff\xfc\xc2\x06\x1cMedicinalProductManufactured\x12O\n\x0cpackage_item\x18\x0b \x03(\x0b\x32\x39.google.fhir.r4.core.MedicinalProductPackaged.PackageItem\x12I\n\x18physical_characteristics\x18\x0c \x01(\x0b\x32\'.google.fhir.r4.core.ProdCharacteristic\x12\x43\n\x15other_characteristics\x18\r \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x41\n\x12shelf_life_storage\x18\x0e \x03(\x0b\x32%.google.fhir.r4.core.ProductShelfLife\x12H\n\x0cmanufacturer\x18\x0f \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x12\xf2\xff\xfc\xc2\x06\x0cOrganization:L\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06@http://hl7.org/fhir/StructureDefinition/MedicinalProductPackagedJ\x04\x08\x07\x10\x08\x42\x84\x01\n\x17\x63om.google.fhir.r4.coreP\x01Zagithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_packaged_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.medicinal_product_packaged_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Zagithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/medicinal_product_packaged_go_proto\230\306\260\265\007\004'
  _MEDICINALPRODUCTPACKAGED_BATCHIDENTIFIER.fields_by_name['outer_packaging']._options = None
  _MEDICINALPRODUCTPACKAGED_BATCHIDENTIFIER.fields_by_name['outer_packaging']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['type']._options = None
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['type']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['quantity']._options = None
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['quantity']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['device']._options = None
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['device']._serialized_options = b'\362\377\374\302\006\020DeviceDefinition'
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['manufactured_item']._options = None
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['manufactured_item']._serialized_options = b'\362\377\374\302\006\034MedicinalProductManufactured'
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['manufacturer']._options = None
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM.fields_by_name['manufacturer']._serialized_options = b'\362\377\374\302\006\014Organization'
  _MEDICINALPRODUCTPACKAGED.fields_by_name['subject']._options = None
  _MEDICINALPRODUCTPACKAGED.fields_by_name['subject']._serialized_options = b'\362\377\374\302\006\020MedicinalProduct'
  _MEDICINALPRODUCTPACKAGED.fields_by_name['marketing_authorization']._options = None
  _MEDICINALPRODUCTPACKAGED.fields_by_name['marketing_authorization']._serialized_options = b'\362\377\374\302\006\035MedicinalProductAuthorization'
  _MEDICINALPRODUCTPACKAGED.fields_by_name['manufacturer']._options = None
  _MEDICINALPRODUCTPACKAGED.fields_by_name['manufacturer']._serialized_options = b'\362\377\374\302\006\014Organization'
  _MEDICINALPRODUCTPACKAGED.fields_by_name['package_item']._options = None
  _MEDICINALPRODUCTPACKAGED.fields_by_name['package_item']._serialized_options = b'\360\320\207\353\004\001'
  _MEDICINALPRODUCTPACKAGED._options = None
  _MEDICINALPRODUCTPACKAGED._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006@http://hl7.org/fhir/StructureDefinition/MedicinalProductPackaged'
  _MEDICINALPRODUCTPACKAGED._serialized_start=206
  _MEDICINALPRODUCTPACKAGED._serialized_end=2644
  _MEDICINALPRODUCTPACKAGED_BATCHIDENTIFIER._serialized_start=1270
  _MEDICINALPRODUCTPACKAGED_BATCHIDENTIFIER._serialized_end=1567
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM._serialized_start=1570
  _MEDICINALPRODUCTPACKAGED_PACKAGEITEM._serialized_end=2560
# @@protoc_insertion_point(module_scope)
