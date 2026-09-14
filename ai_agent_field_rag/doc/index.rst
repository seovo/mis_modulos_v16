==========================
AI Agent - Field RAG Sources
==========================

This module extends Odoo 19's AI Agent with a new source type that allows indexing
content from any model's text, char, or HTML fields for RAG (Retrieval-Augmented Generation).

Features
========

* Add model field content as AI agent sources
* Support for text, char, and HTML fields
* Domain filtering to select specific records
* Context fields for enriched semantic search
* Automatic sync via scheduled action
* Per-record source creation for semantic isolation

Dependencies
============

* base
* ai
* ai_app

Changelog
=========

Version 19.0.1.0.0
------------------

* Initial release
