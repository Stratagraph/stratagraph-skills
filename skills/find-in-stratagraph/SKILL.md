---
name: find-in-stratagraph
description: >-
  Find and verify specific information in a connected Stratagraph project.
  Use when the user asks to find, look up, check, verify, or answer a focused
  question from Stratagraph, including a focused question about chronology or
  change. Common requests include "what do we know about X?", "what is
  current?", "who owns X?", "what did this person say?", "when did X
  change?", "find this node key", or questions about a fact, requirement,
  status, source, or decision. Search semantically to locate candidates, then
  read the full evidence. Use optional lineage context only after search and
  only when chronology helps. This skill is read-only. Do not use it for an
  exhaustive project history, importing sources, daily gathering, or writing
  documents to Stratagraph.
---

# Find information in Stratagraph

Answer a focused question from the connected Stratagraph project. Begin with semantic discovery unless the user supplies an exact node key. Read every node used in the answer in full, and cite every node key as a link. Lineage is optional chronological wayfinding, not a source of truth or currentness. Briefs are optional.

## Select the project safely

- Find attached Stratagraph tools by names ending in values such as `strata_search_nodes`. Full tool names may start with an MCP-generated identifier. Never assume a connector UUID, server URL, project key, or full tool name.
- If 1 Stratagraph connector is attached, use it. If several are attached, use the connector named by `strata_project`. If no connector is selected, ask which project to use before querying.
- If no Stratagraph connector is available, tell the user to connect the project's MCP server. Stop until the tools are available.
- Treat the live tool descriptions and input schemas as authoritative because tool parameters may change.
- Use only read tools. Never call `strata_post_document` or another write tool while following this skill.
- Read the project key from the MCP server instructions or tool descriptions. Do not infer it when the server provides it.
- Read the application origin from the attached MCP connector URL when it is visible. Keep only the scheme and host. If the connector URL is not visible, use `https://stratagraph.io`.

## Frame the lookup

Read the request and identify:

1. The fact or question to answer.
2. Any named document, date range, speaker, or source.
3. Whether chronology or change is needed to understand the answer.
4. Whether the request is a focused lookup or an exhaustive history. Use this skill only for the focused lookup.

Ask a question only when 2 or more reasonable scopes would produce different answers. Otherwise, use the narrowest reasonable scope and state it when helpful.

## Delegate the lookup to a subagent when possible

If the environment can spawn subagents and a subagent can reach this project's Stratagraph tools, run the lookup in 1 subagent instead of the main conversation. The full nodes and documents this skill reads are its context-heavy part, and the skill is read-only, so delegation keeps that payload out of the main context at no risk.

- Give the subagent the framed question and this skill to follow.
- The subagent's report must contain the exact returned node keys and the full node content behind every statement, including `occurred_at`, attribution, review status, and admission method when available. When the subagent explored lineage, the report must also carry the fence state, the event grouping of the claims it read, and any path or span truncation it saw. Never accept a paraphrase without keys: the report is the calling agent's only verification evidence, and every node key cited in the final answer comes from it.
- If subagents are unavailable, or they cannot reach the project's tools, follow the rest of this skill directly.

## Choose the first tool

| Question shape | Start with | What to do |
|---|---|---|
| Exact node key | `strata_get_node` | Fetch the known node directly. Do not search for it, except with 1 search on the node's topic when chronology is needed, because only a search response supplies the lineage fence. |
| Focused topic, fact, status, requirement, owner, chronology, or change | `strata_search_nodes` | Write 1 concise semantic query. Add a type filter only when the request supports it. Chronology still starts with search. |
| Named document, source, date, or speaker | `strata_list_documents` | Find the relevant documents. Then use `strata_get_document` or search with `document_ids` or `speaker`. |
| Named brief or explicit request for maintained synthesis | `strata_list_briefs`, then `strata_get_brief` | Use briefs only when they are available and clearly relevant. Continue without them when none exist. |
| Unfamiliar node types | `strata_get_graph_schema` | Read the live node taxonomy instead of guessing. |

For a question limited to a named source, use `strata_get_document` to inspect every returned extracted claim before declaring a gap. The document response contains claim snippets, not full claim bodies. Fetch each node used in the answer with `strata_get_node` or `strata_get_nodes`. If the document response returns `truncated: true`, state that the claim list is incomplete and do not claim that the document lacks a matching claim. For a question limited to a person, set `speaker` instead of only adding the person's name to the query.

## Read the evidence

Use `strata_search_nodes` to locate candidates. Treat `semantic_similarity` when supplied as relative proximity, not truth, confidence, relevance, or currentness. Never answer a substantive question from search snippets alone.

After a useful search:

- Fetch 1 clearly relevant candidate with `strata_get_node`.
- Fetch several relevant candidates in 1 `strata_get_nodes` call.
- Fetch the document when the answer depends on all claims extracted from that document. Then fetch every relevant node in full before citing it.
- Explore lineage only when the question benefits from chronology and the conditions below are met.

Read full results before running another search. Do not repeat a successful query with synonyms. Search again only to fill a specific gap, such as a named source, person, date, or term found in full node content. Stop when the evidence answers the question.

### Explore chronology conditionally

Search is always the discovery layer. Lineage is an optional follow-on when all of these are true:

- `strata_explore_lineage` is attached;
- the search response reports `lineage.state: available` and a non-null opaque `lineage.as_of_fence`;
- a useful result's `lineage_context.path_count` is greater than zero; and
- full chronological paths would help answer the user's question.

Call `strata_explore_lineage` with the exact returned node key and the response-level fence. Treat its returned membership claims as full evidence with provisional chronological context, then judge their relevance to the question.

- Read `paths` as bounded summaries of the relevant chronological paths. Each `path` reference is local to this response, `name` was assigned when the path was created, and `origin_context` records creation provenance and does not establish membership. A `span.complete: false` value means its counts cover only the readable prefix.
- Read membership claims from `page`, grouped oldest-to-newest by source event. Claims within one event are peers; their array order carries no chronology. `continues_before` or `continues_after` means that event crosses a page boundary.
- To page through the same full-path exploration, keep the same origin node and fence and add the returned cursor. Follow pages only until the evidence answers the question or is no longer relevant. Do not expand chronology automatically.
- State the limitation when `path_count_basis` is `lower_bound`, `paths_truncated` is true, a span is incomplete, or `continuation.members_truncated` is true.

Fall back immediately to semantic search and document retrieval when the lineage tool is absent, lineage is unavailable, the fence is null, the useful result has no paths, or exploration returns `expired`. On expiry, run `strata_search_nodes` again only if chronology is still needed; use the new response and fence. Never reuse an expired fence.

Lineage membership, path names, origin context, and absence are provisional. They do not establish truth, currentness, completeness, contradiction, or relevance, and they do not hide, invalidate, or supersede any node.

## Check the answer

A node's existence in the project does not establish that it is relevant, true, or current. Describe conclusions as what the project records, not as externally verified truth unless separate evidence verifies them.

- Base each factual statement on full node or document content, not on similarity rank or lineage position.
- For current-state questions, compare the full claims, `occurred_at`, `occurred_at_basis` when supplied, attribution, `review`, `admission_method`, and contradictions visible in the content. State any remaining uncertainty. MCP chronology cannot certify an authoritative current head.
- Keep the source or event date from `occurred_at` when present. `document_date` is source context, not a promise of precise event time; `record_created` is the fallback for a documentless node. Do not silently replace either with another timestamp.
- Attribute a statement to a person only when the node or source names that speaker or author.
- Never treat the newest returned claim or the end of a lineage path as current merely because it is newest or last.
- When `admission_method` is `import` and `review` is `unreviewed`, say that the claim was imported and has not been human-reviewed when that status affects trust. Do not describe it as confirmed current state.
- Only when `admission_method` is absent, treat the legacy `review` value `imported` as an imported, unreviewed claim and apply the same caution.
- Remember that semantic search returns only the highest-ranked candidates. It does not inspect every node, so a missing result does not prove that the project lacks the information.

A recently posted node may still be waiting for search indexing. Say so when that could explain an empty result. If the document is known, use `strata_get_document`. Otherwise, run at most 1 more search with a different document, speaker, date, or specific term. Then name what you searched and the remaining limitation.

## Answer with linked node keys

Lead with the answer. Link every displayed node key to `{origin}/projects/{project_key}/nodes/{node_key}`.

Use Markdown links with the exact returned key as the label. For example: `The launch target moved to September [PROJ-142](https://stratagraph.io/projects/PROJ/nodes/PROJ-142).`

Include only what helps the user judge the answer:

- the document, speaker, or date scope
- relevant chronology or a conflicting recorded statement
- any relevant review note
- any evidence gap

Never display a bare node key in the user-facing answer. Never invent or reconstruct a node key. Do not describe the tool calls unless the user asks. When the answer is not in the returned matches, say, “I didn't find this in the returned matches.” Claim only that a specific document lacks an extracted claim after retrieving the document and confirming that `truncated` is `false`.
