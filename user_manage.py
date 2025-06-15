import click
from typing import List, Dict, Optional
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Import service abstractions and models
from service.user import UserService
from service.experience import ExperienceService
from service.project import ProjectService
from model.schema import User, Experience, Project

console = Console()

# Initialize services
user_service = UserService()
experience_service = ExperienceService()
project_service = ProjectService()

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
    education = Prompt.ask("Education Level (e.g., Bachelor's, Master's)")
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
        table.add_row("Location", exp.company_location)
        table.add_row("Position", exp.short_description)
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
        table.add_row("Role", proj.short_description)
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
        console.print("8. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
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
                if Confirm.ask("Are you sure you want to exit?"):
                    console.print("[green]Thank you for using Resume Builder CLI![/green]")
                    break
                    
        except Exception as e:
            console.print(f"[red]An error occurred: {str(e)}[/red]")
            console.print("[yellow]Please try again.[/yellow]")

if __name__ == "__main__":
    main() 