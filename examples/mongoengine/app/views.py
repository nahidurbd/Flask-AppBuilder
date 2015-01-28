import calendar
from flask_appbuilder import expose, has_access
from flask import url_for, make_response, Response
from flask.ext.appbuilder import ModelView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_appbuilder.charts.views import GroupByChartView
from flask.ext.appbuilder.models.group import aggregate_count
from flask.ext.babelpkg import lazy_gettext as _


from app import appbuilder
from .models import ContactGroup, Contact, Tags


class ContactModelView(ModelView):
    datamodel = MongoEngineInterface(Contact)
    list_columns = ['name', 'personal_celphone', 'birthday','contact_group']


class GroupModelView(ModelView):
    datamodel = MongoEngineInterface(ContactGroup)
    related_views = [ContactModelView]
    search_columns = ['name']
    show_columns = ['name', 'download']
    list_columns = ['name', 'download']

    @expose('/mongo_download/<pk>')
    @has_access
    def mongo_download(self, pk):
        item = self.datamodel.get(pk)
        file = item.file.read()
        response = make_response(file)
        response.headers["Content-Disposition"] = "attachment; filename={0}".format(item.file.name)
        return response

    @expose('/img/<pk>')
    def img(self, pk):
        item = self.datamodel.get(pk)
        mime_type = item.image.content_type
        return Response(item.image.read(),mimetype=mime_type,direct_passthrough=True)

class TagsModelView(ModelView):
    datamodel = MongoEngineInterface(Tags)


class ContactChartView(GroupByChartView):
    datamodel = MongoEngineInterface(Contact)
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group': 'contact_group',
            'series': [(aggregate_count, 'contact_group')]
        },
        {
            'group': 'gender',
            'series': [(aggregate_count, 'gender')]
        }
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = MongoEngineInterface(Contact)

    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            'group': 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'contact_group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'contact_group')]
        }
    ]


appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(TagsModelView, "List Tags", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")

appbuilder.security_cleanup()

