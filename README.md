
# Jashu Multi-Agent Workflow 🤖

An intelligent multi-agent AI system that breaks down complex tasks into specialized subtasks using LangGraph and Google's Gemini AI. The system features a beautiful web interface and sophisticated agent orchestration for handling complex queries.

![AI Powered](https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple?style=for-the-badge)

## ✨ Features

- **🧠 Intelligent Task Decomposition**: Automatically breaks down complex queries into manageable subtasks
- **🤖 Specialized Agents**: Multiple agent types with specific capabilities
  - Research Agent (web search, document analysis)
  - Analysis Agent (data processing, statistical analysis)
  - Creative Agent (text generation, content creation)
  - Technical Agent (calculations, code execution)
- **🔄 Adaptive Workflow**: Self-correcting system with feedback loops and reflection
- **🎯 Visual Interface**: Modern, responsive web UI with real-time progress tracking
- **📊 Comprehensive Reporting**: Detailed execution summaries and statistics
- **⚡ Fallback System**: Works even without API keys using intelligent fallbacks

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (optional - fallback mode available)

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
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```
   
   > **Note**: If you don't have a Gemini API key, the system will automatically use fallback mode

4. **Run the application**
   
   **Web Interface:**
   ```bash
   python app.py
   ```
   Then open `http://localhost:5000` in your browser
   
   **Command Line:**
   ```bash
   python agentic_workflow.py
   ```

## 💻 Usage

### Web Interface

1. Open the web application at `http://localhost:5000`
2. Enter your complex task or question in the text area
3. Click "🚀 Process with AI Agents"
4. Watch as the system breaks down your task and processes it with specialized agents
5. View comprehensive results with detailed subtask breakdown

### Command Line Interface

```bash
python agentic_workflow.py
```

Enter your query when prompted, and the system will process it through the multi-agent workflow.

### Example Queries

- "Plan a complete marketing strategy for a new eco-friendly product"
- "Analyze the pros and cons of different programming languages for web development"
- "Create a comprehensive business plan for a tech startup"
- "Research and summarize the latest trends in artificial intelligence"

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Plan Agent    │───▶│  Task Selector   │───▶│ Agent Dispatch  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                                              │
         │                                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Reflection      │◀───│   Tool Agent     │◀───│  Specialized    │
│ Agent           │    │                  │    │  Agents         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Agent Types

- **🧠 Plan Agent**: Orchestrates workflow, creates and manages subtasks
- **🎯 Task Selector**: Chooses next pending task for execution
- **🚀 Agent Dispatch**: Routes tasks to appropriate specialized agents
- **⚙️ Tool Agent**: Executes tasks using available tools
- **🔍 Reflection Agent**: Evaluates results and provides feedback
- **📋 Finalization**: Compiles and formats final results

### Workflow States

- **PENDING**: Task waiting to be processed
- **IN_PROGRESS**: Task currently being executed
- **COMPLETED**: Task successfully finished
- **FAILED**: Task failed (with retry mechanism)

## 🛠️ Configuration

### Environment Variables

```bash
# Required for full functionality
GOOGLE_API_KEY=your_gemini_api_key

# Optional configurations
MAX_ITERATIONS=5
MAX_TASK_ATTEMPTS=3
```

### Customization

The system is highly customizable. You can:

- Add new agent types by modifying the `CAPABILITIES` dictionary
- Adjust retry logic and iteration limits
- Customize the web interface styling
- Extend tool capabilities for different agent types

## 📁 Project Structure

```
jashu-multi-agent-workflow/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (create this)
├── agentic_workflow.py      # Core workflow engine
├── app.py                   # Flask web application (create this)
├── index.html              # Web interface
├── static/                 # Static assets (if needed)
└── templates/              # HTML templates (if using Flask templates)
```

## 🔧 API Reference

### WorkflowState

Main state object that flows through the system:

```python
@dataclass
class WorkflowState:
    user_query: str                    # Original user query
    subtasks: Dict[str, SubTask]       # Generated subtasks
    task_order: List[str]              # Execution order
    current_task_id: Optional[str]     # Currently processing task
    outer_iteration: int               # Planning iterations
    inner_iteration: int               # Task execution iterations
    feedback_queue: List[TaskFeedback] # Pending feedback
    workflow_complete: bool            # Completion status
    final_result: str                  # Compiled results
```

### SubTask

Individual task representation:

```python
@dataclass
class SubTask:
    id: str                    # Unique identifier
    description: str           # Task description
    status: TaskStatus         # Current status
    result: str               # Execution result
    agent_type: str           # Assigned agent type
    tools: List[str]          # Available tools
    attempts: int             # Execution attempts
    max_attempts: int         # Maximum retry attempts
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/jashu-multi-agent-workflow.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Additional dev tools
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions and classes
- Write tests for new features

## 📊 Performance & Monitoring

The system includes built-in monitoring:
- Execution time tracking
- Success/failure rates
- Iteration counts
- Task completion statistics

### Metrics Dashboard

Access metrics through the web interface:
- **Success Rate**: Percentage of completed tasks
- **Processing Time**: Total workflow duration
- **Complexity Score**: Estimated task difficulty (1-10)
- **Agent Utilization**: Usage statistics per agent type

## 🔒 Security & Privacy

- No data persistence by default
- API keys stored in environment variables
- Local processing (no external data sharing except API calls)
- Configurable timeout and rate limiting

## 🐛 Troubleshooting

### Common Issues

**1. "No API key" warnings**
```bash
# Solution: Set your Gemini API key
export GOOGLE_API_KEY="your_key_here"
```

**2. Import errors**
```bash
# Solution: Install all dependencies
pip install -r requirements.txt
```

**3. Web interface not loading**
```bash
# Solution: Check if Flask is installed and port is available
pip install Flask
# Try different port: python app.py --port 8080
```

**4. Workflow gets stuck**
- Check iteration limits in configuration
- Verify API key validity
- Review task complexity (try simpler queries first)

### Debug Mode

Run with debug information:
```bash
python -u agentic_workflow.py --debug
```

## 📈 Roadmap

### Upcoming Features

- [ ] **Plugin System**: Easy integration of custom agents and tools
- [ ] **Database Integration**: Persistent workflow storage
- [ ] **API Endpoints**: RESTful API for external integration
- [ ] **Multi-language Support**: Interface localization
- [ ] **Advanced Analytics**: Detailed performance metrics
- [ ] **Collaborative Workflows**: Multi-user support
- [ ] **Custom Agent Training**: Fine-tuning capabilities

### Version History

- **v1.0.0** - Initial release with core multi-agent functionality
- **v1.1.0** - Added web interface and improved error handling
- **v1.2.0** - Enhanced reflection system and fallback modes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph**: For the excellent graph-based workflow framework
- **Google Gemini**: For powerful AI capabilities
- **Open Source Community**: For inspiration and contributions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/jashu-multi-agent-workflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/jashu-multi-agent-workflow/discussions)
- **Email**: support@jashu-workflow.com

---

<div align="center">

**Built with ❤️ by the Jashu Team**

[🌟 Star this repo](https://github.com/your-username/jashu-multi-agent-workflow) | [🍴 Fork it](https://github.com/your-username/jashu-multi-agent-workflow/fork) | [📞 Get Support](https://github.com/your-username/jashu-multi-agent-workflow/issues)

</div>
