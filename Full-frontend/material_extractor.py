import spacy
import re
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
    exit()

# Load a pre-trained sentence transformer model
try:
    print("Initializing Sentence Transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Sentence Transformer model loaded successfully.")
except Exception as e:
    print(f"Error loading Sentence Transformer model: {e}")
    model = None

# Expanded list of core materials to search for
CORE_KEYWORDS = [
    "Cement", "Aggregate", "Water", "Steel", "Concrete", "Admixture", 
    "Fly Ash", "Bitumen", "Mortar", "Brick", "Gravel", "Sand",
    "Reinforcement", "Formwork", "Shuttering", "Piers", "Abutments", "Columns",
    "Slabs", "Beams", "Walls", "Foundations", "Piles", "Couplers", "Jali",
    "Particle Board", "Damp Proof Course", "Slump Test", "Cube Test", 
    "Slag", "Pozzolana", "TMT Bars", "MS bars", "HYSD bars",
    "Galvanised Sleeves", "Polymer Block", "Waterproofing Materials", 
    "Bitumen felt", "Copper plate", "lignite", "mica", "shale", "clay",
    "pyrites", "coal", "sea shells", "organic impurities", "pentachlorophenol"
]


def find_nearest_heading(all_sentences, start_index):
    """
    Scans backwards from a given index to find the nearest preceding heading,
    with improved filtering to avoid generic headings.
    """
    heading_patterns = [
        r"^\d+\.\d+(?:\.\d+)*\s+.*",      # Matches "1.2.3 Section Title"
        r"^\(?[a-zA-Z]\)\s+.*",          # Matches "(a) Title"
        r"^TABLE\s+\d+\.\d+",           # Matches "TABLE 4.1"
        r"^(?!.*\b(?:MATERIAL|SPECIFICATIONS)\b)[A-Z\s\d\.\-]+$",  # Avoids generic all-caps
    ]
    for i in range(start_index, -1, -1):
        line = all_sentences[i]['text']
        # Skip very short, likely irrelevant lines
        if len(line.split()) < 2 and len(line) < 15:
            continue
        for pattern in heading_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return line.strip()
    return None

def create_semantic_index(sentences):
    """
    Creates a FAISS index for semantic search.
    """
    if not model:
        print("Sentence Transformer model not loaded. Skipping semantic index creation.")
        return None, None
    
    print("Creating semantic index...")
    try:
        # Generate embeddings for all sentences
        print("Generating sentence embeddings...")
        embeddings = model.encode([s['text'] for s in sentences], show_progress_bar=True)
        print("Sentence embeddings generated.")

        # Create a FAISS index
        print("Creating FAISS index...")
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings, dtype=np.float32))
        print("FAISS index created successfully.")
        return index, embeddings
    except Exception as e:
        print(f"Error creating semantic index: {e}")
        return None, None

def search_semantic_index(index, query, sentences, k=35):
    """ 
    Searches the FAISS index for the most similar sentences.
    """
    if not index or not model:
        return []
    
    print(f"Performing semantic search for query: '{query}' with k={k}")
    try:
        query_embedding = model.encode([query])
        distances, indices = index.search(np.array(query_embedding, dtype=np.float32), k)
        results = [sentences[i] for i in indices[0]]
        
        # Log the results
        with open("semantic_search_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"--- SEMANTIC SEARCH RESULTS FOR: '{query}' ---\n")
            for res in results:
                log_file.write(f"  - Page {res['page_number']}: {res['text']}\n")
            log_file.write("--- END SEARCH RESULTS ---\n\n")

        print(f"Semantic search found {len(results)} results.")
        return results
    except Exception as e:
        print(f"Error during semantic search: {e}")
        return []

def extract_information(document_data):
    """
    Extracts structured information about materials from processed document data using a hybrid approach.
    """
    print("Starting hybrid material information extraction...")
    
    # Smartly filter keywords to avoid redundant searches
    keywords = sorted(CORE_KEYWORDS, key=len, reverse=True)
    filtered_keywords = []
    for keyword in keywords:
        if not any(keyword in s for s in filtered_keywords):
            filtered_keywords.append(keyword)

    extracted_materials = []
    
    all_sentences = []
    for page_info in document_data:
        page_text = page_info['text']
        page_number = page_info['page_number']
        lines = page_text.split('\n')
        for line in lines:
            if line.strip():
                all_sentences.append({'text': line.strip(), 'page_number': page_number})

    # Create semantic index
    semantic_index, _ = create_semantic_index(all_sentences)

    processed_materials = set()

    for material_name in filtered_keywords:
        if material_name in processed_materials:
            continue
        
        print(f"Searching for material: {material_name}")
        
        # --- Hybrid Search: Keyword + Semantic ---
        found_indices = set()
        
        # 1. Keyword search
        for idx, sentence_info in enumerate(all_sentences):
            if re.search(r'\b' + re.escape(material_name) + r'\b', sentence_info['text'], re.IGNORECASE):
                found_indices.add(idx)

        # 2. Semantic search
        if semantic_index:
            semantic_results = search_semantic_index(semantic_index, material_name, all_sentences)
            for res in semantic_results:
                # Find the index of the result in the original list
                for idx, s in enumerate(all_sentences):
                    if s['text'] == res['text'] and s['page_number'] == res['page_number']:
                        found_indices.add(idx)
                        break

        if not found_indices:
            continue

        # --- Process found sections ---
        combined_references = []
        material_definitions = []
        other_info_list = []
        
        for idx in sorted(list(found_indices)):
            sentence_info = all_sentences[idx]
            sentence_text = sentence_info['text']
            page_number = sentence_info['page_number']

            # More focused context for extraction
            context_window = all_sentences[max(0, idx - 1):idx + 2]
            context = " ".join(s['text'] for s in context_window)

            heading = find_nearest_heading(all_sentences, idx)
            code_standard = extract_code_standard(sentence_text, page_number)
            
            # Combine heading and code standard intelligently
            reference = heading if heading else ""
            if code_standard:
                reference = f"{reference} – {code_standard}" if reference else code_standard
            
            # Add page number and ensure it's not a duplicate
            if reference:
                reference_with_page = f"{reference.strip()} (Page {page_number})"
                if reference_with_page not in combined_references:
                    combined_references.append(reference_with_page)

            # Extract other info from the focused context
            material_def = extract_material_type_definition(context, material_name)
            if material_def and material_def not in material_definitions:
                material_definitions.append(material_def)
            
            other_info = extract_other_info(context, material_name)
            if other_info and other_info not in other_info_list:
                other_info_list.append(other_info)
        
        # Filter out generic or less relevant references before formatting
        final_references = [
            ref for ref in combined_references if "CHAPTER" not in ref.upper() and len(ref) > 10
        ]
        
        formatted_references = "\n".join(
            f"{i+1}. {ref}" for i, ref in enumerate(final_references)
        ) if final_references else "No Information Available"

        extracted_materials.append({
            'Sl. No': '',
            'Material Name': material_name,
            'Test Name/Reference Code/Standard as per the given document (with reference page number)': formatted_references,
            'Specific Material Type/Material Definition': "; ".join(material_definitions) if material_definitions else "No Information Available",
            'Any other relevant information': "; ".join(other_info_list) if other_info_list else "No Information Available"
        })
        processed_materials.add(material_name)

    df = pd.DataFrame(extracted_materials)
    
    if not df.empty:
        df.drop_duplicates(subset=['Material Name'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df['Sl. No'] = df.index + 1
    
    print("Finished hybrid material information extraction.")
    return df

# This function is no longer needed as its logic is replaced by find_nearest_heading
def extract_test_name(context):
    return None


def extract_code_standard(context, page_number):
    """
    Extracts IS codes and standards from the given context, with page number.
    """
    is_code_pattern = r"IS\s+\d+(?:\s*\(Part\s*[\w\d\s]+\))?"
    matches = re.findall(is_code_pattern, context)
    if matches:
        # Return only the code, page number is added later if needed
        return '; '.join(sorted(set(match.strip() for match in matches)))
    return None

def extract_material_type_definition(context, material_name):
    """
    Extracts material type or definition from the context using spaCy and enhanced fallback rules.
    """
    # Try to find a definition using spaCy's dependency parsing
    doc = nlp(context)
    for sent in doc.sents:
        if re.search(r'\b' + re.escape(material_name) + r'\b', sent.text, re.IGNORECASE):
            for token in sent:
                if token.text.lower() == material_name.lower() and token.dep_ == 'nsubj':
                    if token.head.lemma_ in ['be', 'consist', 'include', 'mean', 'refer']:
                        definition = [child.text for child in token.head.children if child.dep_ not in ['punct', 'advmod']]
                        if definition:
                            return " ".join(definition)
    
    # Enhanced fallback rules with more specific patterns
    fallback_patterns = {
        "Fine Aggregate": r"(fine aggregate(?: is| shall be)?\s+.*?((?:passes through|retained on)\s+\d+\.\d+\s+mm\s+IS\s+sieve|conforming to IS \d+).*?(?=\.|$))",
        "Coarse Aggregate": r"(coarse aggregate(?: is| shall be)?\s+.*?((?:retained on)\s+\d+\.\d+\s+mm\s+IS\s+sieve|conforming to IS \d+).*?(?=\.|$))",
        "Cement": r"((?:Ordinary\s+)?Portland\s+cement(?: of\s+\d+\s+Grade)?|cement(?: is| shall be)?\s+.*?(?=\.|$))",
        "Water": r"(water(?: is| shall be)?\s+.*?(?=\.|$))",
        "Steel": r"(steel(?: is| shall be)?\s+.*?(?=\.|$)|reinforcement(?: is| shall be)?\s+.*?(?=\.|$))",
        "Concrete": r"(concrete(?: is| shall be)?\s+.*?(?=\.|$))",
        "Admixture": r"(admixture(?: is| shall be)?\s+.*?(?=\.|$))",
        "Brick": r"(brick aggregate(?: is| shall be)?\s+.*?(?=\.|$))",
        "Gravel": r"(gravel(?: is| shall be)?\s+.*?(?=\.|$))",
        "Sand": r"(sand(?: is| shall be)?\s+.*?(?=\.|$))",
        "Reinforcement": r"(reinforcement(?: is| shall be)?\s+.*?(?=\.|$))",
        "Formwork": r"(formwork(?: is| shall be)?\s+.*?(?=\.|$))",
        "Shuttering": r"(shuttering(?: is| shall be)?\s+.*?(?=\.|$))",
        "Piers": r"(piers(?: are| shall be)?\s+.*?(?=\.|$))",
        "Abutments": r"(abutments(?: are| shall be)?\s+.*?(?=\.|$))",
        "Columns": r"(columns(?: are| shall be)?\s+.*?(?=\.|$))",
        "Slabs": r"(slabs(?: are| shall be)?\s+.*?(?=\.|$))",
        "Beams": r"(beams(?: are| shall be)?\s+.*?(?=\.|$))",
        "Walls": r"(walls(?: are| shall be)?\s+.*?(?=\.|$))",
        "Foundations": r"(foundations(?: are| shall be)?\s+.*?(?=\.|$))",
        "Piles": r"(piles(?: are| shall be)?\s+.*?(?=\.|$))",
        "Couplers": r"(couplers(?: are| shall be)?\s+.*?(?=\.|$))",
        "Jali": r"(jali(?: is| shall be)?\s+.*?(?=\.|$))",
        "Particle Board": r"(particle board(?: is| shall be)?\s+.*?(?=\.|$))",
        "Damp Proof Course": r"(damp proof course(?: is| shall be)?\s+.*?(?=\.|$))",
        "Slump Test": r"(slump test(?: is| shall be)?\s+.*?(?=\.|$))",
        "Cube Test": r"(cube test(?: is| shall be)?\s+.*?(?=\.|$))",
        "Slag": r"(slag(?: is| shall be)?\s+.*?(?=\.|$))",
        "Pozzolana": r"(pozzolana(?: is| shall be)?\s+.*?(?=\.|$))",
        "TMT Bars": r"(TMT bars(?: are| shall be)?\s+.*?(?=\.|$))",
        "MS bars": r"(MS bars(?: are| shall be)?\s+.*?(?=\.|$))",
        "HYSD bars": r"(HYSD bars(?: are| shall be)?\s+.*?(?=\.|$))",
        "Galvanised Sleeves": r"(galvanised sleeves(?: are| shall be)?\s+.*?(?=\.|$))",
        "Polymer Block": r"(polymer block(?: is| shall be)?\s+.*?(?=\.|$))",
        "Waterproofing Materials": r"(waterproofing materials(?: are| shall be)?\s+.*?(?=\.|$))",
        "Bitumen felt": r"(bitumen felt(?: is| shall be)?\s+.*?(?=\.|$))",
        "Copper plate": r"(copper plate(?: is| shall be)?\s+.*?(?=\.|$))",
        "lignite": r"(lignite(?: is| shall be)?\s+.*?(?=\.|$))",
        "mica": r"(mica(?: is| shall be)?\s+.*?(?=\.|$))",
        "shale": r"(shale(?: is| shall be)?\s+.*?(?=\.|$))",
        "clay": r"(clay(?: is| shall be)?\s+.*?(?=\.|$))",
        "pyrites": r"(pyrites(?: is| shall be)?\s+.*?(?=\.|$))",
        "coal": r"(coal(?: is| shall be)?\s+.*?(?=\.|$))",
        "sea shells": r"(sea shells(?: are| shall be)?\s+.*?(?=\.|$))",
        "organic impurities": r"(organic impurities(?: are| shall be)?\s+.*?(?=\.|$))",
        "pentachlorophenol": r"(pentachlorophenol(?: is| shall be)?\s+.*?(?=\.|$))"
    }
    
    for mat, pattern in fallback_patterns.items():
        if mat.lower() == material_name.lower():
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                # Return the first non-empty matched group
                for group in match.groups():
                    if group:
                        return group.strip()

    # If still no definition, return a more informative message
    return f"No specific definition for {material_name} could be determined from the context."

def extract_other_info(context, material_name):
    """
    Extracts supplementary information, prioritizing tables, notes, and recommendations.
    """
    # If the context contains keywords like "Table", "Note", or "IS recommends", it's likely important.
    if "Table" in context or "Note" in context or "IS recommends" in context:
        return context.strip()
    return None


if __name__ == '__main__':
    # Example usage:
    # This part would typically be called by app.py after document processing.
    # For testing, you'd feed it data similar to what document_processor.py returns.

    # Dummy document data for testing
    dummy_doc_data = [
        {'page_number': 1, 'text': "This document discusses various materials. Cement shall be 43 Grade Ordinary Portland. It undergoes compressive strength test as per IS 4031 (Part 6)."},
        {'page_number': 2, 'text': "Fine Aggregate is used in concrete. Its gradation is as per Table 3.1. Silt content test is important. Steel reinforcement conforming to IS 1786. "},
        {'page_number': 3, 'text': "Water is a key component. Admixtures conforming to IS 9103 are used for workability. Concrete strength is tested by cube test. "}
    ]

    # extracted_df = extract_information(dummy_doc_data)
    # print(extracted_df.to_string())
    pass
