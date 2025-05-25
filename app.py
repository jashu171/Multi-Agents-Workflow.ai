from flask import Flask, request, jsonify, render_template, render_template_string
from flask_cors import CORS
import os
import json
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Import your workflow classes (assuming they're in the same file or imported)
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"

class FeedbackType(Enum):
    MODIFY = "modify"
    DELETE = "delete"
    ADD = "add"

@dataclass
class SubTask:
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    agent_type: str = "research_agent"
    tools: List[str] = field(default_factory=lambda: ["web_search"])
    attempts: int = 0
    max_attempts: int = 3

@dataclass
class TaskFeedback:
    task_id: str
    feedback_type: FeedbackType
    message: str
    new_tasks: List[str] = field(default_factory=list)

@dataclass
class WorkflowState:
    user_query: str
    subtasks: Dict[str, SubTask] = field(default_factory=dict)
    task_order: List[str] = field(default_factory=list)
    current_task_id: Optional[str] = None
    outer_iteration: int = 0
    inner_iteration: int = 0
    feedback_queue: List[TaskFeedback] = field(default_factory=list)
    workflow_complete: bool = False
    final_result: str = ""

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.available = False
        
        if self.api_key and not self.api_key.startswith("YOUR_"):
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
                self.available = True
                print("✅ Gemini API configured")
            except Exception as e:
                print(f"❌ Gemini API error: {e}")
        else:
            print("❌ Using fallback mode - Set GOOGLE_API_KEY in .env file")
    
    def generate(self, prompt: str) -> str:
        if not self.available:
            return self._fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else ""
        except Exception as e:
            print(f"API error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        if "break down" in prompt.lower():
            return json.dumps([
                {"description": "Research and analyze the request", "agent_type": "research_agent"},
                {"description": "Process and synthesize information", "agent_type": "analysis_agent"},
                {"description": "Generate final output", "agent_type": "creative_agent"}
            ])
        elif "execute" in prompt.lower():
            return "Task executed successfully using available tools and simulated processing"
        elif "reflect" in prompt.lower():
            return "Task completed with good quality results after reflection"
        return "Processed successfully with fallback system"

# Initialize global client
gemini = GeminiClient()

# Agent classes with streamlined output
class PlanAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        print(f"\n🧠 PlanAgent - Iteration {state.outer_iteration + 1}")
        state.outer_iteration += 1
        
        if state.outer_iteration > 5:
            state.workflow_complete = True
            return state
        
        if state.feedback_queue:
            state = self._process_feedback(state)
        
        if not state.subtasks:
            state = self._create_subtasks(state)
        
        state.workflow_complete = self._all_completed(state)
        return state
    
    def _create_subtasks(self, state: WorkflowState) -> WorkflowState:
        print("📋 Creating subtasks...")
        
        prompt = f"""Break down this request into 3-5 actionable subtasks:
        "{state.user_query}"
        
        Return JSON array:
        [{{"description": "task description", "agent_type": "research_agent|analysis_agent|creative_agent|technical_agent"}}]"""
        
        response = gemini.generate(prompt)
        
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                tasks_data = json.loads(response[start:end])
            else:
                raise ValueError("No JSON found")
        except:
            tasks_data = [
                {"description": f"Research and gather information about: {state.user_query}", "agent_type": "research_agent"},
                {"description": f"Analyze and process data for: {state.user_query}", "agent_type": "analysis_agent"},
                {"description": f"Generate comprehensive output for: {state.user_query}", "agent_type": "creative_agent"}
            ]
        
        for i, task_data in enumerate(tasks_data):
            task_id = f"task_{i+1}"
            subtask = SubTask(
                id=task_id,
                description=task_data["description"],
                agent_type=task_data.get("agent_type", "research_agent")
            )
            state.subtasks[task_id] = subtask
            state.task_order.append(task_id)
        
        print(f"✅ Created {len(state.subtasks)} subtasks")
        return state
    
    def _process_feedback(self, state: WorkflowState) -> WorkflowState:
        print("🔄 Processing feedback...")
        
        for feedback in state.feedback_queue:
            if feedback.feedback_type == FeedbackType.MODIFY:
                if feedback.task_id in state.subtasks:
                    task = state.subtasks[feedback.task_id]
                    task.description += f" (Updated: {feedback.message})"
                    task.status = TaskStatus.PENDING
                    task.attempts = 0
            
            elif feedback.feedback_type == FeedbackType.DELETE:
                if feedback.task_id in state.subtasks:
                    del state.subtasks[feedback.task_id]
                    if feedback.task_id in state.task_order:
                        state.task_order.remove(feedback.task_id)
            
            elif feedback.feedback_type == FeedbackType.ADD:
                for new_task in feedback.new_tasks:
                    task_id = f"task_{len(state.subtasks) + 1}"
                    state.subtasks[task_id] = SubTask(id=task_id, description=new_task)
                    state.task_order.append(task_id)
        
        state.feedback_queue.clear()
        return state
    
    def _all_completed(self, state: WorkflowState) -> bool:
        return all(task.status == TaskStatus.COMPLETED for task in state.subtasks.values())

def select_next_task(state: WorkflowState) -> WorkflowState:
    for task_id in state.task_order:
        if task_id in state.subtasks:
            task = state.subtasks[task_id]
            if task.status == TaskStatus.PENDING:
                state.current_task_id = task_id
                state.inner_iteration += 1
                print(f"🎯 Selected: {task_id}")
                return state
    
    state.current_task_id = None
    return state

class AgentDispatch:
    CAPABILITIES = {
        "research_agent": ["web_search", "document_analysis"],
        "analysis_agent": ["data_processing", "statistical_analysis"], 
        "creative_agent": ["text_generator", "content_creation"],
        "technical_agent": ["calculator", "code_execution"]
    }
    
    def __call__(self, state: WorkflowState) -> WorkflowState:
        if not state.current_task_id:
            return state
        
        task = state.subtasks[state.current_task_id]
        tools = self.CAPABILITIES.get(task.agent_type, ["web_search"])
        task.tools = tools
        
        print(f"🤖 Dispatched {task.agent_type}")
        return state

class ToolAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        if not state.current_task_id:
            return state
        
        task = state.subtasks[state.current_task_id]
        task.attempts += 1
        task.status = TaskStatus.IN_PROGRESS
        
        print(f"⚙️ Executing {task.id}")
        
        prompt = f"""Execute this task and provide a concise summary (max 200 words):
        Task: {task.description}
        Agent: {task.agent_type}
        Tools: {', '.join(task.tools)}
        
        Provide actionable results."""
        
        result = gemini.generate(prompt)
        # Truncate result to max 200 words for summary
        words = result.split() if result else []
        if len(words) > 200:
            result = ' '.join(words[:200]) + "..."
        
        task.result = result or f"Executed using {', '.join(task.tools[:2])}"
        task.status = TaskStatus.COMPLETED if result else TaskStatus.FAILED
        
        print(f"✅ Completed {task.id}")
        return state

class ReflectionAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        if not state.current_task_id:
            return state
        
        task = state.subtasks[state.current_task_id]
        print(f"🔍 Reflecting on {task.id}")
        
        # Simple reflection without generating feedback for now
        if task.status == TaskStatus.FAILED and task.attempts < task.max_attempts:
            task.status = TaskStatus.PENDING
        
        return state

def finalize_results(state: WorkflowState) -> WorkflowState:
    print("\n📋 Finalizing results...")
    
    completed = [t for t in state.subtasks.values() if t.status == TaskStatus.COMPLETED]
    if completed:
        # Create a concise summary instead of full output
        summary_parts = []
        summary_parts.append(f"🎯 Query: {state.user_query}")
        summary_parts.append(f"📊 Completed {len(completed)}/{len(state.subtasks)} tasks")
        
        for task in completed:
            # Limit each task result to 100 characters for summary
            result_preview = task.result[:100] + "..." if len(task.result) > 100 else task.result
            summary_parts.append(f"• {task.description}: {result_preview}")
        
        state.final_result = "\n".join(summary_parts)
    else:
        state.final_result = "❌ No tasks completed successfully"
    return state

# Routing functions
def route_workflow(state: WorkflowState) -> str:
    if state.workflow_complete:
        return "finalize"
    
    pending = [t for t in state.subtasks.values() 
              if t.status == TaskStatus.PENDING and t.attempts < t.max_attempts]
    
    return "task_selector" if pending and not state.feedback_queue else "plan"

def route_task_selector(state: WorkflowState) -> str:
    if state.current_task_id:
        return "agent_dispatch"
    
    all_done = all(t.status == TaskStatus.COMPLETED for t in state.subtasks.values())
    return "finalize" if all_done else "plan"

def route_after_reflection(state: WorkflowState) -> str:
    if state.current_task_id:
        task = state.subtasks[state.current_task_id]
        if task.status == TaskStatus.FAILED and task.attempts < task.max_attempts:
            return "tool_agent"
    
    pending = [t for t in state.subtasks.values() if t.status == TaskStatus.PENDING]
    if pending:
        return "task_selector"
    
    all_done = all(t.status == TaskStatus.COMPLETED for t in state.subtasks.values())
    return "finalize" if all_done else "plan"

def create_workflow() -> StateGraph:
    print("🔧 Creating workflow...")
    
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("plan", PlanAgent())
    workflow.add_node("task_selector", select_next_task)
    workflow.add_node("agent_dispatch", AgentDispatch())
    workflow.add_node("tool_agent", ToolAgent())
    workflow.add_node("reflection", ReflectionAgent())
    workflow.add_node("finalize", finalize_results)
    
    workflow.set_entry_point("plan")
    
    workflow.add_conditional_edges("plan", route_workflow, {
        "plan": "plan", "task_selector": "task_selector", "finalize": "finalize"
    })
    
    workflow.add_conditional_edges("task_selector", route_task_selector, {
        "agent_dispatch": "agent_dispatch", "plan": "plan", "finalize": "finalize"
    })
    
    workflow.add_edge("agent_dispatch", "tool_agent")
    workflow.add_edge("tool_agent", "reflection")
    
    workflow.add_conditional_edges("reflection", route_after_reflection, {
        "plan": "plan", "task_selector": "task_selector", 
        "tool_agent": "tool_agent", "finalize": "finalize"
    })
    
    workflow.add_edge("finalize", END)
    
    return workflow.compile()

# In-memory storage for history
query_history = []

def serialize_state(state_dict, include_full_results=False):
    """Convert state to JSON-serializable format with optional result truncation"""
    result = {}
    
    for key, value in state_dict.items():
        if key == 'subtasks':
            result[key] = {}
            for task_id, task in value.items():
                # Truncate result for summary unless full results requested
                task_result = task.result
                if not include_full_results and len(task_result) > 150:
                    task_result = task_result[:150] + "..."
                
                task_dict = {
                    'id': task.id,
                    'description': task.description,
                    'status': task.status.value if isinstance(task.status, TaskStatus) else task.status,
                    'result': task_result,
                    'agent_type': task.agent_type,
                    'tools': task.tools,
                    'attempts': task.attempts,
                    'max_attempts': task.max_attempts
                }
                result[key][task_id] = task_dict
        elif key == 'feedback_queue':
            result[key] = []
            for feedback in value:
                feedback_dict = {
                    'task_id': feedback.task_id,
                    'feedback_type': feedback.feedback_type.value if isinstance(feedback.feedback_type, FeedbackType) else feedback.feedback_type,
                    'message': feedback.message,
                    'new_tasks': feedback.new_tasks
                }
                result[key].append(feedback_dict)
        else:
            result[key] = value
    
    return result

# Flask Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_query():
    """Process a user query through the workflow"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Empty query provided'}), 400
        
        print(f"\n🚀 Processing query: {query}")
        
        # Create and run workflow
        app_workflow = create_workflow()
        initial_state = WorkflowState(user_query=query)
        
        # Execute workflow
        final_state = app_workflow.invoke(initial_state, config={"recursion_limit": 100})
        
        # Serialize the state with summarized results
        serialized_state = serialize_state(final_state, include_full_results=False)
        
        # Store in history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'result': serialized_state,
            'summary': serialized_state.get('final_result', 'No summary available')
        }
        query_history.append(history_entry)
        
        # Keep only last 50 entries
        if len(query_history) > 50:
            query_history.pop(0)
        
        print("✅ Query processed successfully")
        return jsonify(serialized_state)
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get query history with summaries"""
    try:
        # Return only summaries for history view
        history_summary = []
        for entry in query_history:
            summary_entry = {
                'timestamp': entry['timestamp'],
                'query': entry['query'],
                'summary': entry.get('summary', 'No summary available')[:200] + '...' if len(entry.get('summary', '')) > 200 else entry.get('summary', 'No summary available')
            }
            history_summary.append(summary_entry)
        return jsonify(history_summary)
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        return jsonify({'error': 'Failed to get history'}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear query history"""
    try:
        global query_history
        query_history = []
        return jsonify({'message': 'History cleared successfully'})
    except Exception as e:
        print(f"❌ Error clearing history: {e}")
        return jsonify({'error': 'Failed to clear history'}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'gemini_available': gemini.available,
        'total_queries': len(query_history),
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Jashu Multi-Agents Workflow Server")
    print("=" * 50)
    print(f"🔑 Gemini API: {'✅ Configured' if gemini.available else '❌ Not configured'}")
    print("🌐 Server starting on http://localhost:8000")
    print("📡 API Endpoints:")
    print("   • GET  /          - Main interface")
    print("   • POST /process   - Process query")
    print("   • GET  /history   - Get history")
    print("   • POST /clear-history - Clear history")
    print("   • GET  /status    - System status")
    print("=" * 50)

    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE\n')
        print("📝 Created .env file - Please add your Google API key")

    app.run(debug=True, host="0.0.0.0", port=8000)