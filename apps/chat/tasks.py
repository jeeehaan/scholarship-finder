from huey.contrib.djhuey import task
from core.ai.prompt_manager import PromptManager
from core.methods import send_chat_message
from apps.chat.models import Conversation
from apps.scholarships.models import Scholarship
from core.ai.chroma import chroma_client, openai_ef
from core.ai.prompts import RAG_SYSTEM_PROMPT_SHORT, RAG_FALLBACK_SYSTEM_PROMPT



@task()
def process_chat(message, user):
    # Save user message
    Conversation.objects.create(message=message, role="user", user=user)

    try:
        collection = chroma_client.get_collection(name="scholarship_finder", embedding_function=openai_ef)

        # Query the collection
        content = collection.query(
            query_texts=[message],
            n_results=3,
        )
        
        scholarship_ids = []  
        # Print the raw content for debugging
        print("=" * 50)
        print("RAW CONTENT FROM CHROMADB:")
        print("=" * 50)
        print(f"Content type: {type(content)}")
        print(f"Content keys: {list(content.keys()) if hasattr(content, 'keys') else 'Not a dict'}")
        print(f"Full content: {content}")
        print("=" * 50)
        
        # Check if we got relevant results
        context_text = ""
        min_relevance_score = 0.3 # Adjust this threshold as needed
        
        if (content and 
            'documents' in content and 
            content['documents'] and 
            len(content['documents'][0]) > 0):
            
            print("DOCUMENTS FOUND:")
            print(f"Number of document lists: {len(content['documents'])}")
            print(f"Documents in first list: {len(content['documents'][0])}")
            for i, doc in enumerate(content['documents'][0]):
                print(f"Document {i+1}: {doc[:200]}..." if len(doc) > 200 else f"Document {i+1}: {doc}")
            print("-" * 30)
            
            # Check if results are relevant enough
            has_relevant_content = False
            
            if 'distances' in content and content['distances']:
                print("DISTANCE SCORES:")
                distances = content['distances'][0]
                print(f"Distances: {distances}")
                for i, distance in enumerate(distances):
                    similarity_score = 1 - (distance / 2)  # Normalize assuming max distance is 2
                    print(f"Document {i+1} - Distance: {distance:.4f}, Similarity: {similarity_score:.4f}")
                    if similarity_score >= min_relevance_score:
                        has_relevant_content = True
                        print(f"Document {i+1} meets relevance threshold!")
                print(f"Has relevant content: {has_relevant_content}")
                print("-" * 30)
            else:
                print("NO DISTANCE SCORES AVAILABLE")
                # If no distance scores, assume content might be relevant
                has_relevant_content = True
            
            if has_relevant_content:
                # Combine the retrieved documents
                documents = content['documents'][0]
                metadatas = content.get('metadatas', [[]])[0] if content.get('metadatas') else []
                for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                    print(f"Document {i+1}: {doc[:200]}...")
                    print(f"Metadata {i+1}: {metadata}")
                    
                    # Extract scholarship ID from metadata
                    if metadata and 'id' in metadata and i == 0:
                        scholarship_ids.append(str(metadata['id']))
                        print(f"Found scholarship ID: {metadata['id']}")
                        
                context_text = "\n\n".join([doc for doc in documents if doc.strip()])
                print("FINAL CONTEXT TEXT:")
                print(f"Context length: {len(context_text)} characters")
                print(f"Context preview: {context_text[:300]}...")
                print("-" * 30)
        else:
            print("NO DOCUMENTS FOUND OR EMPTY RESULTS")
            
        # Prepare system prompt based on context availability
        if context_text.strip():
            system_prompt = RAG_SYSTEM_PROMPT_SHORT.format(
                context=context_text)
            print("USING RAG SYSTEM PROMPT WITH CONTEXT")
        else:
            # Fallback system prompt for irrelevant questions
            system_prompt = RAG_FALLBACK_SYSTEM_PROMPT
            print("USING FALLBACK SYSTEM PROMPT (NO RELEVANT CONTEXT)")
        
        print("SYSTEM PROMPT PREVIEW:")
        print(f"{system_prompt[:200]}...")
        print("=" * 50)

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Get recent conversation history (excluding the current user message)
        chats = Conversation.objects.filter(user=user).exclude(
            message=message, role="user"
        ).order_by("-created_at")[:5]

        # Add conversation history in reverse order (oldest first)
        for chat in reversed(chats):
            messages.append({"role": chat.role, "content": chat.message})
        
        # Add current user message
        messages.append({"role": "user", "content": message})

        # Generate response
        p = PromptManager()
        p.set_messages(messages)
        res = p.generate()

    
        print("Generated response:", res)
        print("Context used:", bool(context_text.strip()))
        print("Messages sent to LLM:", p.get_messages())
        
        scholarship_data = []
        if scholarship_ids and len(scholarship_ids) > 0:
            for scholarship_id in scholarship_ids:
                try:
                    scholarship = Scholarship.objects.get(id=scholarship_id)
                    # Convert to dictionary with required fields
                    scholarship_dict = {
                        'id': scholarship.id,
                        'title': scholarship.title,
                        'description': scholarship.description,
                        # Add other fields as needed based on your Scholarship model
                    }
                    scholarship_data.append(scholarship_dict)
                except Scholarship.DoesNotExist:
                    print(f"Scholarship with ID {scholarship_id} not found")
                    continue

        # Save assistant response
        Conversation.objects.create(message=res, role="assistant", user=user)
        send_chat_message(res, scholarship_data)
        
    except Exception as e:
        print(f"Error in process_chat: {str(e)}")
        # Send error message to user
        error_message = "I'm sorry, I encountered an error while processing your question. Please try again."
        Conversation.objects.create(message=error_message, role="assistant", user=user)
        send_chat_message(error_message, [])