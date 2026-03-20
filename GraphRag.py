"""
graphrag.py
A compact GraphRAG pipeline:
- extract triples from text using a local LLM (Ollama/Mistral example)
- build a NetworkX knowledge graph with provenance
- perform multi-hop retrieval (BFS-based)
- feed retrieved context into the LLM to answer questions

Usage: python graphrag.py
"""

import json
import time
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
# Try to import networkx and provide a helpful error if not installed
try:
    import networkx as nx
except ImportError:
    raise ImportError("networkx is not installed. Please install it with 'pip install networkx'.")
import logging
import re
from datetime import datetime

# Try to import LangChain-style classes from common variants (robust to different installs)
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    # LLM wrapper for Ollama - user earlier used langchain_ollama
    try:
        from langchain_ollama import ChatOllama
    except Exception:
        ChatOllama = None
except Exception:
    # fallback names used in the user's example
    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_ollama import ChatOllama
    except Exception:
        raise ImportError()
    
    

# ---------- Basic configuration ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graphrag")

# ---------- Data classes ----------
@dataclass
class Triple:
    head: str
    relation: str
    tail: str
    sentence: Optional[str] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: Optional[str] = None

    def to_dict(self):
        return asdict(self)

# ---------- Utilities ----------
def normalize_entity(name: str) -> str:
    """Simple normalization for entity labels."""
    if name is None:
        return ""
    name = name.strip()
    # Remove extra whitespace; keep case for readability but normalize multiple spaces
    name = re.sub(r"\s+", " ", name)
    # Optionally remove trailing punctuation:
    name = re.sub(r"^[\"'`]+|[\"'`]+$", "", name)
    return name

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

# ---------- LLM Extraction Chain ----------
def make_extraction_chain(llm):
    extract_prompt = PromptTemplate(
    template="""
    You are a strict JSON generator.

    Extract relationships from the text.

    Return ONLY valid JSON.
    NO explanation.
    NO text before or after.

    Output format:

    [
    {{"head": "Entity1", "relation": "relation", "tail": "Entity2"}}
    ]

    STRICT RULES:
    - Use double quotes ONLY
    - No trailing commas
    - No extra text
    - No comments
    - No markdown

    Text:
    {text}
    """,
        input_variables=["text"],
    )

    def clean_output(raw: str) -> str:
        # Remove markdown or unwanted wrappers
        raw = raw.strip()
        raw = raw.replace("```json", "").replace("```", "")
        return raw

    def extraction_chain_invoke(text: str) -> List[Dict[str, Any]]:
        prompt = extract_prompt.format_prompt(text=text).to_string()

        logger.info("Invoking LLM for triple extraction...")
        out = llm.invoke(prompt)

        raw = out.content if hasattr(out, "content") else str(out)

        # 🔍 DEBUG (important)
        # print("\nRAW OUTPUT:\n", raw)

        raw = clean_output(raw)

        # 🔥 Fix common issues
        raw = raw.replace("'", '"')  # single → double quotes

        # Try JSON
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except:
            pass

        # Extract JSON block
        match = re.search(r"\[.*\]", raw, re.S)
        if match:
            try:
                parsed = json.loads(match.group())
                return parsed
            except:
                pass

        # 🔥 LAST fallback (convert bullet text → JSON manually)
        triples = []
        lines = raw.split("\n")

        for line in lines:
            if " is " in line or " by " in line:
                parts = re.split(r"is|by", line)
                if len(parts) >= 2:
                    head = parts[0].strip(" -•")
                    tail = parts[1].strip()
                    triples.append({
                        "head": head,
                        "relation": "related to",
                        "tail": tail
                    })

        if triples:
            return triples

        logger.error("❌ Could not parse LLM output")
        return []

    return extraction_chain_invoke

# ---------- Graph Builder ----------
class KnowledgeGraph:
    def __init__(self, directed: bool = True):
        self.kg = nx.DiGraph() if directed else nx.Graph()

    def add_triples(self, triples: List[Triple]):
        for t in triples:
            h = normalize_entity(t.head)
            tail = normalize_entity(t.tail)
            if not h or not tail:
                continue
            # Add nodes (with metadata)
            self.kg.add_node(h)
            self.kg.add_node(tail)
            # Edge metadata
            edge_meta = {
                "relation": t.relation,
                "sentence": t.sentence,
                "source_id": t.source_id,
                "confidence": t.confidence,
                "timestamp": t.timestamp or now_iso()
            }
            self.kg.add_edge(h, tail, **edge_meta)

    def nodes(self):
        return list(self.kg.nodes)

    def edges(self):
        return list(self.kg.edges(data=True))

    def has_node(self, n):
        return self.kg.has_node(n)

    def shortest_paths_between(self, source: str, target: str, k: int = 3):
        # Return up to k shortest simple paths (by edge count)
        try:
            paths = list(nx.shortest_simple_paths(self.kg, source=source, target=target))
            return paths[:k]
        except Exception:
            return []

    def bfs_multi_hop(self, start: str, max_depth: int = 2, beam: int = 100) -> List[Tuple[List[str], List[Dict[str, Any]]]]:
        """
        BFS from start up to max_depth. Returns a list of (path_nodes, path_edges) with edges as dicts
        Paths are ordered by ascending path length.
        beam limits total paths returned.
        """
        if not self.kg.has_node(start):
            return []

        results = []
        queue = [([start], 0)]
        visited_paths: Set[Tuple[str, ...]] = set()

        while queue and len(results) < beam:
            path_nodes, depth = queue.pop(0)
            current = path_nodes[-1]
            if depth >= max_depth:
                # record this path (except trivial single-node path)
                if len(path_nodes) > 1:
                    # collect edges metadata
                    path_edges = []
                    for i in range(len(path_nodes) - 1):
                        e = self.kg.get_edge_data(path_nodes[i], path_nodes[i + 1])
                        path_edges.append({
                            "from": path_nodes[i],
                            "to": path_nodes[i + 1],
                            "meta": e
                        })
                    results.append((path_nodes, path_edges))
                continue

            # traverse successors and predecessors to allow back-and-forth walks
            neighbors = list(self.kg.successors(current)) + list(self.kg.predecessors(current))
            for nb in neighbors:
                new_path = tuple(path_nodes + [nb])
                if new_path in visited_paths:
                    continue
                visited_paths.add(new_path)
                queue.append((list(new_path), depth + 1))
                # Save paths that are >1 node
                if len(new_path) > 1:
                    path_edges = []
                    for i in range(len(new_path) - 1):
                        try:
                            e = self.kg.get_edge_data(new_path[i], new_path[i + 1])
                        except Exception:
                            e = None
                        path_edges.append({
                            "from": new_path[i],
                            "to": new_path[i + 1],
                            "meta": e
                        })
                    results.append((list(new_path), path_edges))
                    if len(results) >= beam:
                        break
        # dedupe by len then uniqueness
        unique = []
        seen = set()
        for p_nodes, p_edges in sorted(results, key=lambda x: len(x[0])):
            key = tuple(p_nodes)
            if key not in seen:
                unique.append((p_nodes, p_edges))
                seen.add(key)
        return unique

    def retrieve_context_text(self, start_entity: str, max_depth: int = 2, max_paths: int = 20) -> str:
        """
        Retrieve human-readable context by walking the graph. Return a concatenated context string.
        """
        walks = self.bfs_multi_hop(start_entity, max_depth=max_depth, beam=max_paths)
        sentences = []
        for nodes, edges in walks:
            for e in edges:
                meta = e["meta"] or {}
                relation = meta.get("relation")
                if not relation:
                    continue

                sentence = meta.get("sentence") or f"{e['from']} {relation} {e['to']}"
                sentences.append(sentence)
        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for s in sentences:
            if s not in seen:
                ordered.append(s)
                seen.add(s)
        return ". ".join(ordered) if ordered else ""

# ---------- Final RAG prompt builder ----------
def make_final_rag_chain(llm):
    final_prompt = PromptTemplate(
        template="""
Answer the question using ONLY the context below. If the answer is not present in the context, say "INSUFFICIENT_CONTEXT".

Context:
{context}

Question:
{question}

Answer:
""",
        input_variables=["context", "question"]
    )

    def rag_invoke(context: str, question: str):
        prompt = final_prompt.format_prompt(context=context, question=question).to_string() if hasattr(final_prompt, "format_prompt") else final_prompt.template.replace("{context}", context).replace("{question}", question)
        logger.info("Invoking LLM for final answer...")
        out = llm(prompt) if callable(llm) else llm.invoke(prompt)
        # guard: return string
        return out.content if hasattr(out, "content") else str(out)

    return rag_invoke

# ---------- Putting it together: Pipeline class ----------
class GraphRAGPipeline:
    def __init__(self, llm):
        self.llm = llm
        self.extract = make_extraction_chain(llm)
        self.rag = make_final_rag_chain(llm)
        self.kg = KnowledgeGraph()

    def extract_triples(self, text: str, source_id: Optional[str] = None) -> List[Triple]:
        raw_triples = self.extract(text)
        triples = []
        for i, item in enumerate(raw_triples):
            # flexible parsing with safety
            if isinstance(item, dict):
                head = item.get("head") or item.get("headin") or item.get("entity")
                relation = item.get("relation") or item.get("predicate")
                tail = item.get("tail") or item.get("object")

                # 🔥 FIX: Correct reversed relationships
                if relation:
                    relation = relation.lower()

                    # Fix "powers" relation direction
                    if relation == "powers":
                        # Assume AI model powers application, not vice versa
                        if "GPT" in tail and "ChatGPT" in head:
                            head, tail = tail, head

            else:
                head = relation = tail = None
            sentence = item.get("sentence") or None
            confidence = item.get("confidence") or None
            if (
                head and tail and relation and
                isinstance(head, str) and
                isinstance(tail, str) and
                isinstance(relation, str)
            ):
                t = Triple(
                    head=head,
                    relation=relation,
                    tail=tail,
                    sentence=sentence or None,
                    source_id=source_id or f"doc:unknown::{i}",
                    confidence=float(confidence) if confidence is not None else None,
                    timestamp=now_iso()
                )
                triples.append(t)
        logger.info(f"Extracted {len(triples)} triples.")
        return triples

    def ingest(self, text: str, source_id: Optional[str] = None):
        triples = self.extract_triples(text, source_id=source_id)
        self.kg.add_triples(triples)
        return triples

    def retrieve(self, entity: str, max_depth: int = 2, max_paths: int = 20) -> str:
        # normalize
        ent = normalize_entity(entity)
        if not self.kg.has_node(ent):
            logger.warning(f"Entity '{ent}' not found in KG.")
            return ""
        return self.kg.retrieve_context_text(ent, max_depth=max_depth, max_paths=max_paths)

    def ask(self, question: str, entity_hint: Optional[str] = None, max_depth: int = 3):
        # If entity_hint provided, use it. Otherwise, try to pick an entity by simple extraction from question
        if entity_hint:
            context = self.retrieve(entity_hint, max_depth=max_depth)
        else:
            # fallback: use the entire KG as context (careful with size)
            # better: try to extract a central entity from the question using a naive heuristic (quoted words or proper noun-like tokens)
            candidate = None
            m = re.search(r"\"(.+?)\"", question)
            if m:
                candidate = m.group(1)
            if candidate and self.kg.has_node(candidate):
                context = self.retrieve(candidate, max_depth=max_depth)
            else:
                # small safety: pick nodes that appear in question tokens
                tokens = [t for t in re.split(r"\W+", question) if t]
                found = [n for n in self.kg.nodes() if any(tok.lower() in n.lower() for tok in tokens)]
                if found:
                    context = self.retrieve(found[0], max_depth=max_depth)
                else:
                    # last resort: empty context or entire small graph
                    context = ""  # prefer empty to hallucination
        if not context:
            # avoid sending empty context; we will still call LLM but instruct to return INSUFFICIENT_CONTEXT
            final = self.rag("","")  # should not happen; but keep safe
            return "INSUFFICIENT_CONTEXT"

        answer = self.rag(context, question)
        return answer

# ---------- Optional: Neo4j export helper (stub) ----------
def export_to_neo4j(kg: KnowledgeGraph, uri: str, user: str, password: str):
    """
    If you want to scale the graph or use graph queries (Cypher), export to Neo4j.
    This function is a stub: add 'neo4j' package and implement connection/creation.
    """
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Neo4j python driver not installed. pip install neo4j to enable export.")
        return False

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # Add nodes and edges using Cypher
        for n in kg.nodes():
            session.run("MERGE (a:Entity {name: $name})", name=n)
        for u, v, data in kg.edges():
            session.run(
                "MATCH (a:Entity {name:$u}), (b:Entity {name:$v}) "
                "MERGE (a)-[r:RELATION {rel:$rel, sentence:$sentence, source:$source, confidence:$confidence}]->(b)",
                u=u, v=v, rel=data.get("relation"), sentence=data.get("sentence"),
                source=data.get("source_id"), confidence=data.get("confidence")
            )
    driver.close()
    return True

# ---------- Demo main using the user's example ----------
def load_local_mistral_llm():
    if ChatOllama is None:
        raise RuntimeError("ChatOllama not available")

    return ChatOllama(
        model="mistral",   # or "tinyllama" if phi3 crashes
        temperature=0,
        base_url="http://127.0.0.1:11434"
    )

def sample_demo():
    llm = load_local_mistral_llm()
    pipeline = GraphRAGPipeline(llm)

    print("Enter text (type END to finish):")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)

    text = " ".join(lines)

    print("\n🔹 Enter your question:\n")
    question = input()

    # Ingest
    triples = pipeline.ingest(text, source_id="user_input")

    print("\n📌 Extracted Triples:")
    for t in triples:
        print(t.to_dict())

    print("\n📊 KG Nodes:", pipeline.kg.nodes())

    entity_prompt = f"""
    Extract the main entity from this question:

    {question}

    Return only one entity name.
    """

    try:
        entity = llm.invoke(entity_prompt).content.strip()
        entity = entity.replace("The main entity is", "").strip()
    except:
        entity = None

    if not entity or entity not in pipeline.kg.nodes():
        for node in pipeline.kg.nodes():
            if node.lower() in question.lower():
                entity = node
                break

    if not entity:
        entity = pipeline.kg.nodes()[0] if pipeline.kg.nodes() else None

    print(f"\n Using entity: {entity}")

    context = pipeline.retrieve(entity, max_depth=5)
    print("\n Retrieved Context:\n", context)

    answer = pipeline.ask(question, entity_hint=entity, max_depth=5)
    print("\n Answer:\n", answer)


if __name__ == "__main__":
    sample_demo()