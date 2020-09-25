from owlready2 import Thing, default_world, base, label, comment
from .base import AbstractRDFEntity
from .extentions import Identity, readonly, restriction, required, domain, subClassOf, subPropertyOf, nest


class RDFClass(AbstractRDFEntity):
    def __init__(self, entity, onto, export_onto_url):
        super().__init__(entity, export_onto_url)
        self.onto = onto

    @staticmethod
    def build_subclass(entity):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass):
                    Property of entity.
            Returns:
                (List[]): Subclasses of entity.
        """
        return list(subClassOf._get_indirect_values_for_class(entity))

    @staticmethod
    def build_required(owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                required_attr (bool): Is owl_property required
        """
        required_attr = required._get_indirect_values_for_class(owl_property)
        if required_attr:
            return required_attr[0]
        return False

    def class_get_full_id(self, entity):
        """
            Args:
                entity (ThingClass): ThingClass entity.
            Returns:
                (str):  Class id and name of entity.
        """
        class_id = ''
        subclass = self.build_subclass(entity)
        if subclass and subclass[0] != Thing:
            class_id = f'{self.class_get_full_id(subclass[0])}/'
        return f'{class_id}{entity.name}'

    def build_attributes(self):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                total_attributes (List[]): List of attributes
        """
        total_attributes = set()

        for a in self.onto.data_properties():
            if self.entity.ancestors().intersection(a.domain):
                total_attributes.add(a)

        for a in self.onto.object_properties():
            if self.entity.ancestors().intersection(a.domain):
                total_attributes.add(a)

        return total_attributes


class ContextRDFClass(RDFClass):
    def create_context_from_rdf_class(self):
        """Return dict of generated properties to create Context from rdf classes.
            Returns:
                context_template (dict of str: Any): Dictionary of required parameters
        """
        context_template = {
            '@version': self.VERSION,
            '@vocab': f"{self.export_onto_url}Vocabulary/{self.directories.get('id')}",
            '@classDefinition': f"{self.export_onto_url}ClassDefinitions/{self.directories.get('id')}",
            self.entity.name: {"@id": self.entity.name},
            '@schema': f"{self.export_onto_url}Schema/{self.directories.get('id')}",
            f'{self.PREFIX}': {
                '@id': f'{self.export_onto_url}Vocabulary/',
                '@prefix': True
            },
            'data': f'{self.PREFIX}:data',
            'metadata': f'{self.PREFIX}:metadata'
        }
        if Identity in self.entity.ancestors():
            context_template["@base"] = "https://api.oftrust.net/identities/v1/"

        # Define and fill propeties for each supported attribute
        total_attributes = self.build_attributes()
        for rdf_attribute in total_attributes:
            attribute_properties = dict()
            attribute_properties[
                '@id'] = f'{self.PREFIX}:{self.prop_get_full_id(rdf_attribute)}'

            nest_list = nest._get_indirect_values_for_class(rdf_attribute)
            if nest_list:
                attribute_properties['@nest'] = nest_list[0].name

            context_template[rdf_attribute.name] = attribute_properties

        context_wrapper = {'@context': context_template}
        return context_wrapper


class ClassDefinitionsRDFClass(RDFClass):
    def create_definition_from_rdf_class(self):
        """Return dict of generated properties to create ClassDefinition from rdf classes.
            Returns:
                definition_template (dict of str: Any): Dictionary of required parameters
        """
        # Define main ClassDefinition template
        definition_template = {
            '@context': {
                '@version': self.VERSION,
                '@vocab': f"{self.export_onto_url}Vocabulary/{self.directories.get('id')}",
                'xsd': {
                    '@id': 'http://www.w3.org/2001/XMLSchema#',
                    '@prefix': True
                },
                f'{self.PREFIX}': {
                    '@id': f'{self.export_onto_url}Vocabulary/',
                    '@prefix': True
                },
                'description': {
                    '@id': 'rdfs:comment',
                    '@container': ['@language', '@set']
                },
                'label': {
                    '@id': 'rdfs:label',
                    '@container': ['@language', '@set']
                },
                'comment': {
                    '@id': 'rdfs:comment',
                    '@container': ['@language', '@set']
                }
            },
        }
        # Define and fill entity propeties: subclasses, labels, comments
        entity_properties = dict()
        entity_properties['@id'] = f'{self.PREFIX}:{self.directories.get("id")}'
        entity_properties['@type'] = 'owl:Class'

        subclasses = self.build_subclass(self.entity)
        if subclasses and subclasses[0] != Thing:
            entity_properties['subClassOf'] = f'{self.PREFIX}:{subclasses[0].name}'

        labels = self.build_labels(self.entity)
        if labels:
            entity_properties['rdfs:label'] = labels

        comments = self.build_comments(self.entity)
        if comments:
            entity_properties['rdfs:comment'] = comments

        # Define supported attributes template
        supported_attrs = {
            'data': {
                '@id': f'{self.PREFIX}:data',
                '@type': f'{self.PREFIX}:SupportedAttribute',
                'rdfs:label': 'data',
                'rdfs:comment': {
                    'en-us': 'data'
                },
                f'{self.PREFIX}:required': False,
            }
        }

        # Define and fill propeties for each supported attribute
        total_attributes = self.build_attributes()
        for rdf_attribute in total_attributes:
            attribute_properties = dict()
            attribute_properties[
                '@id'] = f'{self.PREFIX}:{self.prop_get_full_id(rdf_attribute)}'
            attribute_properties['@type'] = default_world._unabbreviate(rdf_attribute._owl_type).replace(
                'http://www.w3.org/2002/07/owl#', 'owl:')

            subproperties = self.build_subproperty(rdf_attribute)
            if subproperties:
                attribute_properties[
                    'subPropertyOf'] = f'{self.PREFIX}:{self.prop_get_full_id(subproperties[0])}'

            labels = self.build_labels(rdf_attribute)
            if labels.items():
                attribute_properties["rdfs:label"] = labels

            comments = self.build_comments(rdf_attribute)
            if comments.items():
                attribute_properties["rdfs:comment"] = comments

            nested_labes = self.build_nested_labels(rdf_attribute)
            if nested_labes:
                attribute_properties["label"] = nested_labes

            nested_comments = self.build_nested_comments(rdf_attribute)
            if nested_comments:
                attribute_properties["comment"] = nested_comments

            ranges = self.build_ranges(rdf_attribute)
            if ranges:
                attribute_properties[f'{self.PREFIX}:valueType'] = ranges

            restrictions = self.build_restrictions(rdf_attribute)
            if restrictions:
                attribute_properties['xsd:restriction'] = restrictions

            is_required = self.build_required(rdf_attribute)
            attribute_properties[f'{self.PREFIX}:required'] = is_required

            is_readonly = readonly._get_indirect_values_for_class(
                rdf_attribute)
            if is_readonly:
                attribute_properties[f'{self.PREFIX}:readonly'] = is_readonly[0]

            supported_attrs[str(rdf_attribute.name)] = attribute_properties

        # Add attribute propeties to ClassDefinition template
        entity_properties[f'{self.PREFIX}:supportedAttribute'] = supported_attrs
        definition_template[f'{self.PREFIX}:supportedClass'] = entity_properties

        return definition_template


class VocabularyRDFClass(RDFClass):
    def create_vocabulary_from_rdf_class(self):
        """Return dict of generated properties to create Vocabulary from rdf classes.
            Returns:
                vocabulary_template (dict of str: Any): Dictionary of required parameters
        """
        # Define main Vocabulary template for class
        vocabulary_template = {
            '@context': {
                '@version': self.VERSION,
                f'{self.PREFIX}': {
                    '@id': f'{self.export_onto_url}Vocabulary/',
                    '@prefix': True
                },
                'rdf': {
                    '@id': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                    '@prefix': True
                },
                'rdfs': {
                    '@id': 'http://www.w3.org/2000/01/rdf-schema#',
                    '@prefix': True
                },
                'owl': {
                    '@id': 'http://www.w3.org/2002/07/owl#',
                    '@prefix': True
                },
                'vs': {
                    '@id': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
                },
                'xsd': {
                    '@id': 'http://www.w3.org/2001/XMLSchema#',
                    '@prefix': True
                },
                'label': {
                    '@id': 'rdfs:label',
                    "@container": ['@language', '@set']
                },
                'comment': {
                    '@id': 'rdfs:comment',
                    "@container": ['@language', '@set']
                }
            }
        }
        # Define and fill entity propeties: subclasses, labels, comments
        entity_properties = dict()
        entity_properties['@id'] = f'{self.PREFIX}:{self.directories.get("id")}'
        entity_properties['@type'] = 'owl:Class'

        subclasses = self.build_subclass(self.entity)
        if subclasses and subclasses[0] != Thing:
            entity_properties['subClassOf'] = f'{self.PREFIX}:{subclasses[0].name}'

        labels = self.build_labels(self.entity)
        if labels:
            entity_properties['rdfs:label'] = labels

        comments = self.build_comments(self.entity)
        if comments:
            entity_properties['rdfs:comment'] = comments

        vocabulary_template[self.entity.name] = entity_properties

        for dependent in self.entity.subclasses():
            vocabulary_template[dependent.name] = {
                'rdfs:subClassOf': {
                    '@id': f'{self.PREFIX}:{self.class_get_full_id(dependent).replace(f"/{dependent.name}", "")}'
                }
            }

        # Define and fill propeties for each supported attribute
        total_attributes = self.build_attributes()
        for rdf_attribute in total_attributes:
            attribute_properties = dict()
            attribute_properties[
                '@id'] = f'{self.PREFIX}:{self.prop_get_full_id(rdf_attribute)}'
            attribute_properties['@type'] = default_world._unabbreviate(rdf_attribute._owl_type).replace(
                'http://www.w3.org/2002/07/owl#', 'owl:')

            subproperties = self.build_subproperty(rdf_attribute)
            if subproperties:
                attribute_properties[
                    'subPropertyOf'] = f'{self.PREFIX}:{self.prop_get_full_id(subproperties[0])}'

            labels = self.build_labels(rdf_attribute)
            if labels.items():
                attribute_properties["rdfs:label"] = labels

            comments = self.build_comments(rdf_attribute)
            if comments.items():
                attribute_properties["rdfs:comment"] = comments

            nested_labes = self.build_nested_labels(rdf_attribute)
            if nested_labes:
                attribute_properties["label"] = nested_labes

            nested_comments = self.build_nested_comments(rdf_attribute)
            if nested_comments:
                attribute_properties["comment"] = nested_comments

            ranges = self.build_ranges(rdf_attribute)
            if ranges:
                attribute_properties[f'{self.PREFIX}:valueType'] = ranges

            restrictions = self.build_restrictions(rdf_attribute)
            if restrictions:
                attribute_properties['xsd:restriction'] = restrictions

            domains = self.build_domains(rdf_attribute)
            if domains:
                attribute_properties['domain'] = domains

            vocabulary_template[rdf_attribute.name] = attribute_properties

        return vocabulary_template


class SchemaRDFClass(RDFClass):
    def create_schema_from_rdf_class(self):
        """Return dict of generated properties to create Schema from rdf classes.
            Returns:
                schema (dict of str: Any): Dictionary of required parameters
        """
        properties = set()
        parents = set()
        labels = dict()
        comments = dict()
        examples = dict()
        required_attrs = list()

        # Define and fill propeties for each supported attribute
        total_attributes = self.build_attributes()
        for attr in total_attributes:
            # Build required
            if self.build_required(attr):
                required_attrs.append(attr.name)

            # Build labels according to schema specifications
            attr_labels = self.build_labels(attr)
            if attr_labels.get('en-us'):
                labels[attr.name] = attr_labels['en-us']
            else:
                attr_nested_labels = self.build_nested_labels(attr)
                if attr_nested_labels:
                    labels[attr.name] = attr_nested_labels[0]['rdfs:label']['en-us']
                else:
                    labels[attr.name] = ''

            # Build comments according to schema specifications
            attr_comments = self.build_comments(attr)
            if attr_comments.get('en-us'):
                comments[attr.name] = attr_comments['en-us']
            else:
                attr_nested_comments = self.build_nested_comments(attr)
                if attr_nested_comments:
                    for c in attr_nested_comments:
                        for d in c.get('domain'):
                            if self.entity.name == d.split(':')[-1]:
                                attr_nested_comment = c['rdfs:comment']
                                if attr_nested_comment.get('en-us'):
                                    comments[attr.name] = attr_nested_comment['en-us']
                                else:
                                    comments[attr.name] = ''
                else:
                    comments[attr.name] = ''

            examples[attr.name] = attr.example if attr.example else ''

            # Build parent properties
            parent = nest._get_indirect_values_for_class(
                attr)[0] if nest._get_indirect_values_for_class(attr) else None
            if parent:
                properties.add((parent.name, attr.name))
            else:
                parents.add(attr.name)

        properties_dict = {}
        for k, v in properties:
            if k in properties_dict:
                properties_dict[k].append(v)
            else:
                properties_dict[k] = [v]

        for p in parents:
            if p not in properties_dict:
                properties_dict[p] = []

        result = dict()
        result["@context"] = {
            "type": "string",
            "minLength": 1,
            "const": f"{self.export_onto_url}Context/{self.directories.get('id')}/"
        }
        result["@type"] = {
            "type": "string",
            "minLength": 1,
            "enum": [self.entity.name],
            "const": self.entity.name
        }

        required_attrs.append("@context")
        required_attrs.append("@type")

        if 'id' in required_attrs:
            required_attrs.remove('id')
            required_attrs.append("@id")

        prop_parent = {v[0] for v in properties}
        for i in parents:
            if i in prop_parent:
                result[i] = {"title": "", "description": "",
                             "type": "object", "properties": {}}
            else:
                result[i] = {"title": "", "description": "", "type": "string"}

        for key, values in properties_dict.items():
            for v in values:
                result[key]["title"] = labels[key]
                result[key]["description"] = comments[key]
                result[key]["properties"][v] = {
                    "title": labels[v] if v in labels else '',
                    "description": comments[v] if v in comments else '',
                    "type": "string"
                }
                if examples[key]:
                    result[key]["examples"] = examples[key]
                if key in result and examples[v]:
                    result[key]["properties"][v]["examples"] = examples[v]

        if 'id' in result:
            result['@id'] = result['id']
            del result['id']

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema",
            "type": "object",
            "properties": result,
            "required": required_attrs
        }

        return schema


class DataExampleRDFClass(RDFClass):
    def create_data_example_from_schema(self, schema_data):
        """Generate data example based on schema.
            Args:
                schema_data (str): Schema data.
            Returns:
                data_example (dict of str: Any): Dictionary of required parameters
        """
        # Build data example json based on schema

        data_example = dict()
        data_example['@context'] = f'{self.export_onto_url[:-1]}/Contex/{self.directories["id"]}'
        data_example['@type'] = f'{self.directories["id"].split("/")[-1]}'
        data_example['@id'] = ''
        data_example['data'] = ''
        data_example['metadata'] = ''

        for i in schema_data['properties']:
            if i != '@type' and i != '@context':
                if schema_data['properties'][i].get('properties'):
                    data_example[i] = {k: schema_data['properties'][i]['properties'][k]['examples'][0]
                                       if 'examples' in schema_data['properties'][i]['properties'][k] else '' for k in schema_data['properties'][i]['properties']}
                else:
                    data_example[i] = ''

        return data_example


class ContextDataProduct(RDFClass):
    def create_context_from_data_product(self, manual_path):
        """Return dict of generated properties to create Context from rdf classes.
            Returns:
                context_template (dict of str: Any): Dictionary of required parameters
        """
        self.directories['dir'] = '/'.join(manual_path[:0:-1])
        self.directories['filename'] = f'{manual_path[0]}.jsonld'
        self.directories['id'] = '/'.join(manual_path[::-1])

        context_template = {
            '@version': self.VERSION,
            self.entity.name: {"@id": f'pot:{self.entity.name}'},
            '@schema': f"{self.export_onto_url}Schema/{self.directories.get('id')}",
            f'{self.PREFIX}': {
                '@id': f'{self.export_onto_url}Vocabulary/',
                '@prefix': True
            }
        }

        # Hard Code for now
        context_template["productCode"] = {"@id": "pot:productCode"}
        context_template["timestamp"] = {"@id": "pot:timestamp"}
        context_template["parameters"] = {"@id": "pot:parameters"}

        # Define and fill propeties for each supported attribute
        total_attributes = self.build_attributes()
        for rdf_attribute in total_attributes:
            attribute_properties = dict()
            attribute_properties['@id'] = f'{self.PREFIX}:{str(rdf_attribute).split(".")[1]}'
            attribute_properties['@nest'] = "parameters"

            context_template[rdf_attribute.name] = attribute_properties

        for dependent in self.entity.subclasses():
            context_template[dependent.name] = {
                'rdfs:subClassOf': {
                    '@id': f'{self.PREFIX}:{self.class_get_full_id(dependent).replace(f"/{dependent.name}", "")}'
                }
            }

        context_wrapper = {'@context': context_template}
        return context_wrapper
