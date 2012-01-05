===========
aws.authrss
===========

Access your Plone RSS feeds as authenticated user.

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

Each user may have a private token he can change every times he wants in his
personal preferences. This token is part of the query string of the
authenticated RSS field, and identifies the user **only** for the RSS feeds.

A control panel for site administrators gives the possibility to prune private
tokens of removed users.

Plays with
==========

Plone 4.1 only as this component is still a baby. Plone 4.0 support should not
be that difficult (contributors are welcome).

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

Developers of ``aws.authrss`` should use this: ::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      aws.authrss[test]

Upgrading
=========

Available upgrades may be executed from the ``portal_setup`` tool of your Plone
site in the **Upgrades** tab.

Customization
=============

``aws.authrss`` comes with its own tokens manager that stores tokens in an
``OOBtree``. See the module ``aws.authrss.tokenmanager.DefaulttokenManager``.

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

At github.com
  https://github.com/glenfant/aws.authrss

At the cheeseshop
  http://pypi.python.org/pypi/aws.authrss

Planned features
================

Provide the same authenticated RSS feeds to search results but this requires to
override the standard ``search`` template machinery, and I hate overriding
templates. Patches are welcome.

Do not assign tokens to users authenticated from an user folder that's not in
the Plone site.

Add unit tests to KSS handlers (Any help appreciated).
