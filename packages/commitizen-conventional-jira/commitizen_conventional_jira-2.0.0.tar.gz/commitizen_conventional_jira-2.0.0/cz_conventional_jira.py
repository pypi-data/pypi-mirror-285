import re
from typing import Pattern, AnyStr

from commitizen import config
from commitizen.cz.conventional_commits import ConventionalCommitsCz


class ConventionalJiraCz(ConventionalCommitsCz):
    def schema_pattern(self) -> Pattern[AnyStr]:
        conf = config.read_cfg()
        jira_prefixes = conf.settings.get("jira_prefixes", None)
        jira_issues_required = conf.settings.get("jira_issues_required", False)
        jira_no_ticket_key = conf.settings.get("jira_no_ticket_key", None)
        if jira_prefixes and len(jira_prefixes) > 0:
            jira_prefix_pattern = "|".join(jira_prefixes)
            if len(jira_prefixes) > 1:
                jira_prefix_pattern = f"(?:{jira_prefix_pattern})"
            if jira_no_ticket_key:
                issue_pattern = fr"{jira_prefix_pattern}-(?:\d+(?:,{jira_prefix_pattern}-(?:\d+))*|{jira_no_ticket_key})"
            else:
                issue_pattern = fr"{jira_prefix_pattern}-\d+(?:,{jira_prefix_pattern}-(?:\d+))*"
            if jira_issues_required:
                pattern = fr"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)" \
                          fr"(\({issue_pattern}\))!?:(\s.*)"
            else:
                pattern = fr"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)" \
                          fr"(\({issue_pattern}\))?!?:(\s.*)"
        else:
            pattern = (
                r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"
                r"(\(\S+\))?!?:(\s.*)"
            )
        return re.compile(pattern)


discover_this = ConventionalJiraCz
