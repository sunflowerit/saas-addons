======================
 Quick Demo Databases
======================

Deployment
==========

General requirements for deployment:

* You need a repository with custom odoo modules. At least one of the modules has to have ``saas_demo_title`` attribute in it's manifest (see below for details)
* Follow  instruction of `SaaS Base <../../saas/doc/index.rst>`__ module

One-server deployment
---------------------

Following commands deploy the system on 80 port. You may need to change that to configure https support or if 80 is already occupied by another program (e.g. nginx).

::

   # Clone prepared project. Note, that cloning odoo source could take some time.
   git clone TODO
   cd saas_demo

   # Make dockers
   make create

   # change port if needed
   #sed -i s/'80:80'/'8080:80'/  docker-compose.yml

   # set master password
   < /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32} > .adminpwd

   # init saas database
   # Tip: database name "apps" will used as a subdomain in your urls. If you
   # want to use another subdomain, change it here
   docker-compose run dodoo init -n apps -m saas_demo --no-demo

   # update admin password: set the same as masterpassword
   echo "env.ref('base.user_admin').password = '$(cat .adminpwd)'" | dc run dodoo run -d apps

   # Run!
   # Tip: to run in detach mode add "-d" after "up"
   docker-compose up odoo


Configuration
=============

Manifests
---------

Add following attributes to manifest of your modules

::

    "saas_demo_title": "Super-Duper Reminders",
    "saas_demo_addons": ["reminder_phonecall", "reminder_task_deadline", "reminder_hr_recruitment"],
    "saas_demo_addons_hidden": ["website"],

* ``saas_demo_title`` -- human-readable description of demonstrated modules
* ``saas_demo_addons`` -- list of additional modules to demostrate
* ``saas_demo_addons_hidden`` -- additional modules to install

SaaS Backend
------------

* Open menu ``[[ SaaS ]] >> Operators``
* Create or update an Operator:

  * **Repositories**

    * **Repo URL**
    * **Branch**
    * **Scan for demo** -- if not, it's used only as dependency

Usage
=====

* Go to ``[[ SaaS ]] >> SaaS Demo`` menu
* Create new record:

  * set **Operators** (for one server installation set *Same instance*)
  * set **Repositories** -- list of repositories with the modules to demonstrate and its dependencies
  * click ``[Save]``
* At the *SaaS Demo* Record click ``[Fetch repositories]``
*
* Open url: http://apps.127.0.0.1.nip.io/demo/itpp/saas-demo-test/13.0/web_login_background_test
* RESULT: you are authenticated in new demo instance

Publishing URL
==============

Live Preview at apps.odoo.com
-----------------------------

To activate ``[Live Preview]`` button at apps-store, add following attrubute to module manifest::

    "live_test_url": "http://apps.example.com/demo/itpp/saas-demo-test/13.0/web_login_background_test",


Custom Web Page
---------------

On publishing the demo url at some web page, don't forget to add ``rel="nofollow"`` attribute to your ``<a href="..."><a/>`` node. Otherwise `internet spiders <https://en.wikipedia.org/wiki/Web_crawler>`__ will create hundreds builds at your server by following the link.
