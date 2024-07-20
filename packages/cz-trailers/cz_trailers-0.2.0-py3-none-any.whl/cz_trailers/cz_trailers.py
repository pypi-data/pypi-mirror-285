import re

from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen import git
from jinja2 import PackageLoader

class ConventionalCommitsCzTrailers(ConventionalCommitsCz):
    template_loader = PackageLoader("cz_trailers", "templates")
    commit_parser = "\A(?:(?P<change_type>[^\(!:]+)(?:\((?P<scope>[^\)]+)\))?(?P<breaking>!)?: (?P<message>.+))(?:(?!(?:\n{2}^(?:BREAKING[ -]CHANGE|[a-zA-Z0-9_\-]+)(?:: | #\b)[^\n:]+(\n*\b)?)+)\n{2}(?P<body>(?:(?!\n{2}(?:^(?:BREAKING[ -]CHANGE|[a-zA-Z0-9_\-]+)(?:: | #\b)[^\n:]+(\n*\b)?)+).|\n+?)+?))?(?:\n{2}(?P<footers>(?:^(?:BREAKING[ -]CHANGE|[a-zA-Z0-9_\-]+)(?:: | #\b)[^\n:]+(\n*\b)?)+))?(?:\n*)\Z"
    change_type_map = {
        "feat": "Features",
        "fix": "Fixes",
        "refactor": "Refactors",
        "perf": "Performance",
        "docs": "Documentation",
        "build": "Build",
    }
    changelog_change_types = ["feat", "fix", "docs", "build"]
    change_type_order = list(change_type_map.values())
    footer_re = re.compile(
        "(?P<key>(?:^(?:BREAKING[-]CHANGE|[a-zA-Z0-9_\-]+)))(?:: | #\b)(?P<value>[^\n:]+(?:\n*\b)?)"
    )

    def changelog_message_builder_hook(
        self, parsed_message: dict, commit: git.GitCommit
    ) -> dict | list | None:
        if parsed_message["change_type"] not in self.changelog_change_types:
            return None
        rev = commit.rev
        m = parsed_message["message"]
        footers = parsed_message["footers"]
        if footers is not None:
            _footers = self.footer_re.findall(footers)
            footers = {}
            for footer in _footers:
                footers.setdefault(footer[0].lower(),[]).append(footer[1])
        else:
            footers = {}

        parsed_message["footers"] = footers

        parsed_message["commit"] = commit.__dict__
        return parsed_message
