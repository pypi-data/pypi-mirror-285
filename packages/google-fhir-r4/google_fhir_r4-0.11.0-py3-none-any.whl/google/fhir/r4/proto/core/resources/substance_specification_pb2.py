# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/substance_specification.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nAgoogle/fhir/r4/proto/core/resources/substance_specification.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\"\xeb=\n\x16SubstanceSpecification\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\n \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x32\n\x04type\x18\x0b \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06status\x18\x0c \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06\x64omain\x18\r \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x30\n\x0b\x64\x65scription\x18\x0e \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12G\n\x06source\x18\x0f \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12,\n\x07\x63omment\x18\x10 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x42\n\x06moiety\x18\x11 \x03(\x0b\x32\x32.google.fhir.r4.core.SubstanceSpecification.Moiety\x12\x46\n\x08property\x18\x12 \x03(\x0b\x32\x34.google.fhir.r4.core.SubstanceSpecification.Property\x12\x62\n\x15reference_information\x18\x13 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB#\xf2\xff\xfc\xc2\x06\x1dSubstanceReferenceInformation\x12H\n\tstructure\x18\x14 \x01(\x0b\x32\x35.google.fhir.r4.core.SubstanceSpecification.Structure\x12\x42\n\x04\x63ode\x18\x15 \x03(\x0b\x32\x34.google.fhir.r4.core.SubstanceSpecification.CodeType\x12>\n\x04name\x18\x16 \x03(\x0b\x32\x30.google.fhir.r4.core.SubstanceSpecification.Name\x12g\n\x10molecular_weight\x18\x17 \x03(\x0b\x32M.google.fhir.r4.core.SubstanceSpecification.Structure.Isotope.MolecularWeight\x12N\n\x0crelationship\x18\x18 \x03(\x0b\x32\x38.google.fhir.r4.core.SubstanceSpecification.Relationship\x12P\n\x0cnucleic_acid\x18\x19 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1a\xf2\xff\xfc\xc2\x06\x14SubstanceNucleicAcid\x12G\n\x07polymer\x18\x1a \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x16\xf2\xff\xfc\xc2\x06\x10SubstancePolymer\x12G\n\x07protein\x18\x1b \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x16\xf2\xff\xfc\xc2\x06\x10SubstanceProtein\x12V\n\x0fsource_material\x18\x1c \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1d\xf2\xff\xfc\xc2\x06\x17SubstanceSourceMaterial\x1a\xc5\x05\n\x06Moiety\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x32\n\x04role\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x33\n\nidentifier\x18\x05 \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12)\n\x04name\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12=\n\x0fstereochemistry\x18\x07 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12>\n\x10optical_activity\x18\x08 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x36\n\x11molecular_formula\x18\t \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12J\n\x06\x61mount\x18\n \x01(\x0b\x32:.google.fhir.r4.core.SubstanceSpecification.Moiety.AmountX\x1a\x8b\x01\n\x07\x41mountX\x12\x31\n\x08quantity\x18\x01 \x01(\x0b\x32\x1d.google.fhir.r4.core.QuantityH\x00\x12;\n\x0cstring_value\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xcd\x06\n\x08Property\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x36\n\x08\x63\x61tegory\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x04\x63ode\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12/\n\nparameters\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x63\n\x12\x64\x65\x66ining_substance\x18\x07 \x01(\x0b\x32G.google.fhir.r4.core.SubstanceSpecification.Property.DefiningSubstanceX\x12L\n\x06\x61mount\x18\x08 \x01(\x0b\x32<.google.fhir.r4.core.SubstanceSpecification.Property.AmountX\x1a\xca\x01\n\x12\x44\x65\x66iningSubstanceX\x12`\n\treference\x18\x01 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB+\xf2\xff\xfc\xc2\x06\x16SubstanceSpecification\xf2\xff\xfc\xc2\x06\tSubstanceH\x00\x12@\n\x10\x63odeable_concept\x18\x02 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\x8b\x01\n\x07\x41mountX\x12\x31\n\x08quantity\x18\x01 \x01(\x0b\x32\x1d.google.fhir.r4.core.QuantityH\x00\x12;\n\x0cstring_value\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xee\x0e\n\tStructure\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12=\n\x0fstereochemistry\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12>\n\x10optical_activity\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x36\n\x11molecular_formula\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12@\n\x1bmolecular_formula_by_moiety\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12N\n\x07isotope\x18\x08 \x03(\x0b\x32=.google.fhir.r4.core.SubstanceSpecification.Structure.Isotope\x12g\n\x10molecular_weight\x18\t \x01(\x0b\x32M.google.fhir.r4.core.SubstanceSpecification.Structure.Isotope.MolecularWeight\x12G\n\x06source\x18\n \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x12\\\n\x0erepresentation\x18\x0b \x03(\x0b\x32\x44.google.fhir.r4.core.SubstanceSpecification.Structure.Representation\x1a\xa6\x06\n\x07Isotope\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\nidentifier\x18\x04 \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12\x32\n\x04name\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12:\n\x0csubstitution\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x30\n\thalf_life\x18\x07 \x01(\x0b\x32\x1d.google.fhir.r4.core.Quantity\x12g\n\x10molecular_weight\x18\x08 \x01(\x0b\x32M.google.fhir.r4.core.SubstanceSpecification.Structure.Isotope.MolecularWeight\x1a\xc2\x02\n\x0fMolecularWeight\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x34\n\x06method\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x04type\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12-\n\x06\x61mount\x18\x06 \x01(\x0b\x32\x1d.google.fhir.r4.core.Quantity\x1a\xc6\x02\n\x0eRepresentation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x32\n\x04type\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x33\n\x0erepresentation\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x33\n\nattachment\x18\x06 \x01(\x0b\x32\x1f.google.fhir.r4.core.Attachment\x1a\xb7\x03\n\x08\x43odeType\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x32\n\x04\x63ode\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06status\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x32\n\x0bstatus_date\x18\x06 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12,\n\x07\x63omment\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12G\n\x06source\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x1a\xf7\x08\n\x04Name\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x31\n\x04name\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x32\n\x04type\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06status\x18\x06 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12/\n\tpreferred\x18\x07 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12\x36\n\x08language\x18\x08 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06\x64omain\x18\t \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12:\n\x0cjurisdiction\x18\n \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x41\n\x07synonym\x18\x0b \x03(\x0b\x32\x30.google.fhir.r4.core.SubstanceSpecification.Name\x12\x45\n\x0btranslation\x18\x0c \x03(\x0b\x32\x30.google.fhir.r4.core.SubstanceSpecification.Name\x12K\n\x08official\x18\r \x03(\x0b\x32\x39.google.fhir.r4.core.SubstanceSpecification.Name.Official\x12G\n\x06source\x18\x0e \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x1a\xbe\x02\n\x08Official\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x37\n\tauthority\x18\x04 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x34\n\x06status\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12+\n\x04\x64\x61te\x18\x06 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x1a\x9d\x08\n\x0cRelationship\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12V\n\tsubstance\x18\x04 \x01(\x0b\x32\x43.google.fhir.r4.core.SubstanceSpecification.Relationship.SubstanceX\x12:\n\x0crelationship\x18\x05 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12\x31\n\x0bis_defining\x18\x06 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12P\n\x06\x61mount\x18\x07 \x01(\x0b\x32@.google.fhir.r4.core.SubstanceSpecification.Relationship.AmountX\x12:\n\x16\x61mount_ratio_low_limit\x18\x08 \x01(\x0b\x32\x1a.google.fhir.r4.core.Ratio\x12\x39\n\x0b\x61mount_type\x18\t \x01(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12G\n\x06source\x18\n \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x17\xf2\xff\xfc\xc2\x06\x11\x44ocumentReference\x1a\xb3\x01\n\nSubstanceX\x12Q\n\treference\x18\x01 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x1c\xf2\xff\xfc\xc2\x06\x16SubstanceSpecificationH\x00\x12@\n\x10\x63odeable_concept\x18\x02 \x01(\x0b\x32$.google.fhir.r4.core.CodeableConceptH\x00:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice\x1a\xe5\x01\n\x07\x41mountX\x12\x31\n\x08quantity\x18\x01 \x01(\x0b\x32\x1d.google.fhir.r4.core.QuantityH\x00\x12+\n\x05range\x18\x02 \x01(\x0b\x32\x1a.google.fhir.r4.core.RangeH\x00\x12+\n\x05ratio\x18\x03 \x01(\x0b\x32\x1a.google.fhir.r4.core.RatioH\x00\x12;\n\x0cstring_value\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringH\x00R\x06string:\x06\xa0\x83\x83\xe8\x06\x01\x42\x08\n\x06\x63hoice:J\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06>http://hl7.org/fhir/StructureDefinition/SubstanceSpecificationJ\x04\x08\x07\x10\x08\x42\x81\x01\n\x17\x63om.google.fhir.r4.coreP\x01Z^github.com/google/fhir/go/google/fhir/r4/proto/core/resources/substance_specification_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.substance_specification_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001Z^github.com/google/fhir/go/google/fhir/r4/proto/core/resources/substance_specification_go_proto\230\306\260\265\007\004'
  _SUBSTANCESPECIFICATION_MOIETY_AMOUNTX._options = None
  _SUBSTANCESPECIFICATION_MOIETY_AMOUNTX._serialized_options = b'\240\203\203\350\006\001'
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX.fields_by_name['reference']._options = None
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\026SubstanceSpecification\362\377\374\302\006\tSubstance'
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX._options = None
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX._serialized_options = b'\240\203\203\350\006\001'
  _SUBSTANCESPECIFICATION_PROPERTY_AMOUNTX._options = None
  _SUBSTANCESPECIFICATION_PROPERTY_AMOUNTX._serialized_options = b'\240\203\203\350\006\001'
  _SUBSTANCESPECIFICATION_STRUCTURE.fields_by_name['source']._options = None
  _SUBSTANCESPECIFICATION_STRUCTURE.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _SUBSTANCESPECIFICATION_CODETYPE.fields_by_name['source']._options = None
  _SUBSTANCESPECIFICATION_CODETYPE.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _SUBSTANCESPECIFICATION_NAME.fields_by_name['name']._options = None
  _SUBSTANCESPECIFICATION_NAME.fields_by_name['name']._serialized_options = b'\360\320\207\353\004\001'
  _SUBSTANCESPECIFICATION_NAME.fields_by_name['source']._options = None
  _SUBSTANCESPECIFICATION_NAME.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX.fields_by_name['reference']._options = None
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX.fields_by_name['reference']._serialized_options = b'\362\377\374\302\006\026SubstanceSpecification'
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX._options = None
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX._serialized_options = b'\240\203\203\350\006\001'
  _SUBSTANCESPECIFICATION_RELATIONSHIP_AMOUNTX._options = None
  _SUBSTANCESPECIFICATION_RELATIONSHIP_AMOUNTX._serialized_options = b'\240\203\203\350\006\001'
  _SUBSTANCESPECIFICATION_RELATIONSHIP.fields_by_name['source']._options = None
  _SUBSTANCESPECIFICATION_RELATIONSHIP.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _SUBSTANCESPECIFICATION.fields_by_name['source']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['source']._serialized_options = b'\362\377\374\302\006\021DocumentReference'
  _SUBSTANCESPECIFICATION.fields_by_name['reference_information']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['reference_information']._serialized_options = b'\362\377\374\302\006\035SubstanceReferenceInformation'
  _SUBSTANCESPECIFICATION.fields_by_name['nucleic_acid']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['nucleic_acid']._serialized_options = b'\362\377\374\302\006\024SubstanceNucleicAcid'
  _SUBSTANCESPECIFICATION.fields_by_name['polymer']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['polymer']._serialized_options = b'\362\377\374\302\006\020SubstancePolymer'
  _SUBSTANCESPECIFICATION.fields_by_name['protein']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['protein']._serialized_options = b'\362\377\374\302\006\020SubstanceProtein'
  _SUBSTANCESPECIFICATION.fields_by_name['source_material']._options = None
  _SUBSTANCESPECIFICATION.fields_by_name['source_material']._serialized_options = b'\362\377\374\302\006\027SubstanceSourceMaterial'
  _SUBSTANCESPECIFICATION._options = None
  _SUBSTANCESPECIFICATION._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\006>http://hl7.org/fhir/StructureDefinition/SubstanceSpecification'
  _SUBSTANCESPECIFICATION._serialized_start=203
  _SUBSTANCESPECIFICATION._serialized_end=8118
  _SUBSTANCESPECIFICATION_MOIETY._serialized_start=1930
  _SUBSTANCESPECIFICATION_MOIETY._serialized_end=2639
  _SUBSTANCESPECIFICATION_MOIETY_AMOUNTX._serialized_start=2500
  _SUBSTANCESPECIFICATION_MOIETY_AMOUNTX._serialized_end=2639
  _SUBSTANCESPECIFICATION_PROPERTY._serialized_start=2642
  _SUBSTANCESPECIFICATION_PROPERTY._serialized_end=3487
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX._serialized_start=3143
  _SUBSTANCESPECIFICATION_PROPERTY_DEFININGSUBSTANCEX._serialized_end=3345
  _SUBSTANCESPECIFICATION_PROPERTY_AMOUNTX._serialized_start=2500
  _SUBSTANCESPECIFICATION_PROPERTY_AMOUNTX._serialized_end=2639
  _SUBSTANCESPECIFICATION_STRUCTURE._serialized_start=3490
  _SUBSTANCESPECIFICATION_STRUCTURE._serialized_end=5392
  _SUBSTANCESPECIFICATION_STRUCTURE_ISOTOPE._serialized_start=4257
  _SUBSTANCESPECIFICATION_STRUCTURE_ISOTOPE._serialized_end=5063
  _SUBSTANCESPECIFICATION_STRUCTURE_ISOTOPE_MOLECULARWEIGHT._serialized_start=4741
  _SUBSTANCESPECIFICATION_STRUCTURE_ISOTOPE_MOLECULARWEIGHT._serialized_end=5063
  _SUBSTANCESPECIFICATION_STRUCTURE_REPRESENTATION._serialized_start=5066
  _SUBSTANCESPECIFICATION_STRUCTURE_REPRESENTATION._serialized_end=5392
  _SUBSTANCESPECIFICATION_CODETYPE._serialized_start=5395
  _SUBSTANCESPECIFICATION_CODETYPE._serialized_end=5834
  _SUBSTANCESPECIFICATION_NAME._serialized_start=5837
  _SUBSTANCESPECIFICATION_NAME._serialized_end=6980
  _SUBSTANCESPECIFICATION_NAME_OFFICIAL._serialized_start=6662
  _SUBSTANCESPECIFICATION_NAME_OFFICIAL._serialized_end=6980
  _SUBSTANCESPECIFICATION_RELATIONSHIP._serialized_start=6983
  _SUBSTANCESPECIFICATION_RELATIONSHIP._serialized_end=8036
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX._serialized_start=7625
  _SUBSTANCESPECIFICATION_RELATIONSHIP_SUBSTANCEX._serialized_end=7804
  _SUBSTANCESPECIFICATION_RELATIONSHIP_AMOUNTX._serialized_start=7807
  _SUBSTANCESPECIFICATION_RELATIONSHIP_AMOUNTX._serialized_end=8036
# @@protoc_insertion_point(module_scope)
