.. changelog::
    :version: {{redmine_version.name}}
    :released: {{current_date.date()}}

    {{codename}}
    {{redmine_version.description}} `(see roadmap) <{redmine_version.url}>`_

    Changes:

    {% for issue in redmine_issues %}
        .. change::
        :tags: {{issue.tracker.name|lower}}
        :tickets: {{issue.id}}

        {{issue.subject}}
    {% endfor %}
