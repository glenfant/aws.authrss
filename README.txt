===========
aws.authrss
===========

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

Installation
============

Production site
---------------

As usual in your ``zc.buildout`` configuration ::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      aws.authrss

Development site
----------------

Developers of ``aws.authrss`` should use this ::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      aws.authrss[test]
