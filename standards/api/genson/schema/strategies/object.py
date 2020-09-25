from collections import defaultdict
from re import search
from .base import SchemaStrategy

# import required staff and builders
from owlready2 import get_ontology
from ...models.extentions import ONTO
from ...models.rdf_properties import RDFProperty

ONTO_PROPERTIES = {RDFProperty(i, "https://standards.oftrust.net/v2/").entity.name: RDFProperty(
    i, "https://standards.oftrust.net/v2/") for i in ONTO.properties()}


class Object(SchemaStrategy):
    """
    object schema strategy
    """
    KEYWORDS = ('type', 'properties', 'patternProperties', 'required')

    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'object'

    @staticmethod
    def match_object(obj):
        return isinstance(obj, dict)

    def __init__(self, node_class):
        super(Object, self).__init__(node_class)

        self._properties = defaultdict(node_class)
        self._pattern_properties = defaultdict(node_class)
        self._required = None
        self._include_empty_required = False

    def add_schema(self, schema):
        super(Object, self).add_schema(schema)
        if 'properties' in schema:
            for prop, subschema in schema['properties'].items():
                subnode = self._properties[prop]
                if subschema is not None:
                    subnode.add_schema(subschema)
        if 'patternProperties' in schema:
            for pattern, subschema in schema['patternProperties'].items():
                subnode = self._pattern_properties[pattern]
                if subschema is not None:
                    subnode.add_schema(subschema)
        if 'required' in schema:
            required = set(schema['required'])
            if not required:
                self._include_empty_required = True
            if self._required is None:
                self._required = required
            else:
                self._required &= required

    def add_object(self, obj):
        properties = set()
        for prop, subobj in obj.items():
            pattern = None
            if prop not in self._properties:
                pattern = self._matching_pattern(prop)

            if pattern is not None:
                self._pattern_properties[pattern].add_object(subobj)
            else:
                properties.add(prop)
                self._properties[prop].add_object(subobj)

        if self._required is None:
            self._required = properties
        else:
            self._required &= properties

    def _matching_pattern(self, prop):
        for pattern in self._pattern_properties.keys():
            if search(pattern, prop):
                return pattern

    def _add(self, items, func):
        while len(self._items) < len(items):
            self._items.append(self._schema_node_class())

        for subschema, item in zip(self._items, items):
            getattr(subschema, func)(item)

    def to_schema(self):
        schema = super(Object, self).to_schema()
        schema['type'] = 'object'
        if self._properties:
            schema['properties'] = self._properties_to_schema(
                self._properties)
        if self._pattern_properties:
            schema['patternProperties'] = self._properties_to_schema(
                self._pattern_properties)
        if self._required or self._include_empty_required:
            schema['required'] = sorted(self._required)
        return schema

    def _properties_to_schema(self, properties):
        schema_properties = {}
        for prop, schema_node in properties.items():
            schema_properties[prop] = schema_node.to_schema()

            l = ""
            c = ""
            try:
                _onto_property = ONTO_PROPERTIES[prop]
                if _onto_property:
                    l = _onto_property.build_labels(_onto_property.entity)
                    # If built labels is not empty, take en-us only. Else make sure that "title" is str.
                    if l:
                        l = l['en-us']
                    else:
                        l = ""

                    c = _onto_property.build_comments(_onto_property.entity)
                    # If built labels is not empty, take en-us only. Else make sure that "title" is str.
                    if c:
                        c = c['en-us']
                    else:
                        c = ""
                # Add title to schema
                # schema_properties[prop]['examples'] = []
            except:
                print(prop)

            schema_properties[prop]['title'] = l
            schema_properties[prop]['description'] = c

        return schema_properties
