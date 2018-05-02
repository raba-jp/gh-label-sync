import os
import fire
import yaml
from github import Github

def find(iterable, default, pred):
    # http://docs.python.jp/3/library/itertools.html
    return next(filter(pred, iterable), default)

class CLI(object):
    def __init__(self):
        try:
            token = os.environ['GITHUB_TOKEN']
        except KeyError:
            print('Undefined `GITHUB_TOKEN` environment variable.')
            raise SystemExit(1)
        self.__github = Github(token)

    def sync(self, filepath='config.yaml', mode='namespace'):
        config = Config(filepath, self.__github)

        if mode == 'namespace':
            repositories = config.repositories_from_namespace()
        else:
            repositories = config.repositories_from_list()

        print('In sync...')
        for repository in repositories:
            print('  ' + repository.full_name)
            self.__sync_label(repository, config.labels())
        print('Complete!!')

    def __sync_label(self, repository, labels):
        current = list(map(lambda l: l.name, repository.get_labels()))
        new = list(map(lambda l: l.name, labels))
        deletion_labels = list(set(current) - set(new))
        creation_labels = list(set(new) - set(current))

        for target in deletion_labels:
            label = find(repository.get_labels(), None, lambda l: l.name == target)
            if label is None:
                continue
            print('Delete: ' + label.name)
            label.delete()
        for target in creation_labels:
            label = find(labels, None, lambda l: l.name == target)
            if label is None:
                continue
            print('Create: ' + label.name)
            repository.create_label(label.name, label.color, label.description)


class Config(object):
    def __init__(self, filepath, github):
        self.__data = yaml.load(open(filepath, 'r+'))
        self.__github = github

    def labels(self):
        return list(map(lambda l: Label(l), self.__data['labels']))

    def repositories_from_namespace(self):
        is_user = self.__data['is_user']
        namespace = self.__data['namespace']
        if is_user:
            repos = list(filter(lambda r: r.owner.login == namespace, self.__github.get_user().get_repos()))
        else:
            repos = list(self.__github.get_organization(namespace).get_repos())
        return repos

    def repositories_from_list(self):
        return list(map(lambda r: self.__github.get_repo(r), self.__data['repositories']))

class Label(object):
    def __init__(self, data):
        try:
            self.name = data['name']
            self.color = data['color']
            self.description = data['description']
        except KeyError:
            print('Invalid label.')
            SystemExit(1)


if __name__ == '__main__':
    fire.Fire(CLI)
