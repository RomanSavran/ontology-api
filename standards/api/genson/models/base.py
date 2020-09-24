import os
import json
from owlready2 import default_world, base, locstr, label, comment
from .extentions import restriction, domain, subPropertyOf, nest
from .extentions import range as owl_range
from .extentions import label as pot_label
from .extentions import comment as pot_comment


class AbstractRDFEntity:
    SKIP_BASES = 1
    VERSION = 1.1
    PREFIX = 'pot'

    def __init__(self, entity, export_onto_url):
        self.entity = entity
        self.export_onto_url = export_onto_url
        self.directories = self.get_files()

    def write_dump_to_file(self, dir_context, data_to_dump, is_json=False):
        """Function to write all entities into various stuctured files.
            Args:
                dir_context (str): Directory context.
                data_to_dump (dict of str: Any): Entity.
        """
        entity_dir_path = os.path.join(
            dir_context, self.directories.get('dir'))
        entity_file_path = os.path.join(
            entity_dir_path, self.directories.get('filename'))
        os.makedirs(entity_dir_path, exist_ok=True)

        if is_json:
            entity_file_path = entity_file_path[:-2]
        with open(entity_file_path, 'w', encoding='utf-8') as rf:
            rf.write(json.dumps(data_to_dump, indent=4,
                                separators=(',', ': '), ensure_ascii=False))

    @staticmethod
    def build_directories(entity):
        parents = entity.is_a
        new_directories = []
        if len(parents):
            for parent in parents:
                directories = AbstractRDFEntity.build_directories(parent)
                for directory in directories:
                    new_directories.append(
                        os.path.join(directory, entity.name))
            return new_directories
        else:
            directories = [entity.name, ]
        return directories

    def get_files(self):
        result_directories = []
        for result_directory in self.build_directories(self.entity):
            entities = result_directory.split(os.path.sep)
            result_directories.append({
                'dir': os.path.sep.join(entities[self.SKIP_BASES:-1]),
                'filename': f'{entities[-1]}.jsonld',
                'id': '/'.join(entities[self.SKIP_BASES:])
            })
        directories = result_directories
        return directories[0]

    def prop_get_full_id(self, owl_property):
        property_id = ''
        subproperties = self.build_subproperty(owl_property)
        if subproperties and subproperties[0].name != 'topDataProperty':
            property_id = f'{self.prop_get_full_id(subproperties[0])}/'
        return f'{property_id}{owl_property.name}'

    @staticmethod
    def build_labels(owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                labels (Dict[str: str]): Labels of owl_property.
        """
        labels = {}
        for l in label._get_indirect_values_for_class(owl_property):
            labels[l.lang] = str(l)
        if not labels.items():
            for l in pot_label._get_indirect_values_for_class(owl_property):
                if isinstance(l, locstr):
                    labels[l.lang] = str(l)
        return labels

    def build_nested_labels(self, owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                nested_labels (List[Dict[str: str]]): Nested labels of owl_property.
        """
        nested_labels = list()
        for l in owl_property.label:
            if l:
                property_nested_labels = list()
                for nested_label in label._get_indirect_values_for_class(l):
                    if isinstance(nested_label, locstr):
                        property_nested_labels.append({
                            nested_label.lang: nested_label
                        })

                nested_labels_template = {'rdfs:label': {}}

                domains = list()
                for d in l.domain:
                    if d and not isinstance(d, str):
                        domains.append(
                            '/'.join(self.build_nested_domains(d)[::-1]))

                for nl in property_nested_labels:
                    for k, v in nl.items():
                        nested_labels_template['rdfs:label'][k] = v
                    nested_labels_template['domain'] = [
                        f'{self.PREFIX}:{d}' for d in domains]
                nested_labels.append(nested_labels_template)

        return nested_labels

    @staticmethod
    def build_comments(owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                comments (List[Dict[str: str]]): Comments of owl_property.
        """
        comments = {}
        for c in comment._get_indirect_values_for_class(owl_property):
            comments[c.lang] = str(c)
        if not comments.items():
            for c in pot_comment._get_indirect_values_for_class(owl_property):
                if isinstance(c, locstr):
                    comments[c.lang] = str(c)
        return comments

    def build_nested_comments(self, owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                    Property of entity.
            Returns:
                nested_comments (List[Dict[str: str]]): Nested comments of owl_property.
        """
        nested_comments = list()
        for c in owl_property.comment:
            if c:
                nested_comments_template = {'rdfs:comment': {}}

                domains = list()
                for d in c.domain:
                    if d and not isinstance(d, str):
                        domains.append(
                            '/'.join(self.build_nested_domains(d)[::-1]))

                for k, v in self.build_comments(c).items():
                    nested_comments_template['rdfs:comment'][k] = v
                nested_comments_template['domain'] = [
                    f'{self.PREFIX}:{d}' for d in domains]
                nested_comments.append(nested_comments_template)
        return nested_comments

    def build_domains(self, owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass):                 
                    Property of entity.
            Returns:
                domains (List[str]): Domains of owl_property.
        """
        domains = list()
        for d in domain._get_indirect_values_for_class(owl_property):
            domains.append(
                f'{self.PREFIX}:{"/".join(self.build_nested_domains(d)[::-1])}')
        return domains

    @staticmethod
    def build_nested_domains(d):
        """
            Args:
                d (ThingClass):                 
                    Property of entity.
            Returns:
                nested_domains (List[str]): Nested domains of owl_property.
        """
        parents = {}
        if d and not isinstance(d, str):
            for a in d.ancestors():
                parent, child = str(a).split('.')
                parents[child] = parent

            nested_domains = []
            nested_domains.append(d.name)
            child = d.name
            while parents[child] != 'pot' and parents[child] != "Vocabulary":
                nested_domains.append(parents[child])
                child = parents[child]
        return nested_domains

    @staticmethod
    def build_ranges(owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass): 
                    Property of entity.
            Returns:
                result_ranges (List[str]): Ranges of owl_property.
        """
        result_ranges = list()
        for range_type in owl_range._get_indirect_values_for_class(owl_property):
            try:
                result_ranges.append(
                    str(default_world._unabbreviate(base._universal_datatype_2_abbrev[range_type])).replace(
                        'http://www.w3.org/2001/XMLSchema#', 'xsd:'))
            except:
                result_ranges.append(
                    str(range_type).replace('XMLSchema.', 'xsd:'))
        return result_ranges

    @staticmethod
    def build_restrictions(owl_property):
        """
        Args:
            owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass): 
                Property of entity.
        Returns:
            result_restrictions (List[str]): Restrictions of owl_property
        """
        result_restrictions = []
        for restriction_type in restriction._get_indirect_values_for_class(owl_property):
            try:
                result_restrictions.append(
                    str(default_world._unabbreviate(base._universal_datatype_2_abbrev[restriction_type])).replace(
                        'http://www.w3.org/2001/XMLSchema#', 'xsd:'))
            except:
                result_restrictions.append(
                    str(restriction_type).replace('XMLSchema.', 'xsd:'))
        return result_restrictions

    @staticmethod
    def build_subproperty(owl_property):
        """
            Args:
                owl_property (AnnotationPropertyClass or DataPropertyClass or ObjectPropertyClass):
                    Property of entity.
            Returns:
                (List[ObjectPropertyClass] or List[DataPropertyClass]): Subproperties of owl_property.
        """
        return list(subPropertyOf._get_indirect_values_for_class(owl_property))
