mds-cashbook-report
===================
Tryton module to add reports to cashbook.

Install
=======

pip install mds-cashbook-report

Requires
========
- Tryton 7.0

Info
====
Module cashbook_report adds the following evaluations:
- account balance as amount,
- price difference according to stock exchange price as amount,
- exchange rate difference in percent,
- current value according to stock exchange price,
- total yield

The displayed data is selected according to cash books,
types of cash books and cash books by category.
The presentation can be done as pie, bar and line chart.
For each evaluation, a dashboard view is also created,
so that you can display several evaluations at the same time.

Changes
=======

*7.0.11 - 18.07.2024*

- updt: optimize check of permissions

*7.0.10 - 13.01.2024*

- add: multiple data sources in evaluations

*7.0.9 - 10.12.2023*

- fix: selection of lines in dashboard-view

*7.0.8 - 06.12.2023*

- compatibility to Tryton 7.0
