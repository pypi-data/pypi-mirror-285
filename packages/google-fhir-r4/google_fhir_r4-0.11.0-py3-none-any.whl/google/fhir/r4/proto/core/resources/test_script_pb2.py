# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/fhir/r4/proto/core/resources/test_script.proto
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
from google.fhir.r4.proto.core import valuesets_pb2 as google_dot_fhir_dot_r4_dot_proto_dot_core_dot_valuesets__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n5google/fhir/r4/proto/core/resources/test_script.proto\x12\x13google.fhir.r4.core\x1a\x19google/protobuf/any.proto\x1a(google/fhir/core/proto/annotations.proto\x1a%google/fhir/r4/proto/core/codes.proto\x1a)google/fhir/r4/proto/core/datatypes.proto\x1a)google/fhir/r4/proto/core/valuesets.proto\"\x80l\n\nTestScript\x12#\n\x02id\x18\x01 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\'\n\x04meta\x18\x02 \x01(\x0b\x32\x19.google.fhir.r4.core.Meta\x12\x30\n\x0eimplicit_rules\x18\x03 \x01(\x0b\x32\x18.google.fhir.r4.core.Uri\x12+\n\x08language\x18\x04 \x01(\x0b\x32\x19.google.fhir.r4.core.Code\x12,\n\x04text\x18\x05 \x01(\x0b\x32\x1e.google.fhir.r4.core.Narrative\x12\'\n\tcontained\x18\x06 \x03(\x0b\x32\x14.google.protobuf.Any\x12\x31\n\textension\x18\x08 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\t \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12-\n\x03url\x18\n \x01(\x0b\x32\x18.google.fhir.r4.core.UriB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x33\n\nidentifier\x18\x0b \x01(\x0b\x32\x1f.google.fhir.r4.core.Identifier\x12,\n\x07version\x18\x0c \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\x04name\x18\r \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12*\n\x05title\x18\x0e \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x42\n\x06status\x18\x0f \x01(\x0b\x32*.google.fhir.r4.core.TestScript.StatusCodeB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x32\n\x0c\x65xperimental\x18\x10 \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12+\n\x04\x64\x61te\x18\x11 \x01(\x0b\x32\x1d.google.fhir.r4.core.DateTime\x12.\n\tpublisher\x18\x12 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x33\n\x07\x63ontact\x18\x13 \x03(\x0b\x32\".google.fhir.r4.core.ContactDetail\x12\x32\n\x0b\x64\x65scription\x18\x14 \x01(\x0b\x32\x1d.google.fhir.r4.core.Markdown\x12\x36\n\x0buse_context\x18\x15 \x03(\x0b\x32!.google.fhir.r4.core.UsageContext\x12:\n\x0cjurisdiction\x18\x16 \x03(\x0b\x32$.google.fhir.r4.core.CodeableConcept\x12.\n\x07purpose\x18\x17 \x01(\x0b\x32\x1d.google.fhir.r4.core.Markdown\x12\x30\n\tcopyright\x18\x18 \x01(\x0b\x32\x1d.google.fhir.r4.core.Markdown\x12\x36\n\x06origin\x18\x19 \x03(\x0b\x32&.google.fhir.r4.core.TestScript.Origin\x12@\n\x0b\x64\x65stination\x18\x1a \x03(\x0b\x32+.google.fhir.r4.core.TestScript.Destination\x12:\n\x08metadata\x18\x1b \x01(\x0b\x32(.google.fhir.r4.core.TestScript.Metadata\x12\x38\n\x07\x66ixture\x18\x1c \x03(\x0b\x32\'.google.fhir.r4.core.TestScript.Fixture\x12?\n\x07profile\x18\x1d \x03(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x12:\n\x08variable\x18\x1e \x03(\x0b\x32(.google.fhir.r4.core.TestScript.Variable\x12\x34\n\x05setup\x18\x1f \x01(\x0b\x32%.google.fhir.r4.core.TestScript.Setup\x12\x32\n\x04test\x18  \x03(\x0b\x32$.google.fhir.r4.core.TestScript.Test\x12:\n\x08teardown\x18! \x01(\x0b\x32(.google.fhir.r4.core.TestScript.Teardown\x1a\x98\x02\n\nStatusCode\x12?\n\x05value\x18\x01 \x01(\x0e\x32\x30.google.fhir.r4.core.PublicationStatusCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:m\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05/http://hl7.org/fhir/ValueSet/publication-status\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x8b\x02\n\x06Origin\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\x05index\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.IntegerB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x34\n\x07profile\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.CodingB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x90\x02\n\x0b\x44\x65stination\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x33\n\x05index\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.IntegerB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x34\n\x07profile\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.CodingB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x88\t\n\x08Metadata\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12;\n\x04link\x18\x04 \x03(\x0b\x32-.google.fhir.r4.core.TestScript.Metadata.Link\x12O\n\ncapability\x18\x05 \x03(\x0b\x32\x33.google.fhir.r4.core.TestScript.Metadata.CapabilityB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xff\x01\n\x04Link\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12-\n\x03url\x18\x04 \x01(\x0b\x32\x18.google.fhir.r4.core.UriB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x30\n\x0b\x64\x65scription\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x1a\x8e\x04\n\nCapability\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x36\n\x08required\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x37\n\tvalidated\x18\x05 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x30\n\x0b\x64\x65scription\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12,\n\x06origin\x18\x07 \x03(\x0b\x32\x1c.google.fhir.r4.core.Integer\x12\x31\n\x0b\x64\x65stination\x18\x08 \x01(\x0b\x32\x1c.google.fhir.r4.core.Integer\x12&\n\x04link\x18\t \x03(\x0b\x32\x18.google.fhir.r4.core.Uri\x12<\n\x0c\x63\x61pabilities\x18\n \x01(\x0b\x32\x1e.google.fhir.r4.core.CanonicalB\x06\xf0\xd0\x87\xeb\x04\x01:C\x9a\x86\x93\xa0\x08=capability.required.exists() or capability.validated.exists()\x1a\xd7\x02\n\x07\x46ixture\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x38\n\nautocreate\x18\x04 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x38\n\nautodelete\x18\x05 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x12@\n\x08resource\x18\x06 \x01(\x0b\x32\x1e.google.fhir.r4.core.ReferenceB\x0e\xf2\xff\xfc\xc2\x06\x08Resource\x1a\xe2\x04\n\x08Variable\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x31\n\x04name\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x32\n\rdefault_value\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x30\n\x0b\x64\x65scription\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12/\n\nexpression\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\x0cheader_field\x18\x08 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12)\n\x04hint\x18\t \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12)\n\x04path\x18\n \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12*\n\tsource_id\x18\x0b \x01(\x0b\x32\x17.google.fhir.r4.core.Id:?\x9a\x86\x93\xa0\x08\x39\x65xpression.empty() or headerField.empty() or path.empty()\x1a\xfc\x36\n\x05Setup\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12I\n\x06\x61\x63tion\x18\x04 \x03(\x0b\x32\x31.google.fhir.r4.core.TestScript.Setup.SetupActionB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x8f\x35\n\x0bSetupAction\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12N\n\toperation\x18\x04 \x01(\x0b\x32;.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation\x12V\n\x0c\x61ssert_value\x18\x05 \x01(\x0b\x32\x38.google.fhir.r4.core.TestScript.Setup.SetupAction.AssertR\x06\x61ssert\x1a\xe3\x14\n\tOperation\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12)\n\x04type\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.Coding\x12Z\n\x08resource\x18\x05 \x01(\x0b\x32H.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation.ResourceCode\x12*\n\x05label\x18\x06 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x30\n\x0b\x64\x65scription\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12V\n\x06\x61\x63\x63\x65pt\x18\x08 \x01(\x0b\x32\x46.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation.AcceptCode\x12\x61\n\x0c\x63ontent_type\x18\t \x01(\x0b\x32K.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation.ContentTypeCode\x12\x31\n\x0b\x64\x65stination\x18\n \x01(\x0b\x32\x1c.google.fhir.r4.core.Integer\x12@\n\x12\x65ncode_request_url\x18\x0b \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x12V\n\x06method\x18\x0c \x01(\x0b\x32\x46.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation.MethodCode\x12,\n\x06origin\x18\r \x01(\x0b\x32\x1c.google.fhir.r4.core.Integer\x12+\n\x06params\x18\x0e \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x61\n\x0erequest_header\x18\x0f \x03(\x0b\x32I.google.fhir.r4.core.TestScript.Setup.SetupAction.Operation.RequestHeader\x12+\n\nrequest_id\x18\x10 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12,\n\x0bresponse_id\x18\x11 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12*\n\tsource_id\x18\x12 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12*\n\ttarget_id\x18\x13 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12(\n\x03url\x18\x14 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x1a\x97\x02\n\x0cResourceCode\x12\x41\n\x05value\x18\x01 \x01(\x0e\x32\x32.google.fhir.r4.core.FHIRDefinedTypeValueSet.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:h\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05*http://hl7.org/fhir/ValueSet/defined-types\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xe3\x01\n\nAcceptCode\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\r\n\x05value\x18\x04 \x01(\t:d\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05&http://hl7.org/fhir/ValueSet/mimetypes\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/codeJ\x04\x08\x01\x10\x02\x1a\xe8\x01\n\x0f\x43ontentTypeCode\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\r\n\x05value\x18\x04 \x01(\t:d\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05&http://hl7.org/fhir/ValueSet/mimetypes\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/codeJ\x04\x08\x01\x10\x02\x1a\x9b\x02\n\nMethodCode\x12\x45\n\x05value\x18\x01 \x01(\x0e\x32\x36.google.fhir.r4.core.TestScriptRequestMethodCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:j\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05,http://hl7.org/fhir/ValueSet/http-operations\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x8f\x02\n\rRequestHeader\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\x32\n\x05\x66ield\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01\x12\x32\n\x05value\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringB\x06\xf0\xd0\x87\xeb\x04\x01:\x9a\x01\x9a\x86\x93\xa0\x08\x93\x01sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' |\'search\' | \'transaction\' | \'history\'))\x1a\xab\x1d\n\x06\x41ssert\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12*\n\x05label\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x30\n\x0b\x64\x65scription\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12Y\n\tdirection\x18\x06 \x01(\x0b\x32\x46.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.DirectionCode\x12\x39\n\x14\x63ompare_to_source_id\x18\x07 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x41\n\x1c\x63ompare_to_source_expression\x18\x08 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12;\n\x16\x63ompare_to_source_path\x18\t \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12^\n\x0c\x63ontent_type\x18\n \x01(\x0b\x32H.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.ContentTypeCode\x12/\n\nexpression\x18\x0b \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\x0cheader_field\x18\x0c \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12/\n\nminimum_id\x18\r \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x36\n\x10navigation_links\x18\x0e \x01(\x0b\x32\x1c.google.fhir.r4.core.Boolean\x12W\n\x08operator\x18\x0f \x01(\x0b\x32\x45.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.OperatorCode\x12)\n\x04path\x18\x10 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x62\n\x0erequest_method\x18\x11 \x01(\x0b\x32J.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.RequestMethodCode\x12<\n\x0brequest_url\x18\x12 \x01(\x0b\x32\x1b.google.fhir.r4.core.StringR\nrequestURL\x12W\n\x08resource\x18\x13 \x01(\x0b\x32\x45.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.ResourceCode\x12W\n\x08response\x18\x14 \x01(\x0b\x32\x45.google.fhir.r4.core.TestScript.Setup.SetupAction.Assert.ResponseCode\x12\x32\n\rresponse_code\x18\x15 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12*\n\tsource_id\x18\x16 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12\x34\n\x13validate_profile_id\x18\x17 \x01(\x0b\x32\x17.google.fhir.r4.core.Id\x12*\n\x05value\x18\x18 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12:\n\x0cwarning_only\x18\x19 \x01(\x0b\x32\x1c.google.fhir.r4.core.BooleanB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\xa4\x02\n\rDirectionCode\x12\x44\n\x05value\x18\x01 \x01(\x0e\x32\x35.google.fhir.r4.core.AssertionDirectionTypeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:q\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x33http://hl7.org/fhir/ValueSet/assert-direction-codes\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xe8\x01\n\x0f\x43ontentTypeCode\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\r\n\x05value\x18\x04 \x01(\t:d\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05&http://hl7.org/fhir/ValueSet/mimetypes\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/codeJ\x04\x08\x01\x10\x02\x1a\xa1\x02\n\x0cOperatorCode\x12\x43\n\x05value\x18\x01 \x01(\x0e\x32\x34.google.fhir.r4.core.AssertionOperatorTypeCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:p\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x32http://hl7.org/fhir/ValueSet/assert-operator-codes\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xa2\x02\n\x11RequestMethodCode\x12\x45\n\x05value\x18\x01 \x01(\x0e\x32\x36.google.fhir.r4.core.TestScriptRequestMethodCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:j\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05,http://hl7.org/fhir/ValueSet/http-operations\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\x97\x02\n\x0cResourceCode\x12\x41\n\x05value\x18\x01 \x01(\x0e\x32\x32.google.fhir.r4.core.FHIRDefinedTypeValueSet.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:h\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05*http://hl7.org/fhir/ValueSet/defined-types\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code\x1a\xa7\x02\n\x0cResponseCode\x12\x44\n\x05value\x18\x01 \x01(\x0e\x32\x35.google.fhir.r4.core.AssertionResponseTypesCode.Value\x12\'\n\x02id\x18\x02 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension:u\xc0\x9f\xe3\xb6\x05\x01\x8a\xf9\x83\xb2\x05\x37http://hl7.org/fhir/ValueSet/assert-response-code-types\x9a\xb5\x8e\x93\x06,http://hl7.org/fhir/StructureDefinition/code:\xf2\x03\x9a\x86\x93\xa0\x08\x89\x02\x65xtension.exists() or (contentType.count() + expression.count() + headerField.count() + minimumId.count() + navigationLinks.count() + path.count() + requestMethod.count() + resource.count() + responseCode.count() + response.count()  + validateProfileId.count() <=1)\x9a\x86\x93\xa0\x08\x62\x63ompareToSourceId.empty() xor (compareToSourceExpression.exists() or compareToSourcePath.exists())\x9a\x86\x93\xa0\x08t(response.empty() and responseCode.empty() and direction = \'request\') or direction.empty() or direction = \'response\':,\x9a\x86\x93\xa0\x08&operation.exists() xor assert.exists()\x1a\xd5\n\n\x04Test\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12)\n\x04name\x18\x04 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x30\n\x0b\x64\x65scription\x18\x05 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12G\n\x06\x61\x63tion\x18\x06 \x03(\x0b\x32/.google.fhir.r4.core.TestScript.Test.TestActionB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x8e\x08\n\nTestAction\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\xec\x01\n\toperation\x18\x04 \x01(\x0b\x32;.google.fhir.r4.core.TestScript.Setup.SetupAction.OperationB\x9b\x01\xf2\xbe\xc0\xa4\x07\x94\x01sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' | \'search\' | \'transaction\' | \'history\'))\x12\xca\x04\n\x0c\x61ssert_value\x18\x05 \x01(\x0b\x32\x38.google.fhir.r4.core.TestScript.Setup.SetupAction.AssertB\xf1\x03\xf2\xbe\xc0\xa4\x07\x88\x02\x65xtension.exists() or (contentType.count() + expression.count() + headerField.count() + minimumId.count() + navigationLinks.count() + path.count() + requestMethod.count() + resource.count() + responseCode.count() + response.count() + validateProfileId.count() <=1)\xf2\xbe\xc0\xa4\x07\x62\x63ompareToSourceId.empty() xor (compareToSourceExpression.exists() or compareToSourcePath.exists())\xf2\xbe\xc0\xa4\x07t(response.empty() and responseCode.empty() and direction = \'request\') or direction.empty() or direction = \'response\'R\x06\x61ssert:,\x9a\x86\x93\xa0\x08&operation.exists() xor assert.exists()\x1a\x93\x05\n\x08Teardown\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12O\n\x06\x61\x63tion\x18\x04 \x03(\x0b\x32\x37.google.fhir.r4.core.TestScript.Teardown.TeardownActionB\x06\xf0\xd0\x87\xeb\x04\x01\x1a\x9d\x03\n\x0eTeardownAction\x12\'\n\x02id\x18\x01 \x01(\x0b\x32\x1b.google.fhir.r4.core.String\x12\x31\n\textension\x18\x02 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12:\n\x12modifier_extension\x18\x03 \x03(\x0b\x32\x1e.google.fhir.r4.core.Extension\x12\xf2\x01\n\toperation\x18\x04 \x01(\x0b\x32;.google.fhir.r4.core.TestScript.Setup.SetupAction.OperationB\xa1\x01\xf0\xd0\x87\xeb\x04\x01\xf2\xbe\xc0\xa4\x07\x94\x01sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' | \'search\' | \'transaction\' | \'history\')):n\xc0\x9f\xe3\xb6\x05\x03\xb2\xfe\xe4\x97\x06\x32http://hl7.org/fhir/StructureDefinition/TestScript\x9a\xaf\xae\xa4\x0b*name.matches(\'[A-Z]([A-Za-z0-9_]){0,254}\')J\x04\x08\x07\x10\x08\x42u\n\x17\x63om.google.fhir.r4.coreP\x01ZRgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/test_script_go_proto\x98\xc6\xb0\xb5\x07\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.fhir.r4.proto.core.resources.test_script_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.google.fhir.r4.coreP\001ZRgithub.com/google/fhir/go/google/fhir/r4/proto/core/resources/test_script_go_proto\230\306\260\265\007\004'
  _TESTSCRIPT_STATUSCODE._options = None
  _TESTSCRIPT_STATUSCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005/http://hl7.org/fhir/ValueSet/publication-status\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_ORIGIN.fields_by_name['index']._options = None
  _TESTSCRIPT_ORIGIN.fields_by_name['index']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_ORIGIN.fields_by_name['profile']._options = None
  _TESTSCRIPT_ORIGIN.fields_by_name['profile']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_DESTINATION.fields_by_name['index']._options = None
  _TESTSCRIPT_DESTINATION.fields_by_name['index']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_DESTINATION.fields_by_name['profile']._options = None
  _TESTSCRIPT_DESTINATION.fields_by_name['profile']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA_LINK.fields_by_name['url']._options = None
  _TESTSCRIPT_METADATA_LINK.fields_by_name['url']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['required']._options = None
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['required']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['validated']._options = None
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['validated']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['capabilities']._options = None
  _TESTSCRIPT_METADATA_CAPABILITY.fields_by_name['capabilities']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA.fields_by_name['capability']._options = None
  _TESTSCRIPT_METADATA.fields_by_name['capability']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_METADATA._options = None
  _TESTSCRIPT_METADATA._serialized_options = b'\232\206\223\240\010=capability.required.exists() or capability.validated.exists()'
  _TESTSCRIPT_FIXTURE.fields_by_name['autocreate']._options = None
  _TESTSCRIPT_FIXTURE.fields_by_name['autocreate']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_FIXTURE.fields_by_name['autodelete']._options = None
  _TESTSCRIPT_FIXTURE.fields_by_name['autodelete']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_FIXTURE.fields_by_name['resource']._options = None
  _TESTSCRIPT_FIXTURE.fields_by_name['resource']._serialized_options = b'\362\377\374\302\006\010Resource'
  _TESTSCRIPT_VARIABLE.fields_by_name['name']._options = None
  _TESTSCRIPT_VARIABLE.fields_by_name['name']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_VARIABLE._options = None
  _TESTSCRIPT_VARIABLE._serialized_options = b'\232\206\223\240\0109expression.empty() or headerField.empty() or path.empty()'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_RESOURCECODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_RESOURCECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005*http://hl7.org/fhir/ValueSet/defined-types\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_ACCEPTCODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_ACCEPTCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005&http://hl7.org/fhir/ValueSet/mimetypes\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_CONTENTTYPECODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_CONTENTTYPECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005&http://hl7.org/fhir/ValueSet/mimetypes\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_METHODCODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_METHODCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005,http://hl7.org/fhir/ValueSet/http-operations\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER.fields_by_name['field']._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER.fields_by_name['field']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER.fields_by_name['value']._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER.fields_by_name['value']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION.fields_by_name['encode_request_url']._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION.fields_by_name['encode_request_url']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION._serialized_options = b'\232\206\223\240\010\223\001sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' |\'search\' | \'transaction\' | \'history\'))'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_DIRECTIONCODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_DIRECTIONCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0053http://hl7.org/fhir/ValueSet/assert-direction-codes\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_CONTENTTYPECODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_CONTENTTYPECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005&http://hl7.org/fhir/ValueSet/mimetypes\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_OPERATORCODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_OPERATORCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0052http://hl7.org/fhir/ValueSet/assert-operator-codes\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_REQUESTMETHODCODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_REQUESTMETHODCODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005,http://hl7.org/fhir/ValueSet/http-operations\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESOURCECODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESOURCECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\005*http://hl7.org/fhir/ValueSet/defined-types\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESPONSECODE._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESPONSECODE._serialized_options = b'\300\237\343\266\005\001\212\371\203\262\0057http://hl7.org/fhir/ValueSet/assert-response-code-types\232\265\216\223\006,http://hl7.org/fhir/StructureDefinition/code'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT.fields_by_name['warning_only']._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT.fields_by_name['warning_only']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT._options = None
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT._serialized_options = b'\232\206\223\240\010\211\002extension.exists() or (contentType.count() + expression.count() + headerField.count() + minimumId.count() + navigationLinks.count() + path.count() + requestMethod.count() + resource.count() + responseCode.count() + response.count()  + validateProfileId.count() <=1)\232\206\223\240\010bcompareToSourceId.empty() xor (compareToSourceExpression.exists() or compareToSourcePath.exists())\232\206\223\240\010t(response.empty() and responseCode.empty() and direction = \'request\') or direction.empty() or direction = \'response\''
  _TESTSCRIPT_SETUP_SETUPACTION._options = None
  _TESTSCRIPT_SETUP_SETUPACTION._serialized_options = b'\232\206\223\240\010&operation.exists() xor assert.exists()'
  _TESTSCRIPT_SETUP.fields_by_name['action']._options = None
  _TESTSCRIPT_SETUP.fields_by_name['action']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_TEST_TESTACTION.fields_by_name['operation']._options = None
  _TESTSCRIPT_TEST_TESTACTION.fields_by_name['operation']._serialized_options = b'\362\276\300\244\007\224\001sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' | \'search\' | \'transaction\' | \'history\'))'
  _TESTSCRIPT_TEST_TESTACTION.fields_by_name['assert_value']._options = None
  _TESTSCRIPT_TEST_TESTACTION.fields_by_name['assert_value']._serialized_options = b'\362\276\300\244\007\210\002extension.exists() or (contentType.count() + expression.count() + headerField.count() + minimumId.count() + navigationLinks.count() + path.count() + requestMethod.count() + resource.count() + responseCode.count() + response.count() + validateProfileId.count() <=1)\362\276\300\244\007bcompareToSourceId.empty() xor (compareToSourceExpression.exists() or compareToSourcePath.exists())\362\276\300\244\007t(response.empty() and responseCode.empty() and direction = \'request\') or direction.empty() or direction = \'response\''
  _TESTSCRIPT_TEST_TESTACTION._options = None
  _TESTSCRIPT_TEST_TESTACTION._serialized_options = b'\232\206\223\240\010&operation.exists() xor assert.exists()'
  _TESTSCRIPT_TEST.fields_by_name['action']._options = None
  _TESTSCRIPT_TEST.fields_by_name['action']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT_TEARDOWN_TEARDOWNACTION.fields_by_name['operation']._options = None
  _TESTSCRIPT_TEARDOWN_TEARDOWNACTION.fields_by_name['operation']._serialized_options = b'\360\320\207\353\004\001\362\276\300\244\007\224\001sourceId.exists() or (targetId.count() + url.count() + params.count() = 1) or (type.code in (\'capabilities\' | \'search\' | \'transaction\' | \'history\'))'
  _TESTSCRIPT_TEARDOWN.fields_by_name['action']._options = None
  _TESTSCRIPT_TEARDOWN.fields_by_name['action']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT.fields_by_name['url']._options = None
  _TESTSCRIPT.fields_by_name['url']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT.fields_by_name['name']._options = None
  _TESTSCRIPT.fields_by_name['name']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT.fields_by_name['status']._options = None
  _TESTSCRIPT.fields_by_name['status']._serialized_options = b'\360\320\207\353\004\001'
  _TESTSCRIPT.fields_by_name['profile']._options = None
  _TESTSCRIPT.fields_by_name['profile']._serialized_options = b'\362\377\374\302\006\010Resource'
  _TESTSCRIPT._options = None
  _TESTSCRIPT._serialized_options = b'\300\237\343\266\005\003\262\376\344\227\0062http://hl7.org/fhir/StructureDefinition/TestScript\232\257\256\244\013*name.matches(\'[A-Z]([A-Za-z0-9_]){0,254}\')'
  _TESTSCRIPT._serialized_start=273
  _TESTSCRIPT._serialized_end=14097
  _TESTSCRIPT_STATUSCODE._serialized_start=1963
  _TESTSCRIPT_STATUSCODE._serialized_end=2243
  _TESTSCRIPT_ORIGIN._serialized_start=2246
  _TESTSCRIPT_ORIGIN._serialized_end=2513
  _TESTSCRIPT_DESTINATION._serialized_start=2516
  _TESTSCRIPT_DESTINATION._serialized_end=2788
  _TESTSCRIPT_METADATA._serialized_start=2791
  _TESTSCRIPT_METADATA._serialized_end=3951
  _TESTSCRIPT_METADATA_LINK._serialized_start=3098
  _TESTSCRIPT_METADATA_LINK._serialized_end=3353
  _TESTSCRIPT_METADATA_CAPABILITY._serialized_start=3356
  _TESTSCRIPT_METADATA_CAPABILITY._serialized_end=3882
  _TESTSCRIPT_FIXTURE._serialized_start=3954
  _TESTSCRIPT_FIXTURE._serialized_end=4297
  _TESTSCRIPT_VARIABLE._serialized_start=4300
  _TESTSCRIPT_VARIABLE._serialized_end=4910
  _TESTSCRIPT_SETUP._serialized_start=4913
  _TESTSCRIPT_SETUP._serialized_end=11949
  _TESTSCRIPT_SETUP_SETUPACTION._serialized_start=5150
  _TESTSCRIPT_SETUP_SETUPACTION._serialized_end=11949
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION._serialized_start=5486
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION._serialized_end=8145
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_RESOURCECODE._serialized_start=6684
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_RESOURCECODE._serialized_end=6963
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_ACCEPTCODE._serialized_start=6966
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_ACCEPTCODE._serialized_end=7193
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_CONTENTTYPECODE._serialized_start=7196
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_CONTENTTYPECODE._serialized_end=7428
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_METHODCODE._serialized_start=7431
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_METHODCODE._serialized_end=7714
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER._serialized_start=7717
  _TESTSCRIPT_SETUP_SETUPACTION_OPERATION_REQUESTHEADER._serialized_end=7988
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT._serialized_start=8148
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT._serialized_end=11903
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_DIRECTIONCODE._serialized_start=9710
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_DIRECTIONCODE._serialized_end=10002
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_CONTENTTYPECODE._serialized_start=7196
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_CONTENTTYPECODE._serialized_end=7428
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_OPERATORCODE._serialized_start=10240
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_OPERATORCODE._serialized_end=10529
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_REQUESTMETHODCODE._serialized_start=10532
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_REQUESTMETHODCODE._serialized_end=10822
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESOURCECODE._serialized_start=6684
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESOURCECODE._serialized_end=6963
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESPONSECODE._serialized_start=11107
  _TESTSCRIPT_SETUP_SETUPACTION_ASSERT_RESPONSECODE._serialized_end=11402
  _TESTSCRIPT_TEST._serialized_start=11952
  _TESTSCRIPT_TEST._serialized_end=13317
  _TESTSCRIPT_TEST_TESTACTION._serialized_start=12279
  _TESTSCRIPT_TEST_TESTACTION._serialized_end=13317
  _TESTSCRIPT_TEARDOWN._serialized_start=13320
  _TESTSCRIPT_TEARDOWN._serialized_end=13979
  _TESTSCRIPT_TEARDOWN_TEARDOWNACTION._serialized_start=13566
  _TESTSCRIPT_TEARDOWN_TEARDOWNACTION._serialized_end=13979
# @@protoc_insertion_point(module_scope)
