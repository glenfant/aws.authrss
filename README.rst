===========
aws.authrss
===========

Access your Plone RSS feeds as authenticated user. This feature was inspired by
`Redmine <http://www.redmine.org/>`_.

Abstract
========

Actually, authenticated users in Plone site may read content that are not
available to anonymous users. But when subscribing to a Plone RSS feed they can
only view items that are available to anonymous users. Just because the RSS
readers such as Google Reader do not - and cannot - provide feature to provide
authentication cookie or header to authenticate on the feed URL.

``aws.authrss`` gives to the authenticated users a dedicated and private link to
the Plone RSS feeds. Such feeds provide all elements the user is entitled to
view, when authenticated in the Plone site with a browser, and of course,
relevant to the feed (Folder, Collection, ...)

Each user may have a private token he can change whenever he wants in his
personal preferences. This token is part of the query string of the
authenticated RSS field, and identifies the user **only** for the RSS feeds.

A control panel for site administrators gives the possibility to prune private
tokens of removed users.

Plays with
==========

Plone 4.1 only as this component is still a baby. Plone 4.0 support should not
be that difficult (contributors are welcome).

.. admonition::
   Conflicts with...

   `collective.blog.feeds <http://pypi.python.org/pypi/collective.blog.feeds>`_
   because both override the same viewlet, and there's no possible conflict
   resolution. Sorry.

Installation
============

Production site
---------------

As usual in your ``zc.buildout`` configuration: ::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      aws.authrss

Development site
----------------

The development package at Github comes with a suitable ``buildout.cfg``. See
`Links`_. You just need to clone that repoitory and play the usual ``python
bootstrap.py`` + ``bin/buildout``.

In ZMI
------

Don't forget to enable syndication in the ``portal_syndication`` object of your
site, and to check the ``Visible?`` checkbox of the
``portal_actions/object/syndication`` action of your site to have the control of
the per context syndication.

Upgrading
=========

Available upgrades may be executed from the ``portal_setup`` tool of your Plone
site in the **Upgrades** tab.

.. admonition::
   No upgrades with alpha releases

   For the first alpha versions, we shall not provide upgrade steps. You will
   need to reinstall the component. Stable versions coming after the first
   stable versions will come will all necessary upgrade steps.

Customization
=============

Integrators
-----------

``aws.authrss`` adds the authenticated RSS link with the
``portal_actions/document_actions/private_rss`` action in your site. You may
move this action (cut / paste) anywhere you want, as long as you keep its
properties unchanged.

You may hide the standard ``portal_action/document_actions/rss`` action that is
now useless.

Developers
----------

``aws.authrss`` comes with its own tokens manager that stores tokens in an
``OOBtree``. See the class ``aws.authrss.tokenmanager.DefaultTokenManager``.

You may provide your own tokens manager registering an utility that implements
``aws.authrss.interfaces.ITokenManager`` in your component's
``override.zcml``. Then install this local utility using a GenericSetup
``componentregistry.xml`` file like this one: ::

  <?xml version="1.0"?>
  <componentregistry>
    <utilities>
      <utility
        interface="aws.authrss.interfaces.ITokenManager"
        factory="my.component.tokenmanager.DefaultTokenManager"
       />
    </utilities>
  </componentregistry>

Credits
=======

This Plone component is sponsored by `Alter Way <http://www.alterway.fr/>`_

Links
=====

At github.com (contributors)
  https://github.com/glenfant/aws.authrss

At the cheeseshop (integrators)
  http://pypi.python.org/pypi/aws.authrss

Planned features
================

Do not assign tokens to users authenticated from an user folder that's not in
the Plone site (i.e a Zope root manager).

Add unit tests to KSS handlers (Any help appreciated).
