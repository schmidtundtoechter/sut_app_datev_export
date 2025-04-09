app_name = "sut_app_datev_export"
app_title = "SUT App DATEV Export"
app_publisher = "ahmad900mohammad@gmail.com"
app_description = "SUT App DATEV Export"
app_email = "ahmad900mohammad@gmail.com"
app_license = "mit"

# Apps
# ------------------
# Document Events
doc_events = {
    "Employee": {
        "on_update": "sut_app_datev_export.sut_app_datev_export.server_scripts.employee.employee_on_update"
    }
}
# Custom fields
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", ["Employee-custom_for_next_export"]]
        ]
    }
]

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "sut_app_datev_export",
# 		"logo": "/assets/sut_app_datev_export/logo.png",
# 		"title": "SUT App DATEV Export",
# 		"route": "/sut_app_datev_export",
# 		"has_permission": "sut_app_datev_export.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sut_app_datev_export/css/sut_app_datev_export.css"
# app_include_js = "/assets/sut_app_datev_export/js/sut_app_datev_export.js"

# include js, css files in header of web template
# web_include_css = "/assets/sut_app_datev_export/css/sut_app_datev_export.css"
# web_include_js = "/assets/sut_app_datev_export/js/sut_app_datev_export.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sut_app_datev_export/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Employee" : "sut_app_datev_export/client_script/employee.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sut_app_datev_export/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sut_app_datev_export.utils.jinja_methods",
# 	"filters": "sut_app_datev_export.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sut_app_datev_export.install.before_install"
# after_install = "sut_app_datev_export.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sut_app_datev_export.uninstall.before_uninstall"
# after_uninstall = "sut_app_datev_export.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sut_app_datev_export.utils.before_app_install"
# after_app_install = "sut_app_datev_export.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sut_app_datev_export.utils.before_app_uninstall"
# after_app_uninstall = "sut_app_datev_export.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sut_app_datev_export.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sut_app_datev_export.tasks.all"
# 	],
# 	"daily": [
# 		"sut_app_datev_export.tasks.daily"
# 	],
# 	"hourly": [
# 		"sut_app_datev_export.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sut_app_datev_export.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sut_app_datev_export.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sut_app_datev_export.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sut_app_datev_export.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sut_app_datev_export.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sut_app_datev_export.utils.before_request"]
# after_request = ["sut_app_datev_export.utils.after_request"]

# Job Events
# ----------
# before_job = ["sut_app_datev_export.utils.before_job"]
# after_job = ["sut_app_datev_export.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sut_app_datev_export.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

