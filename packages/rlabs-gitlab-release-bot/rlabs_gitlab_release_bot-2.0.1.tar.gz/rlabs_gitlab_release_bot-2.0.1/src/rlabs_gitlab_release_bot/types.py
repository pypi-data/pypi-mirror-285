'''
    Types
'''
from typing import TypedDict
from typing import Required

'''
 {
    "version": {
        "current": "0.0.1",
        "bumped": "0.1.0"
    },
    changelog: {
        "added": [
            "feat: i'm a feature (#a1b2c3)",
        ]
        ...
        "__release_notes__": {
            "issues_addressed": [
                {
                    "issue": "...",
                    "web_link": "...",
                    "description": "..."
                },
                ...
            ]
            "additional_notes": [
                "notes",
                ...
            ]
        }
    }
}

'''
class IssuesAddressed(TypedDict):
    issue: str
    web_link: str
    description: str

class AdditionalNotes(TypedDict):
    notes: list[str]

class ReleaseNotes(TypedDict, total=False):
    issues_addressed: list[IssuesAddressed]
    additional_notes: list[str]

class ChangelogBase(TypedDict, total=False):
    added: list[str]
    changed: list[str]
    fixed: list[str]
    continuous_integration: list[str]
    other: list[str]
    performance: list[str]
    documentation: list[str]
    test: list[str]
    build: list[str]
    revert: list[str]

class Changelog(ChangelogBase):
    __release_notes__: Required[ReleaseNotes]

class Version(TypedDict):
    current: str
    bumped: str

class VersionAndChangelog(TypedDict):
    version: Version
    changelog: Changelog

'''
BumpPrefixes:
{
    "major": ["breaking change"],
    "minor": ["feat"],
    "patch": [
        'chore',
        'fix',
        'refactor',
        'perf',
        'docs',
        'style',
        'test',
        'build',
        'ci',
        'revert'
    ]
}
'''
class BumpPrefixes(TypedDict):
    major: list[str]
    minor: list[str]
    patch: list[str]

'''
Bumped commits:
{
    "major": ["breaking change"],
    "minor": ["feat"],
    "patch": [
        'chore',
        ...
    ]
}
'''

class BumpedCommits(TypedDict):
    major: list[str]
    minor: list[str]
    patch: list[str]
    bump_prefixes_used: BumpPrefixes
