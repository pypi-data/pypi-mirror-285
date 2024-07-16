# Auto generated from information_resource_registry.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-07-15T15:48:21
# Schema: Information-Resource-Registry-Schema
#
# id: https://w3id.org/biolink/information_resource_registry.yaml
# description:
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = "1.0.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
BIOGRID = CurieNamespace('BIOGRID', 'http://identifiers.org/biogrid/')
SO = CurieNamespace('SO', 'http://purl.obolibrary.org/obo/SO_')
BIOLINK = CurieNamespace('biolink', 'https://w3id.org/biolink/')
INFORES = CurieNamespace('infores', 'https://w3id.org/biolink/infores/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OBOINOWL = CurieNamespace('oboInOwl', 'http://www.geneontology.org/formats/oboInOwl#')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = CurieNamespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = INFORES


# Types

# Class references



@dataclass
class InformationResourceContainer(YAMLRoot):
    """
    A collection of information resources
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = INFORES["InformationResourceContainer"]
    class_class_curie: ClassVar[str] = "infores:InformationResourceContainer"
    class_name: ClassVar[str] = "InformationResourceContainer"
    class_model_uri: ClassVar[URIRef] = INFORES.InformationResourceContainer

    information_resources: Optional[Union[Union[dict, "InformationResource"], List[Union[dict, "InformationResource"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.information_resources, list):
            self.information_resources = [self.information_resources] if self.information_resources is not None else []
        self.information_resources = [v if isinstance(v, InformationResource) else InformationResource(**as_dict(v)) for v in self.information_resources]

        super().__post_init__(**kwargs)


@dataclass
class InformationResource(YAMLRoot):
    """
    A database or knowledgebase and its supporting ecosystem of interfaces and services that deliver content to
    consumers (e.g. web portals, APIs, query endpoints, streaming services, data downloads, etc.). A single
    Information Resource by this definition may span many different datasets or databases, and include many access
    endpoints and user interfaces. Information Resources include project-specific resources such as a Translator
    Knowledge Provider, and community knowledgebases like ChemBL, OMIM, or DGIdb.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = INFORES["InformationResource"]
    class_class_curie: ClassVar[str] = "infores:InformationResource"
    class_name: ClassVar[str] = "InformationResource"
    class_model_uri: ClassVar[URIRef] = INFORES.InformationResource

    id: str = None
    status: Optional[Union[str, "InformationResourceStatusEnum"]] = None
    name: Optional[str] = None
    xref: Optional[Union[str, List[str]]] = empty_list()
    synonym: Optional[Union[str, List[str]]] = empty_list()
    description: Optional[str] = None
    knowledge_level: Optional[Union[str, "KnowledgeLevelEnum"]] = None
    agent_type: Optional[Union[str, "AgentTypeEnum"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, str):
            self.id = str(self.id)

        if self.status is not None and not isinstance(self.status, InformationResourceStatusEnum):
            self.status = InformationResourceStatusEnum(self.status)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if not isinstance(self.xref, list):
            self.xref = [self.xref] if self.xref is not None else []
        self.xref = [v if isinstance(v, str) else str(v) for v in self.xref]

        if not isinstance(self.synonym, list):
            self.synonym = [self.synonym] if self.synonym is not None else []
        self.synonym = [v if isinstance(v, str) else str(v) for v in self.synonym]

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.knowledge_level is not None and not isinstance(self.knowledge_level, KnowledgeLevelEnum):
            self.knowledge_level = KnowledgeLevelEnum(self.knowledge_level)

        if self.agent_type is not None and not isinstance(self.agent_type, AgentTypeEnum):
            self.agent_type = AgentTypeEnum(self.agent_type)

        super().__post_init__(**kwargs)


# Enumerations
class InformationResourceStatusEnum(EnumDefinitionImpl):
    """
    The status of the infores identifier
    """
    released = PermissibleValue(text="released")
    deprecated = PermissibleValue(text="deprecated")
    draft = PermissibleValue(text="draft")
    modified = PermissibleValue(text="modified")

    _defn = EnumDefinition(
        name="InformationResourceStatusEnum",
        description="The status of the infores identifier",
    )

class KnowledgeLevelEnum(EnumDefinitionImpl):
    """
    The level of knowledge that supports an edge or node. This is a general categorization of the type of evidence
    that supports a statement, and is not intended to be a comprehensive description of the evidence. For example, a
    statement may be supported by a single publication, but that publication may contain multiple types of evidence,
    such as a computational prediction and a manual curation. In this case, the knowledge level would be "curated",
    and the evidence would be described in more detail in the evidence graph.
    """
    knowledge_assertion = PermissibleValue(
        text="knowledge_assertion",
        description="""knowledge asserted by a human expert, based on their interpretation of data or published study results""")
    statistical_association = PermissibleValue(
        text="statistical_association",
        description="""statistical associations calculated between variables in a clinical or omics dataset, by an automated  analysis pipeline""")
    curated = PermissibleValue(
        text="curated",
        description="""knowledge generated through manual curation or interpretation of data or published study results""")
    predicted = PermissibleValue(
        text="predicted",
        description="""predictions generated computationally through inference over less direct forms of evidence (without human  intervention or review)""")
    text_mined = PermissibleValue(
        text="text_mined",
        description="knowledge extracted from published text by NLP agents (without human intervention or review)")
    correlation = PermissibleValue(
        text="correlation",
        description="""statistical correlations calculated between variables in a clinical or omics dataset, by an automated  analysis pipeline""")
    observed = PermissibleValue(
        text="observed",
        description="""edge reports a phenomenon that was reported/observed to have occurred (and possibly some quantification,  e.g. how many times, at what frequency)""")
    other = PermissibleValue(
        text="other",
        description="knowledge level may not fit into the categories above, or is not provided/known")
    mixed = PermissibleValue(
        text="mixed",
        description="""used for sources that might provide edges with different knowledge levels, e.g.correlations in addition to  curated Edges - set tag to Curated, unless predicate rules override""")

    _defn = EnumDefinition(
        name="KnowledgeLevelEnum",
        description="""The level of knowledge that supports an edge or node.  This is a general categorization of the type of evidence that supports a statement, and is not intended to be a comprehensive description of the evidence.  For example, a statement may be supported by a single publication, but that publication may contain multiple types of evidence, such as a computational prediction and a manual curation.  In this case, the knowledge level would be \"curated\", and the evidence would be described in more detail in the evidence graph.""",
    )

class AgentTypeEnum(EnumDefinitionImpl):
    """
    The type of agent that supports an edge or node. This is a general categorization of the type of agent that
    supports a statement, and is not intended to be a comprehensive description of the agent. For example, a statement
    may be supported by a single publication, but that publication may contain multiple types of evidence, such as a
    computational prediction and a manual curation. In this case, the agent type would be "publication", and the
    evidence would be described in more detail in the evidence graph.
    """
    manual_agent = PermissibleValue(
        text="manual_agent",
        description="a human agent, such as a curator or expert")
    not_provided = PermissibleValue(
        text="not_provided",
        description="agent type is not provided or known")
    computational_model = PermissibleValue(
        text="computational_model",
        description="a computational model, such as a machine learning model")
    data_analysis_pipeline = PermissibleValue(
        text="data_analysis_pipeline",
        description="a data analysis pipeline, such as a bioinformatics pipeline")

    _defn = EnumDefinition(
        name="AgentTypeEnum",
        description="""The type of agent that supports an edge or node.  This is a general categorization of the type of agent that supports a statement, and is not intended to be a comprehensive description of the agent.  For example, a statement may be supported by a single publication, but that publication may contain multiple types of evidence, such as a computational prediction and a manual curation.  In this case, the agent type would be \"publication\", and the evidence would be described in more detail in the evidence graph.""",
    )

# Slots
class slots:
    pass

slots.status = Slot(uri=INFORES.status, name="status", curie=INFORES.curie('status'),
                   model_uri=INFORES.status, domain=None, range=Optional[Union[str, "InformationResourceStatusEnum"]])

slots.information_resources = Slot(uri=INFORES.information_resources, name="information_resources", curie=INFORES.curie('information_resources'),
                   model_uri=INFORES.information_resources, domain=None, range=Optional[Union[Union[dict, InformationResource], List[Union[dict, InformationResource]]]])

slots.name = Slot(uri=RDFS.label, name="name", curie=RDFS.curie('label'),
                   model_uri=INFORES.name, domain=None, range=Optional[str])

slots.id = Slot(uri=INFORES.id, name="id", curie=INFORES.curie('id'),
                   model_uri=INFORES.id, domain=None, range=str)

slots.xref = Slot(uri=INFORES.xref, name="xref", curie=INFORES.curie('xref'),
                   model_uri=INFORES.xref, domain=None, range=Optional[Union[str, List[str]]])

slots.synonym = Slot(uri=INFORES.synonym, name="synonym", curie=INFORES.curie('synonym'),
                   model_uri=INFORES.synonym, domain=None, range=Optional[Union[str, List[str]]])

slots.description = Slot(uri=RDFS.comment, name="description", curie=RDFS.curie('comment'),
                   model_uri=INFORES.description, domain=None, range=Optional[str])

slots.knowledge_level = Slot(uri=INFORES.knowledge_level, name="knowledge level", curie=INFORES.curie('knowledge_level'),
                   model_uri=INFORES.knowledge_level, domain=None, range=Optional[Union[str, "KnowledgeLevelEnum"]])

slots.agent_type = Slot(uri=INFORES.agent_type, name="agent type", curie=INFORES.curie('agent_type'),
                   model_uri=INFORES.agent_type, domain=None, range=Optional[Union[str, "AgentTypeEnum"]])