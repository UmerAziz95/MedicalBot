"""
Prompt templates for the RAG system with enhanced context memory and medical knowledge
"""

class Prompts:
    """Collection of prompt templates for different use cases"""
    
    @staticmethod
    def generate_prompt(question: str, context: str, prompt_type: str = "basic", conversation_history: str = "") -> str:
        """
        Generate a prompt based on the type requested
        
        Args:
            question (str): User question
            context (str): Retrieved context
            prompt_type (str): Type of prompt (basic, medical, detailed)
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Generated prompt
        """
        if prompt_type == "medical":
            return Prompts.medical_rag_prompt(context, question, conversation_history)
        elif prompt_type == "detailed":
            return Prompts.detailed_rag_prompt(context, question, conversation_history)
        else:
            return Prompts.basic_rag_prompt(context, question, conversation_history)

    @staticmethod
    def generate_no_context_prompt(question: str, prompt_type: str = "basic", conversation_history: str = "") -> str:
        """
        Generate a prompt for when no context is available
        
        Args:
            question (str): User question
            prompt_type (str): Type of prompt
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Generated prompt
        """
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}
"""
        
        if prompt_type == "medical":
            return f"""You are a helpful medical assistant. The user is asking a question about a medical topic.

{history_section}
Even though I don't have specific medical documents that exactly match their query, you MUST:
1. Always respond to medical questions using your general medical knowledge
2. Be informative and educational when explaining medical terminology, processes, or concepts
3. NEVER say "I don't know" or "I couldn't generate a response" for medical topics
4. Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
5. Maintain consistent information with any previous responses in the conversation history
6. If the question refers to something mentioned in previous messages, address it directly

Question: {question}

Answer:"""
        elif prompt_type == "detailed":
            return f"""You are a helpful medical assistant with extensive knowledge. The user is asking a detailed question.

{history_section}
Even though I don't have specific documents that match their query, you MUST:
1. Provide a thorough and comprehensive response using your general knowledge
2. Be informative and educational when explaining medical terminology, processes, or concepts
3. NEVER say "I don't know" or "I couldn't generate a response" for medical topics
4. Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
5. Maintain consistent information with any previous responses in the conversation history
6. If the question refers to something mentioned in previous messages, address it directly

Question: {question}

Answer:"""
        else:
            return f"""You are a helpful medical assistant. The user is asking a question.

{history_section}
Even though I don't have specific documents that match their query, you MUST:
1. Respond using your general medical knowledge if the question is related to medical topics
2. Be informative and educational when explaining medical terminology, processes, or concepts
3. NEVER say "I don't know" or "I couldn't generate a response" for medical topics
4. Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
5. Maintain consistent information with any previous responses in the conversation history
6. If the question refers to something mentioned in previous messages, address it directly

Question: {question}

Answer:"""
    
    @staticmethod
    def basic_rag_prompt(context: str, question: str, conversation_history: str = "") -> str:
        """
        Basic RAG prompt template with conversation history
        
        Args:
            context (str): Retrieved context from vector database
            question (str): User question
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Formatted prompt
        """
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}

"""
        
        return f"""You are a helpful medical assistant. Use the context below to answer the question.
{history_section}
IMPORTANT INSTRUCTIONS:
1. If the context contains information relevant to the question, use it to provide an accurate answer
2. If the context does not contain information relevant to the question but the question is medical in nature, use your general medical knowledge to provide a helpful response
3. NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer
4. Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
5. Maintain consistency with information provided in the conversation history
6. If the question refers to terms or concepts mentioned in previous messages, explain them thoroughly

Context:
{context}

Question: {question}
Answer:"""
    
    @staticmethod
    def medical_rag_prompt(context: str, question: str, conversation_history: str = "") -> str:
        """
        Medical-focused RAG prompt template with conversation history
        
        Args:
            context (str): Retrieved context from vector database
            question (str): User question
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Formatted prompt
        """
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}

"""
        
        return f"""You are a knowledgeable medical assistant. Use the provided medical context to answer the question accurately.
{history_section}
Important guidelines:
- First, try to answer based on the provided medical context
- If the context doesn't contain relevant information but the question is medical in nature, use your general medical knowledge
- If the question asks about medical terminology or concepts mentioned in previous messages, provide a detailed explanation
- NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer
- Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
- Maintain consistency with information provided in the conversation history
- Provide clear, concise answers
- Do not provide medical diagnosis or treatment recommendations; provide factual information only

Medical Context:
{context}

Question: {question}
Answer:"""
    
    @staticmethod
    def detailed_rag_prompt(context: str, question: str, conversation_history: str = "") -> str:
        """
        Detailed RAG prompt template with more specific instructions and conversation history
        
        Args:
            context (str): Retrieved context from vector database
            question (str): User question
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Formatted prompt
        """
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}

"""
        
        return f"""You are an expert medical assistant specializing in document analysis and question answering.
{history_section}
Instructions:
1. Carefully read the provided context
2. First try to answer based solely on the information in the context
3. If the context doesn't contain relevant information but the question is medical in nature, use your general medical knowledge
4. If the question asks about medical terms, concepts or phrases mentioned in previous messages, provide a comprehensive explanation
5. NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer
6. Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare
7. Maintain consistency with information provided in the conversation history
8. Quote specific parts of the context when relevant
9. Be precise and factual
10. Do not provide medical diagnosis or treatment recommendations; provide factual information only

Context:
{context}

Question: {question}

Please provide a detailed answer:"""
    
    @staticmethod
    def file_analysis_prompt(file_text: str, question: str, prompt_type: str = "basic", conversation_history: str = "") -> str:
        """
        Prompt for file analysis with a user question and conversation history
        
        Args:
            file_text (str): Text extracted from the file
            question (str): User's question about the file
            prompt_type (str): Prompt type (basic, medical, detailed)
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Formatted prompt
        """
        # Determine if file_text contains direct processing hints
        is_direct_process = (
            "will be processed directly by the AI" in file_text.lower() or 
            "rather than extracting text" in file_text.lower()
        )
        
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}

"""
        
        base_prompt = f"""You are analyzing a document that was directly uploaded by the user. You must provide a clear, helpful response.
{history_section}
Document Content:
{file_text[:8000]}  # Limit text to avoid token limits

User Question: {question}

"""
        
        if is_direct_process:
            base_prompt += """
Note: This file has been marked for direct processing.
Focus on answering the user's question based on what might be in this type of file.
"""
        
        if prompt_type == "medical":
            base_prompt += """
Provide a medically focused analysis addressing the question. 
If the document doesn't clearly contain relevant medical information but the question is medical in nature, use your general medical knowledge to respond.
NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer.
Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare.
Do not provide medical advice or diagnosis. Be factual and precise.
Maintain consistency with information provided in the conversation history.
If the question refers to terminology or concepts mentioned in previous messages, provide a thorough explanation.
"""
        elif prompt_type == "detailed":
            base_prompt += """
Provide a comprehensive analysis of the document addressing the question.
If the document doesn't clearly contain relevant information but the question is medical in nature, use your general medical knowledge to respond.
NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer.
Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare.
Reference specific parts of the document when relevant. Be detailed and precise.
Maintain consistency with information provided in the conversation history.
If the question refers to terminology or concepts mentioned in previous messages, provide a thorough explanation.
"""
        else:
            base_prompt += """
Please provide a clear and helpful analysis addressing the question.
If the document doesn't clearly contain relevant information but the question is medical in nature, use your general medical knowledge to respond.
NEVER say "I don't know" or "I couldn't generate a response" for medical topics - always provide an informative answer.
Only say "I am a medical bot and can only assist with medical-related topics" if the question is completely unrelated to medicine or healthcare.
Focus on the information that's most relevant to answering the user's specific question.
Maintain consistency with information provided in the conversation history.
If the question refers to terminology or concepts mentioned in previous messages, provide a thorough explanation.
"""
            
        return base_prompt
    
    @staticmethod
    def file_summary_prompt(file_text: str, prompt_type: str = "basic", conversation_history: str = "") -> str:
        """
        Prompt for file summary without a specific question but with conversation history
        
        Args:
            file_text (str): Text extracted from the file
            prompt_type (str): Prompt type (basic, medical, detailed)
            conversation_history (str): Previous conversation between user and assistant
            
        Returns:
            str: Formatted prompt
        """
        # Determine if file_text contains direct processing hints
        is_direct_process = (
            "will be processed directly by the AI" in file_text.lower() or 
            "rather than extracting text" in file_text.lower()
        )
        
        history_section = ""
        if conversation_history:
            history_section = f"""
Conversation History:
{conversation_history}

"""
        
        base_prompt = f"""You are analyzing a document that was directly uploaded by the user. Provide a helpful summary of its content.
{history_section}
Document Content:
{file_text[:8000]}  # Limit text to avoid token limits

"""
        
        if is_direct_process:
            base_prompt += """
Note: This file has been marked for direct processing.
Focus on summarizing what might be in this type of file based on the limited information available.
"""
        
        if prompt_type == "medical":
            base_prompt += """
Please provide a comprehensive medical summary of this document.
Highlight key medical information, findings, conditions, treatments, or recommendations.
If the document doesn't clearly contain medical information, describe its general content and highlight any aspects that might be relevant to medical topics.
NEVER say "I don't know" or "I couldn't generate a response" - always provide an informative answer.
Do not provide medical advice or diagnosis. Be factual and precise.
Maintain consistency with information provided in the conversation history.
"""
        elif prompt_type == "detailed":
            base_prompt += """
Please provide a detailed analysis of this document.
Break down the document structure, highlight key information, main topics, and important details.
Include a comprehensive summary of the content, focusing on any medical or health-related aspects if present.
NEVER say "I don't know" or "I couldn't generate a response" - always provide an informative answer.
Maintain consistency with information provided in the conversation history.
"""
        else:
            base_prompt += """
Please provide a clear summary of this document.
Highlight key information and main topics covered, particularly any medical or health-related content.
Describe what type of document this appears to be and its general purpose.
NEVER say "I don't know" or "I couldn't generate a response" - always provide an informative answer.
Maintain consistency with information provided in the conversation history.
"""
            
        return base_prompt

# For backward compatibility
PromptTemplates = Prompts