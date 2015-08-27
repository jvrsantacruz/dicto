Hemos cerrado en pruebas {{project}} {{redmine_version.name}}

| Proyecto      |  {{project}} |
|-------------- | ----------------|
| Versión       | {{redmine_version.name}}  |
| Fecha         | {{current_date.date()}} |
| URL           | [{{project|lower}}-prueba](http://{{project|lower}}-prueba) |
| Usa Accounts  | [caronte-prueba](http://caronte-prueba)  |
| Documentación | [docs/docs/{{project|lower}}/{{redmine_version.name}}](http://docs/docs/{{project|lower}}/{{redmine_version.name}}) |
| Planificación | [redmine/versions/{{redmine_version.name}}]({{redmine_version.url}}) |
| Cambios       | [docs/docs/{{project|lower}}/{{redmine_version.name}}/changelog.html](http://docs/docs/{{project|lower}}/{{redmine_version.name}}/changelog.html#change-{{redmine_version.name}}) |

Los cambios incluyen:
{% for issue in redmine_issues %}
* **{{issue.tracker.name}}** ([#{{issue.id}}]({{issue.url}})) {{issue.subject}}
{% endfor %}
