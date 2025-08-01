#!/usr/bin/env python3
"""Remove duplicate tools, keeping the best content version."""

import os
import re
from pathlib import Path
from collections import defaultdict

def score_content_quality(content):
    """Score content quality based on various factors."""
    score = 0
    
    # Extract body content (after frontmatter)
    parts = content.split('---', 2)
    if len(parts) < 3:
        return 0
    
    body = parts[2].strip()
    
    # Positive signals for rich, human-written content
    # Longer content is generally better
    score += len(body) / 100
    
    # Check for varied paragraph lengths (not blocky)
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
    if len(paragraphs) > 3:
        lengths = [len(p) for p in paragraphs]
        variance = max(lengths) - min(lengths)
        if variance > 200:  # Good variation in paragraph lengths
            score += 50
    
    # Check for natural language patterns
    # Good: contractions, varied sentence starters
    if re.search(r"\b(it's|don't|won't|can't|they're|you're|we're)\b", body, re.I):
        score += 20
    
    # Check for specific, detailed features
    if re.search(r"## Key Features", body) and body.count('•') > 5:
        score += 30
    
    # Check for comparison section
    if re.search(r"## How It Compares", body):
        score += 40
    
    # Check for pros and cons
    if re.search(r"## Pros and Cons", body):
        score += 30
    
    # Penalize AI-obvious patterns
    # Repetitive sentence structures
    if body.count("It offers") > 2 or body.count("It provides") > 2:
        score -= 20
    
    # Generic AI phrases
    ai_phrases = [
        "comprehensive solution",
        "powerful tool",
        "seamless integration",
        "robust platform",
        "cutting-edge",
        "revolutionary",
        "game-changing",
        "state-of-the-art",
        "innovative solution"
    ]
    for phrase in ai_phrases:
        if phrase.lower() in body.lower():
            score -= 10
    
    # Check for specific examples and use cases
    if re.search(r"\b(for example|such as|specifically|particularly)\b", body, re.I):
        score += 15
    
    # Check for natural transitions
    transitions = ["however", "although", "while", "despite", "meanwhile", "furthermore"]
    for trans in transitions:
        if trans in body.lower():
            score += 5
    
    return score

def process_duplicates():
    """Process all duplicates and keep the best versions."""
    
    # First, find all duplicates
    content_dir = Path('content/categories')
    tool_files = defaultdict(list)
    
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                tool_name = file[:-3]
                full_path = os.path.join(root, file)
                tool_files[tool_name].append(full_path)
    
    # Find duplicates
    duplicates = {name: paths for name, paths in tool_files.items() if len(paths) > 1}
    
    print(f"Processing {len(duplicates)} duplicate tools...")
    
    removed_count = 0
    kept_files = []
    
    for tool_name, paths in duplicates.items():
        # Score each version
        scores = []
        for path in paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                score = score_content_quality(content)
                scores.append((score, path, content))
            except Exception as e:
                print(f"Error reading {path}: {e}")
                scores.append((0, path, ""))
        
        # Sort by score (highest first)
        scores.sort(reverse=True, key=lambda x: x[0])
        
        # Keep the best one
        best_score, best_path, best_content = scores[0]
        kept_files.append((tool_name, best_path, best_score))
        
        print(f"\n{tool_name}:")
        print(f"  Keeping: {Path(best_path).relative_to(content_dir)} (score: {best_score:.1f})")
        
        # Remove the others
        for score, path, content in scores[1:]:
            print(f"  Removing: {Path(path).relative_to(content_dir)} (score: {score:.1f})")
            try:
                os.remove(path)
                removed_count += 1
            except Exception as e:
                print(f"  Error removing {path}: {e}")
    
    print(f"\n=== DEDUPLICATION COMPLETE ===")
    print(f"Removed {removed_count} duplicate files")
    print(f"Kept {len(kept_files)} best versions")
    
    # Show some examples of kept files
    print("\n=== TOP QUALITY KEPT FILES ===")
    kept_files.sort(key=lambda x: x[2], reverse=True)
    for tool_name, path, score in kept_files[:10]:
        print(f"{tool_name}: {Path(path).relative_to(content_dir)} (score: {score:.1f})")

if __name__ == '__main__':
    process_duplicates()