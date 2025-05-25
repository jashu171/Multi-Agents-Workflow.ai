import os
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

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
            print("❌ Using fallback mode")
    
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
            return "Task executed successfully using available tools"
        elif "reflect" in prompt.lower():
            return "Task completed with good quality results"
        return "Processed successfully"

# Initialize global client
gemini = GeminiClient()

class PlanAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        print(f"\n🧠 PlanAgent - Iteration {state.outer_iteration + 1}")
        state.outer_iteration += 1
        
        if state.outer_iteration > 5:
            state.workflow_complete = True
            return state
        
        # Process feedback first
        if state.feedback_queue:
            state = self._process_feedback(state)
        
        # Create initial tasks if none exist
        if not state.subtasks:
            state = self._create_subtasks(state)
        
        # Check completion
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
            # Extract JSON from response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                tasks_data = json.loads(response[start:end])
            else:
                raise ValueError("No JSON found")
        except:
            # Fallback tasks
            tasks_data = [
                {"description": f"Research: {state.user_query}", "agent_type": "research_agent"},
                {"description": f"Analyze: {state.user_query}", "agent_type": "analysis_agent"},
                {"description": f"Generate output for: {state.user_query}", "agent_type": "creative_agent"}
            ]
        
        # Create SubTask objects
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
    """Select next pending task"""
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
        
        print(f"🤖 Dispatched {task.agent_type} with tools: {tools}")
        return state

class ToolAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        if not state.current_task_id:
            return state
        
        task = state.subtasks[state.current_task_id]
        task.attempts += 1
        task.status = TaskStatus.IN_PROGRESS
        
        print(f"⚙️ Executing {task.id} (attempt {task.attempts})")
        
        # Execute task
        prompt = f"""Execute this task:
        Task: {task.description}
        Agent: {task.agent_type}
        Tools: {', '.join(task.tools)}
        
        Provide detailed execution result."""
        
        result = gemini.generate(prompt)
        task.result = result or f"Executed using {', '.join(task.tools[:2])}"
        task.status = TaskStatus.COMPLETED if result else TaskStatus.FAILED
        
        print(f"📊 Result: {task.result[:60]}...")
        return state

class ReflectionAgent:
    def __call__(self, state: WorkflowState) -> WorkflowState:
        if not state.current_task_id:
            return state
        
        task = state.subtasks[state.current_task_id]
        print(f"🔍 Reflecting on {task.id}")
        
        # Generate reflection
        prompt = f"""Reflect on this task execution:
        Task: {task.description}
        Result: {task.result}
        Status: {task.status.value}
        
        Evaluate quality and suggest improvements."""
        
        reflection = gemini.generate(prompt)
        
        # Create feedback if needed
        feedback = self._generate_feedback(task, reflection)
        if feedback:
            state.feedback_queue.append(feedback)
            print(f"💭 Feedback: {feedback.message}")
        
        return state
    
    def _generate_feedback(self, task: SubTask, reflection: str) -> Optional[TaskFeedback]:
        if task.status == TaskStatus.FAILED:
            if task.attempts < task.max_attempts:
                return TaskFeedback(
                    task_id=task.id,
                    feedback_type=FeedbackType.MODIFY,
                    message="Task failed, needs modification"
                )
            else:
                return TaskFeedback(
                    task_id=task.id,
                    feedback_type=FeedbackType.DELETE,
                    message="Task failed multiple times"
                )
        
        if "additional" in reflection.lower():
            return TaskFeedback(
                task_id=task.id,
                feedback_type=FeedbackType.ADD,
                message="Needs additional work",
                new_tasks=[f"Follow-up for {task.description}"]
            )
        
        return None

def finalize_results(state: WorkflowState) -> WorkflowState:
    """Compile final results"""
    print("\n📋 Finalizing results...")
    
    completed = [t for t in state.subtasks.values() if t.status == TaskStatus.COMPLETED]
    
    if completed:
        results = [f"✅ {t.description}\n   → {t.result}" for t in completed]
        state.final_result = "\n\n".join(results)
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
            return "tool_agent"  # Retry
    
    pending = [t for t in state.subtasks.values() if t.status == TaskStatus.PENDING]
    if pending:
        return "task_selector"
    
    all_done = all(t.status == TaskStatus.COMPLETED for t in state.subtasks.values())
    return "finalize" if all_done else "plan"

def create_workflow() -> StateGraph:
    """Create the agentic workflow"""
    print("🔧 Creating workflow...")
    
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("plan", PlanAgent())
    workflow.add_node("task_selector", select_next_task)
    workflow.add_node("agent_dispatch", AgentDispatch())
    workflow.add_node("tool_agent", ToolAgent())
    workflow.add_node("reflection", ReflectionAgent())
    workflow.add_node("finalize", finalize_results)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Add edges
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

def main():
    print("🚀 Advanced Agentic Workflow")
    print("=" * 50)
    
    query = input("\n💭 Enter your request: ").strip()
    if not query:
        print("No query provided.")
        return
    
    try:
        app = create_workflow()
        initial_state = WorkflowState(user_query=query)
        
        print(f"\n🎯 Processing: {query}")
        print("=" * 50)
        
        final_state = app.invoke(initial_state, config={"recursion_limit": 100})
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 EXECUTION SUMMARY")
        print("=" * 50)
        
        if final_state.get('subtasks'):
            print("\n📋 Tasks:")
            for task_id, task in final_state['subtasks'].items():
                status_map = {
                    TaskStatus.COMPLETED: "✅", TaskStatus.FAILED: "❌",
                    TaskStatus.PENDING: "⏳", TaskStatus.IN_PROGRESS: "🔄"
                }
                emoji = status_map.get(task.status, "❓")
                print(f"   {emoji} {task_id}: {task.description}")
                if task.result:
                    preview = task.result[:60] + "..." if len(task.result) > 60 else task.result
                    print(f"      → {preview}")
        
        if final_state.get('final_result'):
            print(f"\n🎯 FINAL RESULT:")
            print("-" * 30)
            print(final_state['final_result'])
        
        # Stats
        completed = len([t for t in final_state.get('subtasks', {}).values() 
                        if t.status == TaskStatus.COMPLETED])
        total = len(final_state.get('subtasks', {}))
        
        print(f"\n📈 Stats:")
        print(f"   🔄 Outer iterations: {final_state.get('outer_iteration', 0)}")
        print(f"   🔁 Inner iterations: {final_state.get('inner_iteration', 0)}")
        print(f"   ✅ Completed: {completed}/{total}")
        print(f"   🎯 Status: {'Complete' if final_state.get('workflow_complete') else 'Incomplete'}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 

if __name__ == "__main__":
    main()