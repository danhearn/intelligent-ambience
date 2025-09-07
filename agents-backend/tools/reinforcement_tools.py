import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from tools.vector_memory_tools import vector_memory_instance

class ReinforcementLearning:
    def __init__(self):
        self.feedback_file = "reinforcement_feedback.json"
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self._load_feedback_data()
    
    def _load_feedback_data(self):
        """Load existing feedback data"""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                self.feedback_data = json.load(f)
        else:
            self.feedback_data = {
                "positive_feedback": {},
                "negative_feedback": {},
                "context_patterns": {},
                "music_preferences": {},
                "learning_stats": {
                    "total_interactions": 0,
                    "positive_feedback_count": 0,
                    "negative_feedback_count": 0,
                    "last_updated": datetime.now().isoformat()
                }
            }
    
    def _save_feedback_data(self):
        """Save feedback data to file"""
        self.feedback_data["learning_stats"]["last_updated"] = datetime.now().isoformat()
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def record_positive_feedback(self, context: str, environment: str, music_style: str, user_rating: float = 1.0):
        """Record positive feedback to reinforce successful patterns"""
        key = f"{context}_{environment}_{music_style}"
        
        if key not in self.feedback_data["positive_feedback"]:
            self.feedback_data["positive_feedback"][key] = {
                "count": 0,
                "total_rating": 0.0,
                "avg_rating": 0.0,
                "context": context,
                "environment": environment,
                "music_style": music_style,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        feedback = self.feedback_data["positive_feedback"][key]
        feedback["count"] += 1
        feedback["total_rating"] += user_rating
        feedback["avg_rating"] = feedback["total_rating"] / feedback["count"]
        feedback["last_seen"] = datetime.now().isoformat()
        
        # Also store in vector memory for semantic search
        vector_memory_instance.add_music_generation(
            context=context,
            environment=environment,
            music_prompt=f"Successful {music_style} music",
            user_feedback=f"Positive feedback: {user_rating}",
            location="",  # Could be extracted from context
            time_of_day=""  # Could be extracted from context
        )
        
        # Update learning stats
        self.feedback_data["learning_stats"]["positive_feedback_count"] += 1
        self.feedback_data["learning_stats"]["total_interactions"] += 1
        
        self._save_feedback_data()
        return f"Recorded positive feedback for {music_style} in {environment} (rating: {user_rating})"
    
    def record_negative_feedback(self, context: str, environment: str, music_style: str, reason: str = ""):
        """Record negative feedback to avoid unsuccessful patterns"""
        key = f"{context}_{environment}_{music_style}"
        
        if key not in self.feedback_data["negative_feedback"]:
            self.feedback_data["negative_feedback"][key] = {
                "count": 0,
                "reasons": [],
                "context": context,
                "environment": environment,
                "music_style": music_style,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        feedback = self.feedback_data["negative_feedback"][key]
        feedback["count"] += 1
        if reason and reason not in feedback["reasons"]:
            feedback["reasons"].append(reason)
        feedback["last_seen"] = datetime.now().isoformat()
        
        # Also store in vector memory for semantic search
        vector_memory_instance.add_music_generation(
            context=context,
            environment=environment,
            music_prompt=f"Unsuccessful {music_style} music",
            user_feedback=f"Negative feedback: {reason}",
            location="",  # Could be extracted from context
            time_of_day=""  # Could be extracted from context
        )
        
        # Update learning stats
        self.feedback_data["learning_stats"]["negative_feedback_count"] += 1
        self.feedback_data["learning_stats"]["total_interactions"] += 1
        
        self._save_feedback_data()
        return f"Recorded negative feedback for {music_style} in {environment} (reason: {reason})"
    
    def get_recommendation_weights(self, context: str, environment: str) -> Dict[str, float]:
        """Get weighted recommendations based on learned patterns"""
        weights = {}
        
        # Check positive feedback patterns
        for key, feedback in self.feedback_data["positive_feedback"].items():
            if (feedback["context"].lower() in context.lower() or 
                context.lower() in feedback["context"].lower()):
                if (feedback["environment"].lower() in environment.lower() or 
                    environment.lower() in feedback["environment"].lower()):
                    
                    music_style = feedback["music_style"]
                    # Weight based on frequency and average rating
                    weight = feedback["count"] * feedback["avg_rating"] * self.learning_rate
                    weights[music_style] = weights.get(music_style, 0) + weight
        
        # Check negative feedback patterns (reduce weights)
        for key, feedback in self.feedback_data["negative_feedback"].items():
            if (feedback["context"].lower() in context.lower() or 
                context.lower() in feedback["context"].lower()):
                if (feedback["environment"].lower() in environment.lower() or 
                    environment.lower() in feedback["environment"].lower()):
                    
                    music_style = feedback["music_style"]
                    # Reduce weight based on negative feedback frequency
                    penalty = feedback["count"] * 0.5
                    weights[music_style] = weights.get(music_style, 0) - penalty
        
        # Enhance with vector memory search
        vector_weights = self._get_vector_memory_weights(context, environment)
        for music_style, weight in vector_weights.items():
            weights[music_style] = weights.get(music_style, 0) + weight
        
        return weights
    
    def _get_vector_memory_weights(self, context: str, environment: str) -> Dict[str, float]:
        """Get additional weights from vector memory semantic search"""
        weights = {}
        
        # Search for similar successful patterns
        search_query = f"{context} {environment} successful music"
        try:
            results = vector_memory_instance.search_with_metadata(search_query, k=5)
            
            for doc, score in results:
                metadata = doc.metadata
                if metadata.get('user_feedback', '').startswith('Positive feedback'):
                    # Extract music style from the prompt
                    music_prompt = metadata.get('music_prompt', '')
                    if 'Successful' in music_prompt:
                        music_style = music_prompt.replace('Successful ', '').replace(' music', '')
                        # Weight based on similarity score
                        similarity_weight = (1 - score) * 0.3  # Convert distance to similarity
                        weights[music_style] = weights.get(music_style, 0) + similarity_weight
                        
        except Exception as e:
            print(f"Vector memory search error: {e}")
        
        return weights
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        return self.feedback_data["learning_stats"]
    
    def get_top_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing patterns"""
        patterns = []
        
        for key, feedback in self.feedback_data["positive_feedback"].items():
            score = feedback["count"] * feedback["avg_rating"]
            patterns.append({
                "context": feedback["context"],
                "environment": feedback["environment"],
                "music_style": feedback["music_style"],
                "score": score,
                "count": feedback["count"],
                "avg_rating": feedback["avg_rating"]
            })
        
        # Sort by score and return top patterns
        patterns.sort(key=lambda x: x["score"], reverse=True)
        return patterns[:limit]

# Global reinforcement learning instance
reinforcement_learning = ReinforcementLearning()

@tool
def record_positive_feedback(context: str, environment: str, music_style: str, user_rating: float = 1.0) -> str:
    """Record positive feedback to reinforce successful music patterns
        Args:
            context: The emotional/global context that worked well
            environment: The local environment description
            music_style: The music style that was successful
            user_rating: User rating from 0.0 to 1.0 (optional, defaults to 1.0)
        Returns:
            Confirmation that positive feedback was recorded
    """
    return reinforcement_learning.record_positive_feedback(context, environment, music_style, user_rating)

@tool
def record_negative_feedback(context: str, environment: str, music_style: str, reason: str = "") -> str:
    """Record negative feedback to avoid unsuccessful music patterns
        Args:
            context: The emotional/global context that didn't work
            environment: The local environment description
            music_style: The music style that was unsuccessful
            reason: Reason why it didn't work (optional)
        Returns:
            Confirmation that negative feedback was recorded
    """
    return reinforcement_learning.record_negative_feedback(context, environment, music_style, reason)

@tool
def get_recommendation_weights(context: str, environment: str) -> str:
    """Get weighted music recommendations based on learned patterns
        Args:
            context: The current emotional/global context
            environment: The current local environment description
        Returns:
            Weighted recommendations for music styles
    """
    weights = reinforcement_learning.get_recommendation_weights(context, environment)
    
    if not weights:
        return "No learned patterns found for this context. Using default recommendations."
    
    # Sort by weight
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    result = "Learned music recommendations (higher weight = more successful):\n"
    for music_style, weight in sorted_weights:
        if weight > 0:
            result += f"- {music_style}: {weight:.2f}\n"
        else:
            result += f"- {music_style}: {weight:.2f} (avoid - negative feedback)\n"
    
    return result

@tool
def get_learning_stats() -> str:
    """Get current reinforcement learning statistics
        Returns:
            Learning statistics and performance metrics
    """
    stats = reinforcement_learning.get_learning_stats()
    
    result = "Reinforcement Learning Statistics:\n"
    result += f"Total interactions: {stats['total_interactions']}\n"
    result += f"Positive feedback: {stats['positive_feedback_count']}\n"
    result += f"Negative feedback: {stats['negative_feedback_count']}\n"
    
    if stats['total_interactions'] > 0:
        success_rate = stats['positive_feedback_count'] / stats['total_interactions'] * 100
        result += f"Success rate: {success_rate:.1f}%\n"
    
    result += f"Last updated: {stats['last_updated']}\n"
    
    return result

@tool
def get_top_patterns(limit: int = 5) -> str:
    """Get top performing music patterns
        Args:
            limit: Maximum number of patterns to return
        Returns:
            Top performing patterns with scores
    """
    patterns = reinforcement_learning.get_top_patterns(limit)
    
    if not patterns:
        return "No patterns learned yet. Start providing feedback to build recommendations!"
    
    result = f"Top {len(patterns)} Music Patterns:\n\n"
    for i, pattern in enumerate(patterns, 1):
        result += f"{i}. {pattern['music_style']} for {pattern['environment']}\n"
        result += f"   Context: {pattern['context']}\n"
        result += f"   Score: {pattern['score']:.2f} (used {pattern['count']} times, avg rating: {pattern['avg_rating']:.2f})\n\n"
    
    return result

@tool
def search_similar_successful_patterns(context: str, environment: str, limit: int = 5) -> str:
    """Search vector memory for similar successful patterns using semantic search
        Args:
            context: The current emotional/global context
            environment: The current local environment description
            limit: Maximum number of results to return
        Returns:
            Similar successful patterns from vector memory
    """
    search_query = f"{context} {environment} successful music positive feedback"
    
    try:
        results = vector_memory_instance.search_with_metadata(search_query, k=limit)
        
        if not results:
            return f"No similar successful patterns found for '{context}' in '{environment}'"
        
        result = f"Found {len(results)} similar successful patterns:\n\n"
        for i, (doc, score) in enumerate(results, 1):
            metadata = doc.metadata
            similarity = 1 - score
            
            result += f"{i}. Context: {metadata.get('context', 'N/A')}\n"
            result += f"   Environment: {metadata.get('environment', 'N/A')}\n"
            result += f"   Music: {metadata.get('music_prompt', 'N/A')}\n"
            result += f"   Feedback: {metadata.get('user_feedback', 'N/A')}\n"
            result += f"   Similarity: {similarity:.2f}\n"
            result += f"   Date: {metadata.get('created_at', 'N/A')}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error searching vector memory: {str(e)}"

@tool
def learn_from_interaction(context: str, environment: str, music_prompt: str, user_feedback: str, rating: float = None) -> str:
    """Learn from a complete user interaction
        Args:
            context: The emotional/global context used
            environment: The local environment description
            music_prompt: The music generation prompt used
            user_feedback: User's feedback (positive/negative)
            rating: Numeric rating from 0.0 to 1.0 (optional)
        Returns:
            Confirmation of learning and recommendations
    """
    # Extract music style from prompt (simple extraction)
    music_style = music_prompt.split(',')[0].strip() if ',' in music_prompt else music_prompt
    
    feedback_lower = user_feedback.lower()
    
    if any(word in feedback_lower for word in ['good', 'great', 'love', 'perfect', 'amazing', 'excellent']):
        # Positive feedback
        result = reinforcement_learning.record_positive_feedback(
            context, environment, music_style, rating or 1.0
        )
        result += "\n\nThis pattern will be reinforced for future recommendations."
        
    elif any(word in feedback_lower for word in ['bad', 'hate', 'terrible', 'awful', 'wrong', 'dislike']):
        # Negative feedback
        result = reinforcement_learning.record_negative_feedback(
            context, environment, music_style, user_feedback
        )
        result += "\n\nThis pattern will be avoided in future recommendations."
        
    else:
        # Neutral feedback - still record for learning
        result = f"Recorded interaction: {music_style} for {environment} (neutral feedback)"
    
    # Get updated recommendations
    weights = reinforcement_learning.get_recommendation_weights(context, environment)
    if weights:
        result += "\n\nUpdated recommendations for similar contexts:"
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for music_style, weight in sorted_weights[:3]:
            if weight > 0:
                result += f"\n- {music_style}: {weight:.2f}"
    
    return result

def get_reinforcement_tools():
    """Get all reinforcement learning tools"""
    tools = [
        record_positive_feedback,
        record_negative_feedback,
        get_recommendation_weights,
        get_learning_stats,
        get_top_patterns,
        search_similar_successful_patterns,
        learn_from_interaction
    ]
    return tools
