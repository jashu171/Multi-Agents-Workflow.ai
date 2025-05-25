# Jashu Multi-Agent Workflow 🤖

An intelligent multi-agent AI system built with **LangGraph** that breaks down complex tasks into specialized subtasks using advanced workflow orchestration. The system features a beautiful web interface and sophisticated agent coordination for handling complex queries through iterative task refinement and reflection.

![AI Powered](https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-Integrated-red?style=for-the-badge)

## 🎯 Objective

This project implements a sophisticated multi-agent pipeline that:

- **Splits user queries** into manageable sub-tasks using a specialized PlanAgent
- **Iteratively refines tasks** through modify, delete, and add operations
- **Solves tasks efficiently** using ToolAgent with specialized capabilities  
- **Implements feedback loops** and reflection mechanisms for reliability
- **Integrates multiple language models** and tools through LangGraph architecture

## 🧠 Understanding LangGraph Architecture

### What is LangGraph?

**LangGraph** is a library for building stateful, multi-actor applications with Large Language Models (LLMs). It extends LangChain's capabilities by providing a graph-based approach to workflow orchestration.

### Core Concepts

#### 🔗 **Nodes**
Nodes represent individual agents or processing units in the workflow:
- **PlanAgent Node**: Decomposes complex queries into subtasks
- **TaskSelector Node**: Chooses the next pending task for execution
- **ToolAgent Node**: Executes tasks using specialized tools and capabilities
- **ReflectionAgent Node**: Evaluates results and provides feedback
- **FinalizationAgent Node**: Compiles and formats final results

#### ⚡ **Edges** 
Edges define the flow and transitions between nodes:
- **Conditional Edges**: Route based on state conditions (task status, completion criteria)
- **Normal Edges**: Direct connections between sequential processing steps
- **Feedback Edges**: Enable iterative refinement and reflection loops

#### 📊 **State Management**
LangGraph maintains a centralized state that flows through all nodes:
```python
@dataclass
class WorkflowState:
    user_query: str                    # Original user input
    subtasks: Dict[str, SubTask]       # Generated and managed subtasks
    task_order: List[str]              # Execution sequence
    current_task_id: Optional[str]     # Active task identifier
    outer_iteration: int               # Planning cycle count
    inner_iteration: int               # Task execution attempts
    feedback_queue: List[TaskFeedback] # Pending evaluations
    workflow_complete: bool            # Completion status
    final_result: str                  # Compiled output
```

## 🏗️ System Architecture

### Visual Workflow Graph

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   START         │───▶│   PlanAgent      │───▶│  TaskSelector   │
│   (User Query)  │    │   (Decompose)    │    │  (Choose Next)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲                       │
                                │                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ ReflectionAgent │◀───│   ToolAgent      │◀───│  Agent Dispatch │
│ (Evaluate &     │    │   (Execute)      │    │  (Route Task)   │
│  Feedback)      │    └──────────────────┘    └─────────────────┘
└─────────────────┘             │                       
         │                      ▼                       
         │              ┌──────────────────┐            
         └─────────────▶│  Finalization    │            
                        │  (Compile)       │            
                        └──────────────────┘            
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   END            │
                        │  (Final Result)  │
                        └──────────────────┘
```

### LangGraph Integration Flow

1. **State Initialization**: User query creates initial WorkflowState
2. **Node Execution**: Each agent processes state and returns updated version
3. **Edge Routing**: Conditional logic determines next node based on state
4. **Iteration Control**: Feedback loops enable task refinement
5. **State Persistence**: Complete workflow state maintained throughout process

## ✨ Features

### 🤖 **Multi-Agent Orchestration**
- **PlanAgent**: Intelligent task decomposition using Gemini LLM
- **ToolAgent**: Specialized execution with capability-based routing
- **ReflectionAgent**: Quality assurance and iterative improvement
- **TaskSelector**: Optimal task prioritization and sequencing

### 🔄 **Advanced Workflow Management**
- **Stateful Processing**: LangGraph maintains context across all operations
- **Conditional Routing**: Dynamic path selection based on task status
- **Feedback Loops**: Continuous improvement through reflection cycles
- **Error Recovery**: Robust handling with retry mechanisms

### 🛠️ **LangChain Integration**
- **Tool Management**: Seamless integration of LangChain tools
- **Memory Systems**: Persistent context across agent interactions
- **Chain Composition**: Complex reasoning through agent collaboration
- **Custom Tools**: Extensible tool ecosystem for domain-specific tasks

### 🚀 **Gemini LLM Integration**
- **API Key Management**: Secure credential handling
- **Model Selection**: Flexible LLM model configuration
- **Response Processing**: Intelligent parsing and validation
- **Fallback Systems**: Graceful degradation when API unavailable

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (required for full functionality)
- LangChain and LangGraph dependencies

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/jashu-multi-agent-workflow.git
   cd jashu-multi-agent-workflow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your API credentials
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   echo "LANGCHAIN_API_KEY=your_langchain_key_here" >> .env
   echo "LANGCHAIN_TRACING_V2=true" >> .env
   ```

4. **Verify LangGraph installation**
   ```bash
   python -c "import langgraph; print('LangGraph successfully installed')"
   ```

5. **Run the application**
   
   **Web Interface:**
   ```bash
   python app.py
   ```
   Then open `http://localhost:5000` in your browser
   
   **Command Line:**
   ```bash
   python agentic_workflow.py
   ```

## 💻 Usage Examples

### Complex Task Processing

The system excels at breaking down complex, multi-faceted queries:

**Business Strategy Example:**
```
Input: "Create a comprehensive go-to-market strategy for an AI-powered fitness app"

LangGraph Processing:
├── PlanAgent: Decomposes into market research, competitor analysis, pricing strategy
├── ToolAgent: Executes research using web search and analysis tools
├── ReflectionAgent: Evaluates completeness and suggests refinements
└── Finalization: Compiles comprehensive strategy document
```

**Technical Analysis Example:**
```
Input: "Compare cloud platforms for a microservices architecture migration"

Workflow Execution:
├── Task 1: Research AWS, Azure, GCP capabilities
├── Task 2: Analyze cost structures and pricing models
├── Task 3: Evaluate security and compliance features
├── Task 4: Compare development and deployment tools
└── Final: Detailed comparison with recommendations
```

## 🔧 LangGraph Configuration

### Node Definitions

```python
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Define workflow graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("plan_agent", plan_agent_node)
workflow.add_node("task_selector", task_selector_node)  
workflow.add_node("tool_agent", tool_agent_node)
workflow.add_node("reflection_agent", reflection_agent_node)
workflow.add_node("finalization", finalization_node)

# Define edges with conditions
workflow.add_conditional_edges(
    "plan_agent",
    route_after_planning,
    {
        "continue": "task_selector",
        "end": "finalization"
    }
)
```

### State Transitions

```python
def route_after_planning(state: WorkflowState) -> str:
    """Conditional routing based on planning results"""
    if not state.subtasks:
        return "end"
    if state.outer_iteration >= MAX_ITERATIONS:
        return "end"
    return "continue"

def route_after_execution(state: WorkflowState) -> str:
    """Route based on task execution status"""
    if state.workflow_complete:
        return "finalization"
    if state.feedback_queue:
        return "reflection_agent"
    return "task_selector"
```

## 🛠️ Agent Capabilities

### PlanAgent Capabilities
- **Task Decomposition**: Breaking complex queries into subtasks
- **Dependency Analysis**: Understanding task relationships
- **Resource Allocation**: Assigning appropriate tools and agents
- **Timeline Estimation**: Predicting execution complexity

### ToolAgent Specializations
- **Research Agent**: Web search, document analysis, information gathering
- **Analysis Agent**: Data processing, statistical analysis, pattern recognition
- **Creative Agent**: Content generation, writing, ideation
- **Technical Agent**: Code execution, calculations, technical problem-solving

### ReflectionAgent Functions
- **Quality Assessment**: Evaluating task completion quality
- **Gap Analysis**: Identifying missing information or incomplete results
- **Improvement Suggestions**: Recommending task modifications
- **Workflow Optimization**: Suggesting process improvements

## 📊 Performance Monitoring

### Built-in Metrics

The system tracks comprehensive performance data:

- **Execution Metrics**: Processing time, iteration counts, success rates
- **Agent Performance**: Individual agent utilization and effectiveness
- **Task Analytics**: Complexity scoring, completion patterns
- **Resource Usage**: API calls, token consumption, error rates

### LangSmith Integration

Enable advanced monitoring with LangSmith:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="your_langsmith_key"
export LANGCHAIN_PROJECT="jashu-workflow"
```

## 🔒 Security & Best Practices

### API Key Management
- Store credentials in environment variables
- Use `.env` files for local development
- Implement key rotation policies
- Monitor API usage and rate limits

### State Security
- No persistent storage of sensitive data
- In-memory state management only
- Configurable data retention policies
- Secure inter-agent communication

## 🧪 Testing & Development

### Unit Testing
```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Test specific components
python -m pytest tests/test_langgraph_workflow.py
python -m pytest tests/test_agent_integration.py
```

### Development Mode
```bash
# Enable debug logging
export DEBUG=true
python agentic_workflow.py --verbose

# Test with sample queries
python test_workflow.py --sample-queries
```

## 📈 Roadmap & Future Enhancements

### Planned Features
- [ ] **Advanced Graph Topologies**: Complex workflow patterns
- [ ] **Multi-LLM Support**: Integration with multiple language models
- [ ] **Custom Tool Development**: SDK for building specialized tools
- [ ] **Workflow Templates**: Pre-built patterns for common use cases
- [ ] **Real-time Collaboration**: Multi-user workflow sharing
- [ ] **Performance Optimization**: Enhanced caching and parallel processing

### LangGraph Enhancements
- [ ] **Subgraph Support**: Nested workflow capabilities
- [ ] **Dynamic Graph Modification**: Runtime workflow adjustments
- [ ] **Advanced State Management**: Persistent state backends
- [ ] **Workflow Versioning**: Change tracking and rollback capabilities

## 🔧 Troubleshooting

### Common LangGraph Issues

**Graph Compilation Errors**
```bash
# Validate graph structure
python -c "from workflow import workflow; workflow.compile()"
```

**State Management Issues**
```bash
# Debug state transitions
export LANGGRAPH_DEBUG=true
python agentic_workflow.py --debug-state
```

**API Integration Problems**
```bash
# Test API connectivity
python test_gemini_connection.py
python test_langchain_tools.py
```

## 📚 Documentation & Resources

### LangGraph Documentation
- [Official LangGraph Guide](https://python.langchain.com/docs/langgraph)
- [State Management Patterns](https://python.langchain.com/docs/langgraph/concepts)
- [Advanced Workflows](https://python.langchain.com/docs/langgraph/tutorials)

### Integration Guides
- [Gemini API Setup](https://ai.google.dev/tutorials/setup)
- [LangChain Tools](https://python.langchain.com/docs/integrations/tools)
- [Custom Agent Development](https://python.langchain.com/docs/modules/agents)

## 🤝 Contributing

We welcome contributions to enhance the multi-agent workflow system!

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/jashu-multi-agent-workflow.git

# Install development dependencies
pip install -e ".[dev]"
pip install pytest black flake8 mypy

# Run pre-commit hooks
pre-commit install
```

### Contribution Guidelines
- Follow LangGraph best practices
- Maintain comprehensive test coverage
- Document new agent capabilities
- Update workflow diagrams for architectural changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph Team**: For the exceptional graph-based workflow framework
- **LangChain Community**: For comprehensive tool ecosystem
- **Google AI**: For Gemini API and advanced language capabilities
- **Open Source Contributors**: For continuous improvement and innovation

---

<div align="center">

**Built with ❤️ using LangGraph, LangChain, and Gemini AI**

[🌟 Star this repo](https://github.com/your-username/jashu-multi-agent-workflow) | [🍴 Fork it](https://github.com/your-username/jashu-multi-agent-workflow/fork) | [📞 Get Support](https://github.com/your-username/jashu-multi-agent-workflow/issues)

**Experience the Future of Multi-Agent AI Workflows**

</div>
