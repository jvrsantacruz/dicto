{{version.strip()}} ({{current_date.date()}})
------------------

{% for commit in hg_version_commits
   if  'Fix' in commit.desc
    or 'Adds' in commit.desc
    or 'Updates' in commit.desc
    or 'Changes' in commit.desc -%}
* {{commit.desc.splitlines()[0]}}
{% endfor %}
