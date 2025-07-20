import os
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
        
        # Fallback responses for when API is unavailable
        self.fallback_responses = {
            "8-10": {
                "greeting": "Hi there! I'm TechPal, your friendly AI learning assistant! I'm here to help you learn about technology, science, and school subjects. What would you like to know today?",
                "computer": "Computers are like super-smart calculators that can follow instructions really fast! They have a brain (called a CPU) that thinks, memory to remember things, and can connect to the internet to learn new things. Think of them like having a very smart friend who can help you with homework, play games, and learn new things!",
                "internet": "The internet is like a huge library that connects computers all around the world! It's like having millions of books, videos, and games that you can access from anywhere. You can use it to learn new things, talk to friends, watch videos, and play games!",
                "coding": "Coding is like giving instructions to a computer in a special language it understands! It's like writing a recipe for a computer to follow. You can tell it to make games, websites, or even help with your homework!",
                "safety": "Staying safe online is super important! Always ask a parent or teacher before sharing personal information, never talk to strangers online, and if something makes you uncomfortable, tell a trusted adult right away. The internet is amazing, but we need to be smart about how we use it!",
                "math": "Math is everywhere in technology! Computers use math to solve problems, video games use math to create amazing graphics, and even your phone uses math to work. Let's make math fun by connecting it to things you love, like games and technology!",
                "science": "Science and technology go hand in hand! Scientists use computers to discover new things, create amazing inventions, and solve big problems. From robots to space exploration, science and technology make the world more exciting!",
                "default": "That's a great question! I love helping kids learn about technology and science. Let me think about that... Actually, I'm having a little trouble connecting to my brain right now, but I'd be happy to help you with questions about computers, the internet, coding, math, science, or staying safe online!"
            },
            "11-13": {
                "greeting": "Hello! I'm TechPal, your AI learning assistant. I'm here to help you explore technology, science, and school subjects in a fun and educational way. What topic interests you today?",
                "computer": "Computers are sophisticated machines that process information using binary code (1s and 0s). They have a central processing unit (CPU) that executes instructions, memory to store data temporarily, and storage to keep information permanently. Modern computers can perform billions of calculations per second!",
                "internet": "The internet is a global network of connected computers that allows information to be shared worldwide. It works through a system of servers, routers, and cables that transmit data packets. The World Wide Web, email, and online gaming all rely on this network infrastructure.",
                "coding": "Programming is the process of writing instructions for computers using programming languages like Python, JavaScript, or Scratch. It involves logical thinking, problem-solving, and creativity. You can create websites, games, apps, and even control robots!",
                "safety": "Online safety is crucial in today's digital world. Protect your personal information, use strong passwords, be cautious about what you share, and always verify information before believing it. Remember that not everything online is true or safe.",
                "math": "Mathematics is fundamental to technology! Algorithms, data analysis, cryptography, and artificial intelligence all rely on mathematical principles. Understanding math helps you think logically and solve complex problems in programming and science.",
                "science": "Technology and science are deeply interconnected. Scientific discoveries drive technological innovation, while technology enables new scientific research methods. From renewable energy to medical breakthroughs, this partnership shapes our future.",
                "default": "That's an interesting question! I'm designed to help students learn about technology, science, and academic subjects. I'm currently experiencing some connectivity issues, but I can help you with topics like programming, computer science, mathematics, physics, or digital literacy!"
            },
            "14-16": {
                "greeting": "Welcome to TechPal! I'm your AI learning assistant, designed to help you explore technology, science, and academic subjects. I can assist with programming concepts, scientific principles, mathematical problem-solving, and digital literacy. What would you like to learn about?",
                "computer": "Computers are complex systems that execute instructions through hardware and software components. The CPU processes data using transistors and logic gates, while memory hierarchies manage data access speeds. Operating systems coordinate hardware resources, and applications provide user functionality.",
                "internet": "The internet operates on a layered architecture including physical infrastructure (cables, routers), network protocols (TCP/IP), and application services. It enables global communication, data exchange, and distributed computing through client-server and peer-to-peer models.",
                "coding": "Software development involves multiple programming paradigms, data structures, algorithms, and software engineering principles. Modern development includes version control, testing frameworks, and deployment strategies. Programming skills are essential for automation, data analysis, and creating digital solutions.",
                "safety": "Cybersecurity encompasses protecting systems, networks, and data from digital attacks. This includes understanding encryption, authentication methods, secure coding practices, and recognizing social engineering threats. Digital literacy is crucial for navigating the modern information landscape.",
                "math": "Advanced mathematics underpins modern technology, including calculus for physics simulations, linear algebra for computer graphics, statistics for data science, and discrete mathematics for algorithms. Mathematical thinking is essential for problem-solving in technology and science.",
                "science": "Scientific methodology and technological innovation drive progress across disciplines. From quantum computing to biotechnology, understanding scientific principles enables technological advancement. Research methods, data analysis, and experimental design are crucial skills.",
                "default": "That's a sophisticated question! I'm designed to support learning in technology, computer science, mathematics, physics, and related fields. I'm currently experiencing some technical difficulties, but I can help you with programming concepts, scientific principles, mathematical problem-solving, or digital literacy topics."
            }
        }

    def _initialize_clients(self):
        """Initialize API clients if keys are available"""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

    def _get_fallback_response(self, message: str, age_group: str) -> str:
        """Get a fallback response when API is unavailable"""
        message_lower = message.lower()
        
        # Determine the appropriate age group
        if age_group not in self.fallback_responses:
            age_group = "11-13"  # Default to middle age group
        
        responses = self.fallback_responses[age_group]
        
        # Check for specific keywords to provide relevant responses
        if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
            return responses["greeting"]
        elif any(word in message_lower for word in ["computer", "pc", "laptop", "machine"]):
            return responses["computer"]
        elif any(word in message_lower for word in ["internet", "web", "online", "network"]):
            return responses["internet"]
        elif any(word in message_lower for word in ["code", "programming", "coding", "python", "javascript"]):
            return responses["coding"]
        elif any(word in message_lower for word in ["safe", "safety", "protect", "security"]):
            return responses["safety"]
        elif any(word in message_lower for word in ["math", "mathematics", "calculate", "equation"]):
            return responses["math"]
        elif any(word in message_lower for word in ["science", "scientific", "physics", "chemistry", "biology"]):
            return responses["science"]
        else:
            return responses["default"]

    def _prepare_messages(self, user_message: str, age_group: str) -> list:
        """Prepare messages for the LLM with system prompt"""
        system_prompt = f"""You are TechPal, a friendly and educational AI assistant designed specifically for children ages {age_group}. Your role is to help kids learn about technology, science, and school subjects in an engaging, age-appropriate way.

Key Guidelines:
- Use language and concepts appropriate for {age_group} year olds
- Be encouraging, patient, and supportive
- Explain complex topics in simple, relatable terms
- Use analogies and examples that kids can understand
- Focus on educational content and learning
- Always promote safe and responsible technology use
- Encourage curiosity and exploration
- Avoid any content that could be harmful or inappropriate for children

Subject Areas:
- Technology: computers, internet, coding, robotics, AI
- Science: physics, chemistry, biology, space, experiments
- School subjects: math, history, geography with tech connections
- Digital literacy: online safety, critical thinking, media literacy

Communication Style:
- Friendly and approachable
- Use emojis and visual language when helpful
- Ask follow-up questions to encourage engagement
- Provide step-by-step explanations
- Celebrate learning and effort

Safety Guidelines:
- Never provide personal information
- Encourage asking parents/teachers for help
- Promote healthy technology habits
- Focus on educational value

Response Framework:
1. Acknowledge the question with enthusiasm
2. Provide a clear, age-appropriate explanation
3. Use relatable examples or analogies
4. Ask a follow-up question to encourage learning
5. End with encouragement or a fun fact

Remember: You're here to make learning fun and accessible while keeping kids safe and engaged!"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

    def get_response(self, message: str, age_group: str = "11-13", provider: str = "openai") -> Optional[str]:
        """Get response from LLM with fallback to other providers"""
        try:
            # Try the requested provider first
            if provider == "openai" and self.openai_client:
                return self._get_openai_response(message, age_group)
            elif provider == "anthropic" and self.anthropic_client:
                return self._get_anthropic_response(message, age_group)
            
            # Fallback to other available provider
            if provider != "anthropic" and self.anthropic_client:
                return self._get_anthropic_response(message, age_group)
            elif provider != "openai" and self.openai_client:
                return self._get_openai_response(message, age_group)
            
            # If no providers available, use fallback response
            logger.warning("No LLM providers available, using fallback response")
            return self._get_fallback_response(message, age_group)
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            # Return fallback response on any error
            return self._get_fallback_response(message, age_group)

    def _get_openai_response(self, message: str, age_group: str) -> str:
        """Get response from OpenAI"""
        try:
            messages = self._prepare_messages(message, age_group)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _get_anthropic_response(self, message: str, age_group: str) -> str:
        """Get response from Anthropic"""
        try:
            system_prompt = self._prepare_messages(message, age_group)[0]["content"]
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate user message for safety and appropriateness"""
        # Basic validation
        if not message or len(message.strip()) == 0:
            return {"valid": False, "reason": "Message cannot be empty"}
        
        if len(message) > 1000:
            return {"valid": False, "reason": "Message too long (max 1000 characters)"}
        
        # Check for potentially inappropriate content
        inappropriate_words = [
            "password", "credit card", "social security", "address", "phone number",
            "personal information", "private", "secret"
        ]
        
        message_lower = message.lower()
        for word in inappropriate_words:
            if word in message_lower:
                return {
                    "valid": False, 
                    "reason": "Please don't share personal information. Ask a parent or teacher for help with personal matters."
                }
        
        return {"valid": True, "reason": "Message is appropriate"} 