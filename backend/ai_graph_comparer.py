import os
import json
import asyncio
from typing import List, Dict, Any
from collections import defaultdict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key) if api_key else None
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

# ======================================================================================
# Core Logic: GraphRAG-Lite Comparator
# ======================================================================================


async def compare_articles_with_graph(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main entry point for GraphRAG comparison.
    1. Filter: Pick Top 2 articles per company.
    2. Extract: Extract (Entity -> Stance -> Target) triples per company.
    3. Normalize: Merge synonyms (e.g., 'Samsung' == 'Samsung Elec').
    4. Analyze: Compare stances on the same entities.
    """
    print("   🕸️ [GraphRAG] Starting Comparative Analysis...")

    # 1. Group & Filter (Top 2 per company to save tokens)
    company_groups = defaultdict(list)
    for art in articles:
        c = art.get("company_name", "Unknown")
        company_groups[c].append(art)

    selected_texts = {}  # { "Chosun": "Title... Content...", ... }
    for comp, arts in company_groups.items():
        # Sort by length and analytical keywords
        arts.sort(key=lambda x: len(x.get("contents", "")), reverse=True)
        top_arts = arts[:2]  # Pick Top 2

        combined_text = "\n".join([f"[{i+1}] {a.get('title')}\n{a.get('contents')}" for i, a in enumerate(top_arts)])
        selected_texts[comp] = combined_text

    # 2. Parallel Extraction
    # We define a helper to extract triples for one company
    tasks = [extract_triples(comp, text) for comp, text in selected_texts.items()]
    results = await asyncio.gather(*tasks)

    # results is a list of { "company": "A", "triples": [...] }
    all_triples_map = {r["company"]: r["triples"] for r in results}

    # 3. Entity Normalization
    # Collect all entities
    all_entities = set()
    for trips in all_triples_map.values():
        for t in trips:
            all_entities.add(t.get("subject"))
            all_entities.add(t.get("object"))

    entity_map = await normalize_entities(list(all_entities))

    # Apply normalization
    normalized_graph = defaultdict(list)  # { "CanonEntity": [ {company, predicate, original_entity} ] }

    for comp, trips in all_triples_map.items():
        for t in trips:
            subj = entity_map.get(t.get("subject"), t.get("subject"))
            # We focus on Subject-centric comparison for now
            normalized_graph[subj].append(
                {
                    "company": comp,
                    "predicate": t.get("predicate"),
                    "object": entity_map.get(t.get("object"), t.get("object")),
                    "sentiment": t.get("sentiment"),
                }
            )

    # 4. Generate Final Report
    report = await generate_graph_report(normalized_graph, selected_texts.keys())

    return report


# ======================================================================================
# Step 2: Extraction
# ======================================================================================
async def extract_triples(company: str, text: str) -> Dict[str, Any]:
    system_prompt = (
        "You are a Knowledge Graph Extractor. Extract key 'Entity-Relation-Entity' triples from the news text. "
        "Focus on the main political/economic actors and their specific actions or stances. "
        'Output JSON: { "triples": [ {"subject": "...", "predicate": "...", "object": "...", "sentiment": "positive/negative/neutral"} ] }'
    )
    user_prompt = f"""
    Press: {company}
    Text:
    {text[:3000]} (truncated)
    
    Extract 5-10 key semantic triples representing the press's coverage.
    """

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        data = json.loads(resp.choices[0].message.content)
        return {"company": company, "triples": data.get("triples", [])}
    except Exception as e:
        print(f"   ⚠️ [Graph] Extraction failed for {company}: {e}")
        return {"company": company, "triples": []}


# ======================================================================================
# Step 3: Normalization
# ======================================================================================
async def normalize_entities(entities: List[str]) -> Dict[str, str]:
    if not entities:
        return {}

    # Too many entities? Slice top 50 to save tokens based on simple heuristics if needed
    # For now, we assume manageable size (<100)
    entities_str = ", ".join(entities)

    system_prompt = (
        "You are an Entity Resolver. Group synonymous entities into a single canonical name. "
        "Map specific names to general representative names if they refer to the same person/org in this context. "
        'Output JSON: { "mapping": { "Variant": "Canonical", ... } }'
    )
    user_prompt = f"""
    Entities: {entities_str}
    
    Task: Return a mapping dictionary where keys are the input entities and values are their unified canonical names. 
    Only include pairs that need normalization. If an entity is already canonical, you can omit it.
    Example: {{ "Samsung Electronics": "Samsung", "Samsung": "Samsung", "Donald Trump": "Trump" }}
    """

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        data = json.loads(resp.choices[0].message.content)
        return data.get("mapping", {})
    except:
        return {}


# ======================================================================================
# Step 4: Reporting
# ======================================================================================
async def generate_graph_report(graph: Dict[str, List[Dict]], companies: List[str]) -> Dict[str, Any]:
    # Select Top 3 most discussed entities (keys with most list items)
    top_entities = sorted(graph.keys(), key=lambda k: len(graph[k]), reverse=True)[:5]

    # Serialize relevant subgraph
    graph_summary = ""
    for ent in top_entities:
        graph_summary += f"## Entity: {ent}\n"
        # Group by press to show contrast
        press_view = defaultdict(list)
        for edge in graph[ent]:
            press_view[edge["company"]].append(f"{edge['predicate']} -> {edge['object']} ({edge['sentiment']})")

        for press, views in press_view.items():
            graph_summary += f"  - {press}: {'; '.join(views)}\n"
        graph_summary += "\n"

    system_prompt = (
        "You are a News Analyst. Compare the viewpoints of different media outlets based on the provided Knowledge Graph data. "
        "Generate 3-5 sharp, insightful bullet points highlighting the differences in tone, focus, or interpretation."
        "Output MUST be in Korean."
        'Output JSON: { "media_comparison_bullets": [ "Bullet 1", "Bullet 2" ... ] }'
    )

    user_prompt = f"""
    Media Outlets Involved: {', '.join(companies)}
    
    Key Entity Analysis (Graph Data):
    {graph_summary}
    
    Task: Write a comparative analysis in Korean.
    
    Formatting Rules:
    1. **Language**: Strictly KOREAN.
    2. **Tone**: Formal polite style (Ends with '입니다', '합니다', '보입니다').
    3. **Variety**: Avoid repetitive use of '반면' (on the other hand). Use diverse conjunctions (e.g., '한편', '대조적으로', '이와 달리') or direct contrasts.
    
    Content Rules:
    1. Identify contradictions, different framings, or causal links (e.g., Press A links X to Y, while Press B links X to Z).
    2. Focus on *why* they differ (e.g., political stance, target audience, emphasis on economy vs security).
    3. Be specific about the entities and predicates used.
    """

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(resp.choices[0].message.content)
    except:
        return {"media_comparison_bullets": ["분석 실패: 데이터를 처리할 수 없습니다."]}
