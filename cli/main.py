import os
from itertools import chain
from typing import Dict, List

import github
import yaml
from fire import Fire

GITHUB_TOKEN: str = os.getenv('GITHUB_TOKEN')
gh: github.Github = github.Github(GITHUB_TOKEN)


class Label(object):
    def __init__(self, data: Dict) -> None:
        self.name = data.get('name')
        self.color = data.get('color')
        self.description = data.get('descrioption')


def load_config(filepath: str) -> Dict:
    data = None

    def __load() -> Dict:
        nonlocal data
        if data is None:
            data = yaml.load(open(filepath, 'r+'))
        return data

    return __load()


def expected_labels(data) -> List[Label]:
    list: List[Label] = [Label(d) for d in data]
    return list


def user_repositories(gh: github.Github) -> List[github.Repository.Repository]:
    username: str = gh.get_user().login
    return [
        r for r in gh.get_user().get_repos()
        if (not r.archived) and (r.owner.login == username)
    ]


def org_repositories(orgname: str,
                     gh: github.Github) -> List[github.Repository.Repository]:
    return [
        r for r in gh.get_organization(orgname).get_repos() if not r.archived
    ]


def target_repositories(data: Dict) -> List[github.Repository.Repository]:
    if data.get("user"):
        return user_repositories(gh)
    else:
        return chain.from_iterable([
            org_repositories(orgname, gh)
            for orgname in data.get('organizations')
        ])


def create_labels(current: List[github.Label.Label], expected: List[Label],
                  repo: github.Repository.Repository, run: bool) -> None:
    def __creation_plan(current: List[github.Label.Label],
                        expected: List[Label]) -> List[Label]:
        current_names: List[str] = [l.name for l in current]
        expected_names: List[str] = [l.name for l in expected]
        names: List[str] = list(set(expected_names) - set(current_names))
        return [l for l in expected if l.name in names]

    for l in __creation_plan(current, expected):
        print('  Create: `' + l.name + '`')
        if run:
            repo.create_label(l.name, l.color, l.description)


def delete_labels(current: List[github.Label.Label], expected: List[Label],
                  run: bool) -> None:
    def __deletion_plan(current: List[github.Label.Label],
                        expected: List[Label]) -> List[github.Label.Label]:
        current_names: List[str] = [l.name for l in current]
        exptected_names: List[str] = [l.name for l in expected]
        names = list(set(current_names) - set(exptected_names))
        return [l for l in current if l.name in names]

    for l in __deletion_plan(current, expected):
        print('  Delete: `' + l.name + '`')
        if run:
            l.delete()


def edit_labels() -> None:
    def __edition_plan(current: List[github.Label.Label],
                       expected: List[Label]) -> List[github.Label.Label]:
        # TODO not implemented
        return []

    # TODO not implemented
    pass


def sync(filepath='config.yaml', run=False):
    print('In sync...')
    if not run:
        print('======= Dry Run Mode =======')

    config: Dict = load_config(filepath)
    for repo in target_repositories(config):
        print(repo.full_name)
        current: List[github.Label] = repo.get_labels()
        expected: List[Label] = expected_labels(config.get('labels'))

        delete_labels(current, expected, run)
        create_labels(current, expected, repo, run)

    print('Complete!!')


if __name__ == '__main__':
    Fire({'sync': sync})
