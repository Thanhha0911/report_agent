import sys
import os

# Fix Windows console emoji printing issues
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add the parent directory to sys.path so 'report_agent' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from report_agent.crew import ReportAgentCrew

def run():
    print("Welcome to the Report Agent!")
    
    # Check if a prompt was provided as a command-line argument
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter your analysis request: ")
    
    if not user_prompt.strip():
        print("No prompt provided. Exiting.")
        sys.exit(1)

    project_root = os.path.abspath(os.path.dirname(__file__))
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_folder_name = f"report_{timestamp}"
    report_folder = os.path.join(project_root, 'results', report_folder_name)
    os.makedirs(report_folder, exist_ok=True)
    
    # Use forward slashes for safer prompt interpolation
    report_folder = report_folder.replace('\\', '/')

    inputs = {
        'user_prompt': user_prompt,
        'tone_of_voice': 'professional',
        'language': 'English',
        'report_folder': report_folder
    }

    print("\nStarting Analysis...")
    print(f"Prompt: {user_prompt}")
    print(f"Output Folder: {report_folder}\n")
    
    ReportAgentCrew().crew().kickoff(inputs=inputs)
    print(f"\nAnalysis Complete! Check the {report_folder} folder for reports.")

if __name__ == "__main__":
    run()
