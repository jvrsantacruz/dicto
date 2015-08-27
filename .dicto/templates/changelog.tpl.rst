{{version.strip()}} ({{current_date.date()}})
------------------

{% for commit in git_version_commits
   if  'Fix' in commit.summary
    or 'Adds' in commit.summary
    or 'Changes' in commit.summary -%}
* {{commit.summary}}
{% endfor %}
