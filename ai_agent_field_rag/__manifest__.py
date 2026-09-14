# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "AI Agent - Field RAG Sources",
    'version': '19.0.1.0.0',
    'category': 'Productivity/AI',
    'summary': '''Add model field content as AI agent sources for RAG.
    rag, retrieval augmented generation, vector search, semantic search, embeddings, vector database, vector store,
    ai, artificial intelligence, llm, large language model, ai agent, ai assistant, ai copilot, ai bot, chatbot,
    knowledge base, knowledge management, knowledge retrieval, document retrieval, content indexing, enterprise search,
    context retrieval, intelligent search, smart search, ai search, natural language search, nlp, natural language processing,
    odoo ai, odoo rag, odoo vector, odoo embeddings, odoo knowledge base, odoo ai agent, odoo llm, discuss ai,
    chatgpt, claude, gemini, openai, anthropic, google ai, gpt, gpt-4, gpt-5,
    project tasks, helpdesk tickets, crm leads, sale orders, custom fields, text fields, html fields,
    domain filtering, context fields, metadata enrichment, record indexing, content sync, automatic sync,
    ai data source, ai context, ai memory, ai knowledge, grounding, ai grounding,
    langchain, llamaindex, pinecone, chromadb, weaviate, qdrant,
    odoo19, odoo 19''',
    'description': """
AI Agent Field RAG Sources
==========================

This module extends Odoo's AI Agent capabilities by allowing users to add
text content from any model's fields as AI agent sources.

Features:
---------
* Select any model and text field to use as RAG source content
* Support for text, char, and HTML fields
* Domain filtering to select specific records
* Context fields to enrich content with metadata (stage, dates, assignee, etc.)
* Automatic content sync with pull-based updates
* Per-record source creation for semantic isolation
* Record count guidance for optimal RAG performance

Semantic Search Optimization:
-----------------------------
Each indexed source includes a structured header for optimal vector search:
* Record Type (model name) - enables queries like "project tasks"
* Record ID - enables queries like "task 123"
* Record Name (display_name) - enables queries by record name

Context fields enrich semantic matching, allowing queries like:
* "Tasks assigned to John" (if user_id is a context field)
* "High priority tickets" (if priority is a context field)
* "Tasks in the Done stage" (if stage_id is a context field)

Use Cases:
----------
* Project task descriptions as AI sources
* Helpdesk ticket messages as knowledge base
* CRM lead notes and communications
* Sale order notes
* Any model's text/HTML content
    """,
    'depends': ['base', 'ai', 'ai_app'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/ai_field_rag_config_views.xml',
        'views/ai_agent_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_agent_field_rag/static/src/components/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'author': 'Codemarchant',
    'website': 'https://codemarchant.com',
    'support': 'support@codemarchant.com',
    'license': 'OPL-1',
    'price': 0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
