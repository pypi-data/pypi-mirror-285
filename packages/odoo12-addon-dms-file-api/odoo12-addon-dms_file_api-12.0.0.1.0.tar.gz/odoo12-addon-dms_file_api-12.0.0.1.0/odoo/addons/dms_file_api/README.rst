============
DMS FILE API
============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

This module exposes an API-Key authenticated API to create dms files as attachments in partners and crm leads, focusing on the directory structure given by 
the inherited module "dms_res_model_root_directory".

**Table of contents**

.. contents::
   :local:

Configuration
=============

To give access to the API to a structure, go to

- Settings > Technical (debug mode) > Auth API Key
- Click create and select a user, save.
- Communicate the API-KEY to those in need to use the API.

Usage
=====

### Create files

Example of curl to create a dms file with two variables to fill:
- `API_KEY`: authorized key from the odoo server's API-KEY (see previows paragraph)
- `ODOO_URL`: target ODOO server's URL

Tickets can be created with either one of the following parameters, but not both:
- `partner_id`
- `crm_lead_id`

- "files" is an array of documents, each one with the following fields:
  - `filename`: name of the file
  - `content`: base64 encoded file

.. code:: bash

  CONTENT=$(base64 test_pdf.pdf)

  curl -X POST \
    -H "accept: application/json" \
    -H "api-key: $APIKEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg content "$CONTENT" \
          '{
              crm_lead_id: "New Ticket",
              category: "this is an API created ticket",
              attachments: [
                {
                  filename: "test_pdf.pdf",
                  content: $content,
                }
              ]
            }')" \
    "$ODOO_URL/api/documentation"



Known issues / Roadmap
======================

There are no issues for the moment.

Bug Tracker
===========

Bugs are tracked on `GitLab Issues <https://gitlab.com/somitcoop/erp-research/odoo-helpdesk/-/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* SomIT SCCL
* Som Connexio SCCL


Contributors
~~~~~~~~~~~~

* `SomIT SCCL <https://somit.coop>`_:

    * Álvaro García <alvaro.garcia@somit.coop>
    * José Robles <jose.robles@somit.coop>


* `Som Connexio SCCL <https://somconnexio.coop>`_:

    * Gerard Funosas <gerard.funosas@somconnexio.coop>


Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.