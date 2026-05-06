import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileWriterTool, DirectoryReadTool, FileReadTool
from report_agent.tools.report_tools import DuckDBQueryTool, PythonExecutionTool

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# --- Cấu hình Retry (thử lại) cho LiteLLM để xử lý lỗi 503/429 ---
os.environ["LITELLM_MAX_RETRIES"] = "10"       # Thử lại tối đa 10 lần
os.environ["LITELLM_INITIAL_DELAY"] = "5"      # Đợi 5 giây trước lần thử đầu tiên
os.environ["LITELLM_BACKOFF_FACTOR"] = "2"     # Tăng gấp đôi thời gian chờ sau mỗi lần lỗi (5s -> 10s -> 20s)

gemini_llm = LLM(
    model="gemini/gemini-3.1-flash-lite-preview",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.0
)

def check_step_status(step_output):
    """Stops the crew if a tool fails"""
    if "Error:" in str(step_output) or "Tool Failed" in str(step_output) or "Execution Failed" in str(step_output):
        print(f"\n🛑 CRITICAL ERROR DETECTED: {step_output}")
        raise Exception(f"Flow halted due to tool failure: {step_output}")

@CrewBase
class ReportAgentCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def router_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['router_agent'],
            tools=[DirectoryReadTool(), FileReadTool()],
            llm=gemini_llm,
            verbose=True
        )

    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],
            tools=[DuckDBQueryTool()],
            llm=gemini_llm,
            verbose=True,
            step_callback=check_step_status
        )

    @agent
    def data_storyteller(self) -> Agent:
        return Agent(
            config=self.agents_config['data_storyteller'],
            tools=[FileWriterTool(), PythonExecutionTool()],
            llm=gemini_llm,
            verbose=True
        )

    @task
    def prompt_evaluation_task(self) -> Task:
        return Task(config=self.tasks_config['prompt_evaluation_task'])

    @task
    def data_extraction_task(self) -> Task:
        return Task(config=self.tasks_config['data_extraction_task'])

    @task
    def reporting_task(self) -> Task:
        return Task(config=self.tasks_config['reporting_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
