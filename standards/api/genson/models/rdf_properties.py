import os
from owlready2 import Thing, default_world, base, locstr, label, comment
from .base import AbstractRDFEntity
from .extentions import restriction, domain, subPropertyOf, nest


class RDFProperty(AbstractRDFEntity):
    SKIP_BASES = 2

    def get_files(self):
        directories = max(self.build_directories(self.entity), key=len)
        property_directories = directories.split(os.path.sep)[self.SKIP_BASES:]
        if property_directories[0] == 'topDataProperty':
            property_directories.pop(0)
        return {
            'dir': os.path.sep.join(property_directories[:-1]),
            'filename': f'{property_directories[-1]}.jsonld',
            'id': '/'.join(property_directories[self.SKIP_BASES:])
        }


class VocabularyRDFProperty(RDFProperty):
    def create_vocabulary_from_rdf_property(self):
        """Return dict of generated properties to create Vocabulary from rdf property.
            Returns:
                vocabulary_template (dict of str: Any): Dictionary of required parameters
        """
        # Define main Vocabulary template for property
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
        entity_properties['@id'] = f'{self.PREFIX}:{self.prop_get_full_id(self.entity)}'
        entity_properties['@type'] = default_world._unabbreviate(self.entity._owl_type).replace(
            'http://www.w3.org/2002/07/owl#', 'owl:')

        subproperties = self.build_subproperty(self.entity)
        if subproperties:
            entity_properties[
                'subPropertyOf'] = f'{self.PREFIX}:{self.prop_get_full_id(subproperties[0])}'

        labels = self.build_labels(self.entity)
        if labels.items():
            entity_properties["rdfs:label"] = labels

        comments = self.build_comments(self.entity)
        if comments.items():
            entity_properties["rdfs:comment"] = comments

        nested_labes = self.build_nested_labels(self.entity)
        if nested_labes:
            entity_properties["label"] = nested_labes

        nested_comments = self.build_nested_comments(self.entity)
        if nested_comments:
            entity_properties["comment"] = nested_comments

        ranges = self.build_ranges(self.entity)
        if ranges:
            entity_properties[f'{self.PREFIX}:valueType'] = ranges

        restrictions = self.build_restrictions(self.entity)
        if restrictions:
            entity_properties['xsd:restriction'] = restrictions

        domains = self.build_domains(self.entity)
        if domains:
            entity_properties['domain'] = domains

        vocabulary_template[self.entity.name] = entity_properties

        return vocabulary_template
