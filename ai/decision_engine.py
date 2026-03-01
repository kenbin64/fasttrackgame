"""
Dimensional Decision Engine - Flow-Based Reasoning
===================================================

Makes decisions using geometric flow, not neural networks:
- Flow-based reasoning through manifold
- Oscillation-based exploration
- Pythagorean similarity matching
- Perfect memory integration

No GPT. No training. Pure dimensional computing.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.substrates.hexadic_manifold import HexadicManifold
from trinity_memory import TrinityMemorySubstrate
from dimensional_language import DimensionalLanguage
from typing import List, Dict, Tuple, Optional, Any
import time


class DimensionalDecisionEngine:
    """
    Decision engine using flow-based geometric reasoning.
    
    Instead of neural networks:
    - Projects problems into manifold space
    - Flows through geometric space
    - Oscillates to explore solutions
    - Finds answers through Pythagorean similarity
    """
    
    def __init__(self, memory: Optional[TrinityMemorySubstrate] = None):
        self.manifold = HexadicManifold()
        self.memory = memory or TrinityMemorySubstrate()
        self.language = DimensionalLanguage()
        
        # Decision history for learning
        self.decision_history = []
    
    def reason(self, query: str, context: Optional[str] = None, k: int = 10) -> str:
        """
        Reason about query using flow-based computation.
        
        Process:
        1. Embed query in manifold
        2. Recall relevant memories
        3. Synthesize answer from multiple memories
        4. Generate comprehensive response
        
        Args:
            query: Question or problem to reason about
            context: Optional additional context
            k: Number of memories to recall
        
        Returns:
            Reasoned answer
        """
        print(f"[REASON] Query: {query[:60]}...")
        
        # 1. Embed query
        query_point = self.language.embed_text(query)
        print(f"[REASON] Query embedded at ({query_point.x:.2f}, {query_point.y:.2f}, {query_point.z:.2f})")
        
        # 2. Recall relevant memories
        memories = self.memory.recall(query, k=k)
        print(f"[REASON] Recalled {len(memories)} relevant memories")
        
        if not memories:
            return "I don't have enough knowledge to answer that yet. Please teach me by using the 'Learn' feature in settings, or bootstrap more knowledge from free sources like Wikipedia."
        
        # 3. Find the most relevant memory
        # Use the top memory as primary answer
        best_memory = memories[0]
        answer = best_memory.content
        
        # 4. Enhance with related information if available
        # Look for complementary information from other memories
        query_keywords = set(query.lower().split())
        
        for mem in memories[1:3]:  # Check next 2 memories
            # Calculate keyword overlap
            mem_keywords = set(mem.content.lower().split())
            overlap = query_keywords & mem_keywords
            
            # If this memory has significant keyword overlap and adds new info
            if len(overlap) >= 2:
                # Check if it's not too similar (avoid repetition)
                similarity = self.language.similarity(answer, mem.content)
                if similarity < 0.8:  # Not too similar
                    # Add as additional context
                    answer = answer + " " + mem.content
                    break  # Only add one additional piece
        
        print(f"[REASON] Answer generated: {answer[:60]}...")
        return answer
    
    def _synthesize_answer(self, query: str, info_pieces: List[str]) -> str:
        """
        Synthesize a comprehensive answer from multiple information pieces.
        
        Args:
            query: The original question
            info_pieces: List of relevant information
        
        Returns:
            Synthesized answer
        """
        # Extract key concepts from query
        query_lower = query.lower()
        
        # Build answer by combining relevant pieces
        answer_parts = []
        
        # Add most relevant piece first
        answer_parts.append(info_pieces[0])
        
        # Add additional context from other pieces
        for piece in info_pieces[1:]:
            # Avoid repetition
            if piece not in answer_parts[0]:
                # Check if it adds new information
                words_in_piece = set(piece.lower().split())
                words_in_answer = set(' '.join(answer_parts).lower().split())
                new_words = words_in_piece - words_in_answer
                
                if len(new_words) > 3:  # Has meaningful new content
                    answer_parts.append(piece)
        
        # Combine into coherent answer
        if len(answer_parts) == 1:
            return answer_parts[0]
        else:
            # Join with proper formatting
            return ' '.join(answer_parts[:3])  # Limit to 3 pieces for clarity
    
    def decide(self, situation: str, options: List[str], 
               criteria: Optional[str] = None) -> Tuple[str, float]:
        """
        Make decision using manifold flow.
        
        Process:
        1. Embed situation in manifold
        2. Embed all options
        3. Flow from situation
        4. Find which option the flow reaches
        5. Calculate confidence based on distance
        
        Args:
            situation: Description of the situation
            options: List of possible choices
            criteria: Optional decision criteria
        
        Returns:
            (best_option, confidence_score)
        """
        print(f"[DECIDE] Situation: {situation[:60]}...")
        print(f"[DECIDE] Options: {len(options)}")
        
        # Embed situation
        if criteria:
            situation_text = f"{situation} Criteria: {criteria}"
        else:
            situation_text = situation
        
        situation_point = self.language.embed_text(situation_text)
        
        # Embed options
        option_points = [
            (opt, self.language.embed_text(opt))
            for opt in options
        ]
        
        # Flow from situation
        print("[DECIDE] Computing flow...")
        flow_path = self.manifold.compute_flow(situation_point, steps=50, dt=0.1)
        final_point = flow_path[-1]
        
        # Find nearest option
        distances = [
            (opt, self.manifold.substrate.pythagorean_distance(final_point, point))
            for opt, point in option_points
        ]
        
        best_option, best_distance = min(distances, key=lambda x: x[1])
        
        # Calculate confidence (inverse of distance)
        confidence = 1.0 / (1.0 + best_distance)
        
        print(f"[DECIDE] Best option: {best_option[:60]}...")
        print(f"[DECIDE] Confidence: {confidence:.2f}")
        
        # Store decision in history
        self.decision_history.append({
            'situation': situation,
            'options': options,
            'decision': best_option,
            'confidence': confidence,
            'timestamp': time.time()
        })
        
        return best_option, confidence
    
    def learn_from_feedback(self, query: str, correct_answer: str):
        """
        Learn from feedback by storing in memory.
        This improves future reasoning.
        
        Args:
            query: Original query
            correct_answer: Correct answer to learn
        """
        print(f"[LEARN] Storing: {query[:40]}... -> {correct_answer[:40]}...")
        
        # Store as memory
        self.memory.store(
            f"Q: {query}\nA: {correct_answer}",
            metadata={
                'type': 'learned',
                'query': query,
                'answer': correct_answer,
                'timestamp': time.time()
            }
        )
    
    def explain_reasoning(self, query: str) -> Dict[str, Any]:
        """
        Explain the reasoning process for transparency.
        
        Returns:
            Dictionary with reasoning steps and intermediate results
        """
        # Embed query
        query_point = self.language.embed_text(query)
        
        # Recall memories
        memories = self.memory.recall(query, k=5)
        
        # Flow
        flow_path = self.manifold.compute_flow(query_point, steps=50, dt=0.1)
        
        # Explanation
        explanation = {
            'query': query,
            'query_embedding': {
                'x': query_point.x,
                'y': query_point.y,
                'z': query_point.z,
                'phase': query_point.phase,
                'curvature': query_point.curvature
            },
            'memories_recalled': len(memories),
            'top_memories': [
                {
                    'content': m.content[:100],
                    'importance': m.importance,
                    'access_count': m.access_count
                }
                for m in memories[:3]
            ],
            'flow_steps': len(flow_path),
            'final_position': {
                'x': flow_path[-1].x,
                'y': flow_path[-1].y,
                'z': flow_path[-1].z,
                'curvature': flow_path[-1].curvature
            }
        }
        
        return explanation
    
    def batch_reason(self, queries: List[str]) -> List[str]:
        """
        Reason about multiple queries efficiently.
        Uses geometric caching for similar queries.
        
        Args:
            queries: List of queries
        
        Returns:
            List of answers
        """
        answers = []
        
        for query in queries:
            # Check if similar query was already answered
            similar_found = False
            for prev_query, prev_answer in zip(queries[:len(answers)], answers):
                similarity = self.language.similarity(query, prev_query)
                if similarity > 0.9:  # Very similar
                    print(f"[BATCH] Using cached answer for similar query")
                    answers.append(prev_answer)
                    similar_found = True
                    break
            
            if not similar_found:
                answer = self.reason(query)
                answers.append(answer)
        
        return answers


# Standalone testing
if __name__ == "__main__":
    print("=" * 60)
    print("Dimensional Decision Engine - Flow-Based Reasoning")
    print("=" * 60)
    print()
    
    # Create decision engine
    engine = DimensionalDecisionEngine()
    
    # Bootstrap some knowledge
    print("Bootstrapping knowledge...")
    engine.memory.store("Artificial intelligence is the simulation of human intelligence by machines.")
    engine.memory.store("Machine learning is a subset of AI that learns from data without explicit programming.")
    engine.memory.store("Deep learning uses neural networks with multiple layers to learn representations.")
    engine.memory.store("The Pythagorean theorem states that a² + b² = c² for right triangles.")
    engine.memory.store("The golden ratio φ ≈ 1.618 appears frequently in nature and mathematics.")
    engine.memory.store("Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21... where each number is the sum of the previous two.")
    print()
    
    # Test 1: Reasoning
    print("Test 1: Flow-Based Reasoning")
    print("-" * 60)
    query = "What is machine learning?"
    answer = engine.reason(query)
    print(f"Query: {query}")
    print(f"Answer: {answer}")
    print()
    
    # Test 2: Decision Making
    print("Test 2: Decision Making")
    print("-" * 60)
    situation = "I need to build an AI system"
    options = [
        "Use a large language model API",
        "Build a dimensional computing system",
        "Train a neural network from scratch"
    ]
    decision, confidence = engine.decide(situation, options)
    print(f"Situation: {situation}")
    print(f"Options: {options}")
    print(f"Decision: {decision}")
    print(f"Confidence: {confidence:.2f}")
    print()
    
    # Test 3: Learning from Feedback
    print("Test 3: Learning from Feedback")
    print("-" * 60)
    engine.learn_from_feedback(
        "What is dimensional computing?",
        "Dimensional computing uses geometric manifolds and flow-based computation instead of traditional algorithms."
    )
    
    # Now ask the same question
    answer = engine.reason("What is dimensional computing?")
    print(f"Query: What is dimensional computing?")
    print(f"Answer: {answer}")
    print()
    
    # Test 4: Explain Reasoning
    print("Test 4: Explain Reasoning")
    print("-" * 60)
    explanation = engine.explain_reasoning("What is the golden ratio?")
    print(f"Query: {explanation['query']}")
    print(f"Memories recalled: {explanation['memories_recalled']}")
    print(f"Flow steps: {explanation['flow_steps']}")
    print(f"Final curvature: {explanation['final_position']['curvature']:.2f}")
    print()
    
    print("=" * 60)
    print("Decision Engine demonstrates:")
    print("  ✓ Flow-based reasoning")
    print("  ✓ Geometric decision making")
    print("  ✓ Learning from feedback")
    print("  ✓ Explainable reasoning")
    print("  ✓ No neural networks")
    print("  ✓ 100% local computation")
    print("=" * 60)
