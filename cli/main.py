import os
import fire
import yaml
from itertools import chain
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

    def sync(self, filepath='config.yaml'):
        config = Config(filepath, self.__github)

        repositories = config.repositories()

        print('In sync...')
        for repository in repositories:
            print(repository.full_name)
            self.__sync_label(repository, config.labels())
        print('Complete!!')

    def __sync_label(self, repository, labels):
        current = list(map(lambda l: l.name, repository.get_labels()))
        new = list(map(lambda l: l.name, labels))

        deletion_names = list(set(current) - set(new))
        deletion_labels = list(filter(lambda l: l.name in deletion_names, repository.get_labels()))
        for label in deletion_labels:
            print('  Delete: `' + label.name + '`')
            label.delete()

        creation_names = list(set(new) - set(current))
        creation_labels = list(filter(lambda l: l.name in creation_names, labels))
        for label in creation_labels:
            print('  Create: `' + label.name + '`')
            repository.create_label(label.name, label.color, label.description)

class Config(object):
    def __init__(self, filepath, github):
        self.__data = yaml.load(open(filepath, 'r+'))
        self.__github = github
        self.__labels = None
        self.__repositories = None

    def labels(self):
        if self.__labels is None:
            self.__labels = list(map(lambda l: Label(l), self.__data['labels']))
        return self.__labels

    def repositories(self):
        return list(chain(self.__get_user_repos(), self.__get_organizations_repos()))

    def __get_user_repos(self):
        try:
            state = self.__data['user']
        except KeyError:
            return []
        if not state:
            return []

        repos = self.__github.get_user().get_repos()
        user_name = self.__github.get_user().login
        return list(filter(lambda r: r.owner.login == user_name, repos))

    def __get_organizations_repos(self):
        try:
            orgs = self.__data['organizations']
        except KeyError:
            return []
        if orgs is None:
            return []
        expr = map(lambda o: self.__github.get_organization(o).get_repos(), orgs)
        return list(chain.from_iterable(expr))

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
