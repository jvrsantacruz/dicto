Hemos cerrado en pruebas {{project}} {{redmine_version.name}}

| Proyecto      |  {{project}} |
|-------------- | ----------------|
| Versión       | {{redmine_version.name}}  |
| Fecha         | {{current_date.date()}} |
| URL           | [{{project|lower}}-prueba.taric.local](http://{{project|lower}}-prueba.taric.local) |
| Usa Accounts  | [caronte-prueba.taric.local](http://caronte-prueba.taric.local)  |
| Documentación | [docs.taric.local/docs/{{project|lower}}/{{redmine_version.name}}](http://docs.taric.local/docs/{{project|lower}}/{{redmine_version.name}}) |
| Planificación | [redmine/versions/{{redmine_version.name}}]({{redmine_version.url}}) |
| Cambios       | [docs.taric.local/docs/{{project|lower}}/{{redmine_version.name}}/changelog.html](http://docs.taric.local/docs/{{project|lower}}/{{redmine_version.name}}/changelog.html#change-{{redmine_version.name}}) |

Los cambios incluyen:
{% for issue in redmine_issues %}
* **{{issue.tracker.name}}** ([#{{issue.id}}]({{issue.url}})) {{issue.subject}}
{% endfor %}
