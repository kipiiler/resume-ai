import click
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Import service abstractions and models
from services.user import UserService
from services.experience import ExperienceService
from services.project import ProjectService
from agents import AgentFactory
from services.resume_writer import ResumeWriter
from model.schema import User, Experience, Project

console = Console()

# Initialize services
user_service = UserService()
experience_service = ExperienceService()
project_service = ProjectService()

def ensure_data_directory():
    """Ensure the data directory exists."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        console.print(f"[dim]Created data directory: {data_dir}[/dim]")
    return data_dir

def get_or_create_user() -> int:
    """Get existing user or create a new one."""
    console.print("\n[bold blue]User Information[/bold blue]")
    
    # Check if user exists
    email = Prompt.ask("Enter your email")
    existing_user = user_service.get_user_by_email(email)
    
    if existing_user:
        console.print(f"[green]Welcome back, {existing_user.name}![/green]")
        return existing_user.id
    
    # Create new user
    console.print("[yellow]User not found. Let's create a new profile.[/yellow]")
    name = Prompt.ask("Full Name")
    phone = Prompt.ask("Phone Number")
    education = Prompt.ask("University")
    degree = Prompt.ask("Degree (e.g., Bachelor's, Master's)")
    major = Prompt.ask("Major/Field of Study")
    location = Prompt.ask("Location (City, State)")
    
    # Optional fields
    grade = Prompt.ask("Grade/GPA (optional)", default="")
    grad_date = get_grad_date_input("Graduation Date (Month Year, e.g., Dec 2025) (optional, press Enter to skip)")
    
    # Personality traits
    console.print("\n[bold]Enter personality traits (comma-separated, optional)[/bold]")
    personality_input = Prompt.ask("Personality traits", default="")
    personality = [trait.strip() for trait in personality_input.split(",")] if personality_input else []
    
    new_user = User(
        name=name,
        email=email,
        phone=phone,
        personality=personality,
        education=education,
        degree=degree,
        major=major,
        grade=grade if grade else None,
        location=location,
        grad_year=grad_date if grad_date else None
    )
    
    created_user = user_service.create_user(new_user)
    console.print(f"[green]User profile created successfully! ID: {created_user.id}[/green]")
    return created_user.id

def get_date_input(prompt: str) -> str:
    """Get date input with validation."""
    while True:
        date_str = Prompt.ask(prompt + " (YYYY-MM format)")
        try:
            # Validate YYYY-MM format
            datetime.strptime(date_str, "%Y-%m")
            return date_str
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM (e.g., 2023-01)[/red]")

def get_grad_date_input(prompt: str) -> str:
    """Get graduation date input with validation for Month Year format."""
    while True:
        date_str = Prompt.ask(prompt)
        if not date_str:  # Allow empty input
            return ""
        try:
            # Validate "Month Year" format (e.g., "Dec 2025")
            datetime.strptime(date_str, "%b %Y")
            return date_str
        except ValueError:
            console.print("[red]Invalid date format. Please use 'Month Year' format (e.g., Dec 2025)[/red]")

def get_experience_input(user_id: int) -> Experience:
    """Get experience details from user input."""
    console.print("\n[bold blue]Enter Experience Details[/bold blue]")
    
    company_name = Prompt.ask("Company Name")
    role_title = Prompt.ask("Role/Position Title")
    company_location = Prompt.ask("Company Location (City, State)")
    start_date = get_date_input("Start Date")
    end_date = get_date_input("End Date")
    short_description = Prompt.ask("Short Description About this experience")
    long_description = Prompt.ask("Detailed Description of this experience")
    
    console.print("\n[bold]Enter technologies/skills used (comma-separated)[/bold]")
    tech_input = Prompt.ask("Technologies/Skills")
    tech_stack = [tech.strip() for tech in tech_input.split(",")]
    
    return Experience(
        user_id=user_id,
        company_name=company_name,
        role_title=role_title,
        company_location=company_location,
        start_date=start_date,
        end_date=end_date,
        long_description=long_description,
        short_description=short_description,
        tech_stack=tech_stack
    )

def get_project_input(user_id: int) -> Project:
    """Get project details from user input."""
    console.print("\n[bold blue]Enter Project Details[/bold blue]")
    
    project_name = Prompt.ask("Project Name")
    short_description = Prompt.ask("Short description of this project")
    long_description = Prompt.ask("Detailed description of this project")
    
    # Optional dates
    has_dates = Confirm.ask("Do you want to add start and end dates?")
    start_date = get_date_input("Start Date") if has_dates else None
    end_date = get_date_input("End Date") if has_dates else None
    
    console.print("\n[bold]Enter technologies used (comma-separated)[/bold]")
    tech_input = Prompt.ask("Technologies")
    tech_stack = [tech.strip() for tech in tech_input.split(",")]
    
    team_size_str = Prompt.ask("Team Size (optional)", default="1")
    team_size = int(team_size_str) if team_size_str.isdigit() else 1
    
    return Project(
        user_id=user_id,
        project_name=project_name,
        start_date=start_date,
        end_date=end_date,
        long_description=long_description,
        short_description=short_description,
        tech_stack=tech_stack,
        team_size=team_size
    )

def display_user_experiences(user_id: int, show_ids: bool = False):
    """Display all experiences for a user."""
    experiences = experience_service.get_user_experiences(user_id)
    
    if not experiences:
        console.print("[yellow]No experiences found.[/yellow]")
        return experiences
    
    for i, exp in enumerate(experiences, 1):
        title = f"Experience {i}: {exp.company_name}"
        if show_ids:
            title += f" (ID: {exp.id})"
        table = Table(title=title)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Company", exp.company_name)
        table.add_row("Role/Position", exp.role_title)
        table.add_row("Location", exp.company_location)
        table.add_row("Short Description", exp.short_description)
        table.add_row("Duration", f"{exp.start_date} to {exp.end_date}")
        table.add_row("Description", exp.long_description)
        table.add_row("Technologies", ", ".join(exp.tech_stack) if exp.tech_stack else "N/A")
        
        console.print(table)
        console.print()
    
    return experiences

def display_user_projects(user_id: int, show_ids: bool = False):
    """Display all projects for a user."""
    projects = project_service.get_user_projects(user_id)
    
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return projects
    
    for i, proj in enumerate(projects, 1):
        title = f"Project {i}: {proj.project_name}"
        if show_ids:
            title += f" (ID: {proj.id})"
        table = Table(title=title)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Name", proj.project_name)
        table.add_row("Short Description", proj.short_description)
        table.add_row("Duration", f"{proj.start_date or 'N/A'} to {proj.end_date or 'N/A'}")
        table.add_row("Description", proj.long_description)
        table.add_row("Technologies", ", ".join(proj.tech_stack) if proj.tech_stack else "N/A")
        table.add_row("Team Size", str(proj.team_size))
        
        console.print(table)
        console.print()
    
    return projects

def edit_experience(user_id: int):
    """Edit an existing experience."""
    console.print("\n[bold blue]Edit Experience[/bold blue]")
    
    # Display current experiences with IDs
    experiences = display_user_experiences(user_id, show_ids=True)
    if not experiences:
        return
    
    # Get experience ID to edit
    exp_ids = [str(exp.id) for exp in experiences]
    exp_id_str = Prompt.ask("Enter the ID of the experience you want to edit", choices=exp_ids)
    exp_id = int(exp_id_str)
    
    # Get the current experience
    current_exp = experience_service.get_experience(exp_id)
    if not current_exp:
        console.print("[red]Experience not found.[/red]")
        return
    
    console.print(f"\n[bold]Editing: {current_exp.company_name}[/bold]")
    console.print("[dim]Press Enter to keep current value[/dim]")
    
    # Get updated values (with current values as defaults)
    company_name = Prompt.ask("Company Name", default=current_exp.company_name)
    role_title = Prompt.ask("Role/Position Title", default=current_exp.role_title)
    company_location = Prompt.ask("Company Location", default=current_exp.company_location)
    start_date = Prompt.ask("Start Date (YYYY-MM)", default=current_exp.start_date)
    end_date = Prompt.ask("End Date (YYYY-MM)", default=current_exp.end_date)
    short_description = Prompt.ask("Short Description", default=current_exp.short_description)
    long_description = Prompt.ask("Detailed Description", default=current_exp.long_description)
    
    current_tech = ", ".join(current_exp.tech_stack) if current_exp.tech_stack else ""
    tech_input = Prompt.ask("Technologies/Skills (comma-separated)", default=current_tech)
    tech_stack = [tech.strip() for tech in tech_input.split(",")]
    
    # Create updated experience object
    updated_exp = Experience(
        user_id=user_id,
        company_name=company_name,
        role_title=role_title,
        company_location=company_location,
        start_date=start_date,
        end_date=end_date,
        long_description=long_description,
        short_description=short_description,
        tech_stack=tech_stack
    )
    
    # Update in database
    result = experience_service.update_experience(exp_id, updated_exp)
    if result:
        console.print(f"[green]Experience at {result.company_name} updated successfully![/green]")
    else:
        console.print("[red]Failed to update experience.[/red]")

def edit_project(user_id: int):
    """Edit an existing project."""
    console.print("\n[bold blue]Edit Project[/bold blue]")
    
    # Display current projects with IDs
    projects = display_user_projects(user_id, show_ids=True)
    if not projects:
        return
    
    # Get project ID to edit
    proj_ids = [str(proj.id) for proj in projects]
    proj_id_str = Prompt.ask("Enter the ID of the project you want to edit", choices=proj_ids)
    proj_id = int(proj_id_str)
    
    # Get the current project
    current_proj = project_service.get_project(proj_id)
    if not current_proj:
        console.print("[red]Project not found.[/red]")
        return
    
    console.print(f"\n[bold]Editing: {current_proj.project_name}[/bold]")
    console.print("[dim]Press Enter to keep current value[/dim]")
    
    # Get updated values (with current values as defaults)
    project_name = Prompt.ask("Project Name", default=current_proj.project_name)
    short_description = Prompt.ask("Short Description", default=current_proj.short_description)
    long_description = Prompt.ask("Detailed Description", default=current_proj.long_description)
    start_date = Prompt.ask("Start Date (YYYY-MM, optional)", default=current_proj.start_date or "")
    end_date = Prompt.ask("End Date (YYYY-MM, optional)", default=current_proj.end_date or "")
    
    current_tech = ", ".join(current_proj.tech_stack) if current_proj.tech_stack else ""
    tech_input = Prompt.ask("Technologies (comma-separated)", default=current_tech)
    tech_stack = [tech.strip() for tech in tech_input.split(",")]
    
    team_size_str = Prompt.ask("Team Size", default=str(current_proj.team_size))
    team_size = int(team_size_str) if team_size_str.isdigit() else 1
    
    # Create updated project object
    updated_proj = Project(
        user_id=user_id,
        project_name=project_name,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        long_description=long_description,
        short_description=short_description,
        tech_stack=tech_stack,
        team_size=team_size
    )
    
    # Update in database
    result = project_service.update_project(proj_id, updated_proj)
    if result:
        console.print(f"[green]Project '{result.project_name}' updated successfully![/green]")
    else:
        console.print("[red]Failed to update project.[/red]")

def load_data_from_json(user_id: int):
    """Load experiences and projects from a JSON file."""
    console.print("\n[bold blue]Load Data from JSON File[/bold blue]")
    
    # Get file path
    file_path = Prompt.ask("Enter the path to your JSON file")
    
    if not os.path.exists(file_path):
        console.print(f"[red]File not found: {file_path}[/red]")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validate JSON structure
        if not isinstance(data, dict):
            console.print("[red]Invalid JSON format. Expected a dictionary with 'experiences' and/or 'projects' keys.[/red]")
            return
        
        experiences_data = data.get('experiences', [])
        projects_data = data.get('projects', [])
        
        if not experiences_data and not projects_data:
            console.print("[yellow]No experiences or projects found in the JSON file.[/yellow]")
            return
        
        console.print(f"Found {len(experiences_data)} experiences and {len(projects_data)} projects in the file.")
        
        if not Confirm.ask("Do you want to proceed with loading this data?"):
            return
        
        # Load experiences
        exp_success = 0
        exp_errors = []
        for i, exp_data in enumerate(experiences_data):
            try:
                # Validate required fields
                required_fields = ['company_name', 'role_title', 'company_location', 'start_date', 'end_date', 
                                 'short_description', 'long_description']
                missing_fields = [field for field in required_fields if field not in exp_data]
                if missing_fields:
                    exp_errors.append(f"Experience {i+1}: Missing fields: {', '.join(missing_fields)}")
                    continue
                
                experience = Experience(
                    user_id=user_id,
                    company_name=exp_data['company_name'],
                    role_title=exp_data['role_title'],
                    company_location=exp_data['company_location'],
                    start_date=exp_data['start_date'],
                    end_date=exp_data['end_date'],
                    short_description=exp_data['short_description'],
                    long_description=exp_data['long_description'],
                    tech_stack=exp_data.get('tech_stack', [])
                )
                
                experience_service.create_experience(experience)
                exp_success += 1
                
            except Exception as e:
                exp_errors.append(f"Experience {i+1}: {str(e)}")
        
        # Load projects
        proj_success = 0
        proj_errors = []
        for i, proj_data in enumerate(projects_data):
            try:
                # Validate required fields
                required_fields = ['project_name', 'short_description', 'long_description']
                missing_fields = [field for field in required_fields if field not in proj_data]
                if missing_fields:
                    proj_errors.append(f"Project {i+1}: Missing fields: {', '.join(missing_fields)}")
                    continue
                
                project = Project(
                    user_id=user_id,
                    project_name=proj_data['project_name'],
                    start_date=proj_data.get('start_date'),
                    end_date=proj_data.get('end_date'),
                    short_description=proj_data['short_description'],
                    long_description=proj_data['long_description'],
                    tech_stack=proj_data.get('tech_stack', []),
                    team_size=proj_data.get('team_size', 1)
                )
                
                project_service.create_project(project)
                proj_success += 1
                
            except Exception as e:
                proj_errors.append(f"Project {i+1}: {str(e)}")
        
        # Report results
        console.print(f"\n[green]Successfully loaded {exp_success} experiences and {proj_success} projects![/green]")
        
        if exp_errors:
            console.print(f"\n[yellow]Experience errors ({len(exp_errors)}):[/yellow]")
            for error in exp_errors:
                console.print(f"  • {error}")
        
        if proj_errors:
            console.print(f"\n[yellow]Project errors ({len(proj_errors)}):[/yellow]")
            for error in proj_errors:
                console.print(f"  • {error}")
                
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON file: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error loading file: {str(e)}[/red]")

def export_data_to_json(user_id: int):
    """Export user's experiences and projects to a JSON file."""
    console.print("\n[bold blue]Export Data to JSON File[/bold blue]")
    
    # Get user data
    experiences = experience_service.get_user_experiences(user_id)
    projects = project_service.get_user_projects(user_id)
    
    if not experiences and not projects:
        console.print("[yellow]No data to export. Add some experiences or projects first.[/yellow]")
        return
    
    # Convert to dictionaries
    experiences_data = []
    for exp in experiences:
        experiences_data.append({
            'company_name': exp.company_name,
            'role_title': exp.role_title,
            'company_location': exp.company_location,
            'start_date': exp.start_date,
            'end_date': exp.end_date,
            'short_description': exp.short_description,
            'long_description': exp.long_description,
            'tech_stack': exp.tech_stack or []
        })
    
    projects_data = []
    for proj in projects:
        projects_data.append({
            'project_name': proj.project_name,
            'start_date': proj.start_date,
            'end_date': proj.end_date,
            'short_description': proj.short_description,
            'long_description': proj.long_description,
            'tech_stack': proj.tech_stack or [],
            'team_size': proj.team_size
        })
    
    # Create export data
    export_data = {
        'experiences': experiences_data,
        'projects': projects_data,
        'export_info': {
            'total_experiences': len(experiences_data),
            'total_projects': len(projects_data),
            'export_date': datetime.now().isoformat()
        }
    }
    
    # Get file path
    default_filename = f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data_dir = ensure_data_directory()
    default_path = os.path.join(data_dir, default_filename)
    file_path = Prompt.ask("Enter the output file path", default=default_path)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(export_data, file, indent=2, ensure_ascii=False)
        
        console.print(f"[green]Data exported successfully to: {file_path}[/green]")
        console.print(f"[dim]Exported {len(experiences_data)} experiences and {len(projects_data)} projects[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error exporting data: {str(e)}[/red]")

def delete_all_user_data(user_id: int):
    """Delete all experiences and projects for a user."""
    console.print("\n[bold red]Delete All Data[/bold red]")
    
    # Get current data count
    experiences = experience_service.get_user_experiences(user_id)
    projects = project_service.get_user_projects(user_id)
    
    if not experiences and not projects:
        console.print("[yellow]No data to delete.[/yellow]")
        return
    
    console.print(f"[yellow]This will delete {len(experiences)} experiences and {len(projects)} projects.[/yellow]")
    console.print("[bold red]This action cannot be undone![/bold red]")
    
    # Double confirmation
    if not Confirm.ask("Are you sure you want to delete ALL your data?"):
        console.print("[green]Operation cancelled.[/green]")
        return
    
    if not Confirm.ask("This is your final warning. Delete ALL data?"):
        console.print("[green]Operation cancelled.[/green]")
        return
    
    try:
        # Delete all experiences
        exp_deleted = 0
        for exp in experiences:
            if experience_service.delete_experience(exp.id):
                exp_deleted += 1
        
        # Delete all projects
        proj_deleted = 0
        for proj in projects:
            if project_service.delete_project(proj.id):
                proj_deleted += 1
        
        console.print(f"[green]Successfully deleted {exp_deleted} experiences and {proj_deleted} projects.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error deleting data: {str(e)}[/red]")

def generate_resume_from_job_url(user_id: int):
    """Generate resume content from a job URL using the complete workflow."""
    console.print("\n[bold blue]Generate Resume from Job URL[/bold blue]")
    
    # Get job URL from user
    job_url = Prompt.ask("Enter the job posting URL")
    
    # Configuration
    num_experiences = int(Prompt.ask("Number of top experiences to include", default="3"))
    num_projects = int(Prompt.ask("Number of top projects to include", default="3"))
    
    try:
        console.print("\n[yellow]Step 1: Analyzing job posting...[/yellow]")
        
        # Job analysis
        job_analysis_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
        analysis_result = job_analysis_agent.analyze_job(job_url)
        
        if analysis_result.get("error"):
            console.print(f"[red]Error analyzing job: {analysis_result['error']}[/red]")
            return
        
        job_info = analysis_result.get("job_info")
        if not job_info:
            console.print("[red]Failed to extract job information[/red]")
            return
        
        console.print(f"[green]✓ Job analyzed: {job_info.job_title} at {job_info.company_name}[/green]")
        
        console.print("\n[yellow]Step 2: Ranking experiences and projects...[/yellow]")
        
        # Ranking
        ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
        ranking_result = ranking_agent.rank_both(job_info, user_id)
        
        if ranking_result.get("error"):
            console.print(f"[red]Error ranking: {ranking_result['error']}[/red]")
            return
        
        ranked_experiences = ranking_result.get("ranked_experiences", [])
        ranked_projects = ranking_result.get("ranked_projects", [])
        
        if not ranked_experiences and not ranked_projects:
            console.print("[red]No experiences or projects found for ranking[/red]")
            return
        
        console.print(f"[green]✓ Ranked {len(ranked_experiences)} experiences and {len(ranked_projects)} projects[/green]")
        
        console.print("\n[yellow]Step 3: Generating bullet points...[/yellow]")
        
        # Generate bullet points
        resume_agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        experience_results = []
        for i in range(min(num_experiences, len(ranked_experiences))):
            experience_id = ranked_experiences[i][0]
            experience_reason = ranked_experiences[i][1]
            console.print(f"  • Processing experience {i+1}/{num_experiences}...")
            
            result = resume_agent.generate_bullet_points_for_experience(
                experience_id, 
                ranking_reason=experience_reason, 
                job_info=job_info
            )
            experience_results.append(result)
        
        project_results = []
        for i in range(min(num_projects, len(ranked_projects))):
            project_id = ranked_projects[i][0]
            project_reason = ranked_projects[i][1]
            console.print(f"  • Processing project {i+1}/{num_projects}...")
            
            result = resume_agent.generate_bullet_points_for_project(
                project_id, 
                ranking_reason=project_reason, 
                job_info=job_info
            )
            project_results.append(result)
        
        console.print("[green]✓ Bullet points generated successfully![/green]")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = ensure_data_directory()
        
        # Save to log file
        log_filename = os.path.join(data_dir, f"resume_generation_{timestamp}.log")
        with open(log_filename, "w") as f:
            f.write("Resume Generation Results\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Job: {job_info.job_title} at {job_info.company_name}\n")
            f.write(f"URL: {job_url}\n\n")
            
            f.write("Experience Results:\n")
            f.write("-" * 30 + "\n")
            for i, result in enumerate(experience_results, 1):
                f.write(f"\nExperience {i}:\n")
                f.write(f"ID: {ranked_experiences[i-1][0]}\n")
                f.write(f"Ranking Reason: {ranked_experiences[i-1][1]}\n")
                if isinstance(result, dict) and "bullet_points" in result:
                    f.write("Bullet Points:\n")
                    for bullet in result["bullet_points"]:
                        f.write(f"- {bullet}\n")
                if result.get("error"):
                    f.write(f"Error: {result['error']}\n")
                f.write("\n")
                
            f.write("\nProject Results:\n")
            f.write("-" * 30 + "\n")
            for i, result in enumerate(project_results, 1):
                f.write(f"\nProject {i}:\n")
                f.write(f"ID: {ranked_projects[i-1][0]}\n")
                f.write(f"Ranking Reason: {ranked_projects[i-1][1]}\n")
                if isinstance(result, dict) and "bullet_points" in result:
                    f.write("Bullet Points:\n")
                    for bullet in result["bullet_points"]:
                        f.write(f"- {bullet}\n")
                if result.get("error"):
                    f.write(f"Error: {result['error']}\n")
                f.write("\n")
        
        # Convert results to JSON-serializable format
        experience_results_json = []
        for result in experience_results:
            if isinstance(result, dict):
                result_copy = result.copy()
                if 'job_info' in result_copy and hasattr(result_copy['job_info'], '__dict__'):
                    result_copy['job_info'] = result_copy['job_info'].__dict__
                experience_results_json.append(result_copy)
            else:
                experience_results_json.append(result.__dict__ if hasattr(result, '__dict__') else result)
                
        project_results_json = []
        for result in project_results:
            if isinstance(result, dict):
                result_copy = result.copy()
                if 'job_info' in result_copy and hasattr(result_copy['job_info'], '__dict__'):
                    result_copy['job_info'] = result_copy['job_info'].__dict__
                project_results_json.append(result_copy)
            else:
                project_results_json.append(result.__dict__ if hasattr(result, '__dict__') else result)
        
        # Save to JSON file
        json_filename = os.path.join(data_dir, f"resume_generation_results_{timestamp}.json")
        with open(json_filename, "w") as f:
            json.dump({
                "job_info": {
                    "company_name": job_info.company_name,
                    "job_title": job_info.job_title,
                    "location": job_info.location,
                    "job_type": job_info.job_type,
                    "url": job_url
                },
                "experience_results": experience_results_json,
                "project_results": project_results_json,
                "generation_info": {
                    "timestamp": timestamp,
                    "num_experiences": len(experience_results),
                    "num_projects": len(project_results)
                }
            }, f, indent=4)
        
        console.print(f"\n[green]Resume generation complete![/green]")
        console.print(f"[dim]Log saved to: {log_filename}[/dim]")
        console.print(f"[dim]JSON saved to: {json_filename}[/dim]")
        
        # Ask if user wants to generate LaTeX resume
        if Confirm.ask("\nWould you like to generate a LaTeX resume file now?"):
            write_resume_from_results(user_id, json_filename)
        
    except Exception as e:
        console.print(f"[red]Error during resume generation: {str(e)}[/red]")

def write_resume_from_results(user_id: int, results_file: Optional[str] = None):
    """Write LaTeX resume from generated results JSON file."""
    console.print("\n[bold blue]Generate LaTeX Resume[/bold blue]")
    
    if not results_file:
        # Get JSON file path from user
        results_file = Prompt.ask("Enter path to resume generation results JSON file")
    
    try:
        # Load results
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        exp_results = data.get("experience_results", [])
        proj_results = data.get("project_results", [])
        
        if not exp_results and not proj_results:
            console.print("[red]No experience or project results found in file[/red]")
            return
        
        # Convert to format expected by ResumeWriter
        exp_list = []
        for exp_result in exp_results:
            if isinstance(exp_result, dict) and "item_id" in exp_result and "bullet_points" in exp_result:
                exp_list.append((exp_result["item_id"], exp_result["bullet_points"]))
        
        proj_list = []
        for proj_result in proj_results:
            if isinstance(proj_result, dict) and "item_id" in proj_result and "bullet_points" in proj_result:
                proj_list.append((proj_result["item_id"], proj_result["bullet_points"]))
        
        # Get output file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = ensure_data_directory()
        default_output = os.path.join(data_dir, f"resume_{timestamp}.tex")
        output_file = Prompt.ask("Enter output LaTeX file path", default=default_output)
        
        # Get template path
        template_path = Prompt.ask("Enter template path", default="template/jake_resume.tex")
        
        # Generate resume
        console.print("\n[yellow]Generating LaTeX resume...[/yellow]")
        
        resume_writer = ResumeWriter(template_path=template_path)
        resume_writer.write_resume(user_id, output_file, exp_list, proj_list)
        
        console.print(f"[green]✓ LaTeX resume generated: {output_file}[/green]")
        console.print(f"[dim]Used {len(exp_list)} experiences and {len(proj_list)} projects[/dim]")
        
        if data.get("job_info"):
            job_info = data["job_info"]
            console.print(f"[dim]Targeted for: {job_info.get('job_title', 'Unknown')} at {job_info.get('company_name', 'Unknown')}[/dim]")
        
    except FileNotFoundError:
        console.print(f"[red]File not found: {results_file}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]Invalid JSON file: {results_file}[/red]")
    except Exception as e:
        console.print(f"[red]Error generating resume: {str(e)}[/red]")

def list_generated_results():
    """List available resume generation result files."""
    console.print("\n[bold blue]Available Resume Generation Results[/bold blue]")
    
    data_dir = ensure_data_directory()
    
    # Look for JSON files with resume generation pattern
    import glob
    search_pattern = os.path.join(data_dir, "resume_generation_results_*.json")
    result_files = glob.glob(search_pattern)
    
    if not result_files:
        console.print(f"[yellow]No resume generation result files found in {data_dir}/[/yellow]")
        return
    
    table = Table(title="Resume Generation Files")
    table.add_column("File", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Job Info", style="yellow")
    
    for file in sorted(result_files, reverse=True):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            
            # Extract timestamp from filename
            filename = os.path.basename(file)
            timestamp_str = filename.replace("resume_generation_results_", "").replace(".json", "")
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = "Unknown"
            
            # Extract job info
            job_info = data.get("job_info", {})
            job_str = f"{job_info.get('job_title', 'Unknown')} at {job_info.get('company_name', 'Unknown')}"
            
            table.add_row(filename, date_str, job_str)
            
        except Exception as e:
            filename = os.path.basename(file)
            table.add_row(filename, "Error", f"Failed to read: {str(e)}")
    
    console.print(table)

@click.command()
def main():
    """Interactive CLI to collect user experience and project details and store them in the database."""
    console.print("[bold green]Welcome to the Resume Builder CLI![/bold green]")
    
    # Get or create user
    try:
        user_id = get_or_create_user()
    except Exception as e:
        console.print(f"[red]Error setting up user: {str(e)}[/red]")
        return
    
    while True:
        console.print("\n[bold]What would you like to do?[/bold]")
        console.print("1. Add Experience")
        console.print("2. Add Project")
        console.print("3. Edit Experience")
        console.print("4. Edit Project")
        console.print("5. View My Experiences")
        console.print("6. View My Projects")
        console.print("7. View All My Data")
        console.print("8. Load Data from JSON File")
        console.print("9. Export Data to JSON File")
        console.print("10. Delete All My Data")
        console.print("11. Generate Resume from Job URL")
        console.print("12. List Generated Results")
        console.print("13. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"])
        
        try:
            if choice == "1":
                exp_data = get_experience_input(user_id)
                created_exp = experience_service.create_experience(exp_data)
                console.print(f"\n[green]Experience at {created_exp.company_name} added successfully![/green]")
                
            elif choice == "2":
                proj_data = get_project_input(user_id)
                created_proj = project_service.create_project(proj_data)
                console.print(f"\n[green]Project '{created_proj.project_name}' added successfully![/green]")
                
            elif choice == "3":
                edit_experience(user_id)
                
            elif choice == "4":
                edit_project(user_id)
                
            elif choice == "5":
                console.print("\n[bold]Your Experiences:[/bold]")
                display_user_experiences(user_id)
                
            elif choice == "6":
                console.print("\n[bold]Your Projects:[/bold]")
                display_user_projects(user_id)
                
            elif choice == "7":
                console.print("\n[bold]All Your Data:[/bold]")
                display_user_experiences(user_id)
                display_user_projects(user_id)
                
            elif choice == "8":
                load_data_from_json(user_id)
                
            elif choice == "9":
                export_data_to_json(user_id)
                
            elif choice == "10":
                delete_all_user_data(user_id)
                
            elif choice == "11":
                generate_resume_from_job_url(user_id)
                
            elif choice == "12":
                list_generated_results()
                # Ask if user wants to generate resume from existing results
                import glob
                data_dir = ensure_data_directory()
                search_pattern = os.path.join(data_dir, "resume_generation_results_*.json")
                result_files = glob.glob(search_pattern)
                if result_files and Confirm.ask("\nWould you like to generate a LaTeX resume from one of these files?"):
                    file_choices = [f"{i+1}" for i in range(len(result_files))]
                    
                    console.print("\nSelect a file:")
                    for i, file in enumerate(sorted(result_files, reverse=True), 1):
                        filename = os.path.basename(file)
                        console.print(f"{i}. {filename}")
                    
                    file_choice = Prompt.ask("Enter file number", choices=file_choices)
                    selected_file = sorted(result_files, reverse=True)[int(file_choice) - 1]
                    write_resume_from_results(user_id, selected_file)
                
            elif choice == "13":
                if Confirm.ask("Are you sure you want to exit?"):
                    console.print("[green]Thank you for using Resume Builder CLI![/green]")
                    break
                    
        except Exception as e:
            console.print(f"[red]An error occurred: {str(e)}[/red]")
            console.print("[yellow]Please try again.[/yellow]")

if __name__ == "__main__":
    main() 