"""Command-line interface for PostgreSQL Performance Analyzer."""

import click
import os
import sys
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from .utils.db_connection import DatabaseConnection
from .analyzers import StructureAnalyzer, SecurityAnalyzer, PerformanceAnalyzer, NamingAnalyzer
from .ai import LocalAIProvider, CloudAIProvider
from .reports import ReportBuilder, ReportFormatter

console = Console()


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PostgreSQL Performance Analyzer - AI-powered database analysis tool."""
    pass


@main.command()
@click.option('--host', default='localhost', help='Database host')
@click.option('--port', default=5432, type=int, help='Database port')
@click.option('--database', required=True, help='Database name')
@click.option('--user', required=True, help='Database user')
@click.option('--password', help='Database password (or use PGPASSWORD env var)')
@click.option('--sslmode', default='prefer', help='SSL mode')
@click.option('--ai-provider', type=click.Choice(['local', 'cloud']), default='cloud', 
              help='AI provider to use')
@click.option('--ai-model', help='AI model name (optional)')
@click.option('--api-key', help='API key for cloud AI provider (or use OPENAI_API_KEY env var)')
@click.option('--output', '-o', default='report.md', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['markdown', 'html', 'json']), 
              default='markdown', help='Output format')
@click.option('--skip-ai', is_flag=True, help='Skip AI analysis and generate raw report only')
def analyze(host, port, database, user, password, sslmode, ai_provider, ai_model, 
           api_key, output, format, skip_ai):
    """Analyze PostgreSQL database and generate performance report."""
    
    console.print(Panel.fit(
        "[bold blue]PostgreSQL Performance Analyzer[/bold blue]\n"
        "AI-powered database analysis and optimization",
        border_style="blue"
    ))
    
    # Get password from environment if not provided
    if not password:
        password = os.environ.get('PGPASSWORD', '')
    
    # Database configuration
    db_config = {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password,
        'sslmode': sslmode
    }
    
    # Initialize report builder
    report_builder = ReportBuilder()
    
    try:
        # Connect to database
        console.print("\n[bold]Connecting to database...[/bold]")
        with DatabaseConnection(db_config) as db:
            # Test connection
            if not db.test_connection():
                console.print("[red]Failed to connect to database[/red]")
                sys.exit(1)
            
            console.print("[green]✓ Connected successfully[/green]")
            
            # Get server version
            server_version = db.get_server_version()
            console.print(f"[dim]Server: {server_version}[/dim]\n")
            
            # Set report metadata
            report_builder.set_metadata(db_config, server_version)
            
            # Run analyses
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Structure Analysis
                task = progress.add_task("[cyan]Analyzing database structure...", total=None)
                structure_analyzer = StructureAnalyzer(db)
                structure_results = structure_analyzer.analyze()
                report_builder.add_structure_analysis(structure_results)
                progress.update(task, completed=True)
                console.print("[green]✓ Structure analysis complete[/green]")
                
                # Security Analysis
                task = progress.add_task("[cyan]Analyzing database security...", total=None)
                security_analyzer = SecurityAnalyzer(db)
                security_results = security_analyzer.analyze()
                report_builder.add_security_analysis(security_results)
                progress.update(task, completed=True)
                console.print("[green]✓ Security analysis complete[/green]")
                
                # Performance Analysis
                task = progress.add_task("[cyan]Analyzing database performance...", total=None)
                performance_analyzer = PerformanceAnalyzer(db)
                performance_results = performance_analyzer.analyze()
                report_builder.add_performance_analysis(performance_results)
                progress.update(task, completed=True)
                console.print("[green]✓ Performance analysis complete[/green]")
                
                # Naming Standards Analysis
                task = progress.add_task("[cyan]Analyzing naming standards...", total=None)
                naming_analyzer = NamingAnalyzer(db)
                naming_results = naming_analyzer.analyze()
                report_builder.add_naming_analysis(naming_results)
                progress.update(task, completed=True)
                console.print("[green]✓ Naming standards analysis complete[/green]")
        
        # Generate summary
        console.print("\n[bold]Generating summary...[/bold]")
        report_builder.generate_summary()
        
        # Display quick summary
        _display_summary(report_builder)
        
        # AI Analysis
        if not skip_ai:
            console.print("\n[bold]Generating AI recommendations...[/bold]")
            
            # Initialize AI provider
            ai = _initialize_ai_provider(ai_provider, ai_model, api_key)
            
            if ai and ai.is_available():
                console.print(f"[dim]Using: {ai.get_provider_name()}[/dim]\n")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    
                    # Structure recommendations
                    task = progress.add_task("[cyan]Generating structure recommendations...", total=None)
                    try:
                        structure_rec = ai.analyze(structure_results, "structure")
                        report_builder.add_ai_recommendation("structure", structure_rec, ai.get_provider_name())
                        progress.update(task, completed=True)
                        console.print("[green]✓ Structure recommendations generated[/green]")
                    except Exception as e:
                        console.print(f"[yellow]⚠ Structure recommendations failed: {e}[/yellow]")
                    
                    # Security recommendations
                    task = progress.add_task("[cyan]Generating security recommendations...", total=None)
                    try:
                        security_rec = ai.analyze(security_results, "security")
                        report_builder.add_ai_recommendation("security", security_rec, ai.get_provider_name())
                        progress.update(task, completed=True)
                        console.print("[green]✓ Security recommendations generated[/green]")
                    except Exception as e:
                        console.print(f"[yellow]⚠ Security recommendations failed: {e}[/yellow]")
                    
                    # Performance recommendations
                    task = progress.add_task("[cyan]Generating performance recommendations...", total=None)
                    try:
                        performance_rec = ai.analyze(performance_results, "performance")
                        report_builder.add_ai_recommendation("performance", performance_rec, ai.get_provider_name())
                        progress.update(task, completed=True)
                        console.print("[green]✓ Performance recommendations generated[/green]")
                    except Exception as e:
                        console.print(f"[yellow]⚠ Performance recommendations failed: {e}[/yellow]")
            else:
                console.print("[yellow]⚠ AI provider not available, skipping AI recommendations[/yellow]")
        
        # Generate report
        console.print("\n[bold]Generating report...[/bold]")
        formatter = ReportFormatter(report_builder.get_report_data())
        
        if format == 'markdown':
            report_content = formatter.to_markdown()
        elif format == 'html':
            report_content = formatter.to_html()
        elif format == 'json':
            report_content = formatter.to_json()
        
        # Save report
        with open(output, 'w') as f:
            f.write(report_content)
        
        console.print(f"\n[bold green]✓ Report generated: {output}[/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option('--ai-provider', type=click.Choice(['local', 'cloud']), default='local',
              help='AI provider to check')
def check_ai(ai_provider):
    """Check AI provider availability and configuration."""
    
    console.print(Panel.fit(
        "[bold blue]AI Provider Check[/bold blue]",
        border_style="blue"
    ))
    
    if ai_provider == 'local':
        console.print("\n[bold]Checking Local AI (Ollama)...[/bold]")
        ai = LocalAIProvider()
        
        if ai.is_available():
            console.print("[green]✓ Ollama is available[/green]")
            models = ai.list_available_models()
            if models:
                console.print(f"\n[bold]Available models:[/bold]")
                for model in models:
                    console.print(f"  • {model}")
            else:
                console.print("[yellow]⚠ No models found[/yellow]")
        else:
            console.print("[red]✗ Ollama is not available[/red]")
            console.print("\n[dim]Install Ollama from: https://ollama.ai[/dim]")
    
    elif ai_provider == 'cloud':
        console.print("\n[bold]Checking Cloud AI...[/bold]")
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            console.print("[red]✗ OPENAI_API_KEY environment variable not set[/red]")
            console.print("\n[dim]Set your API key: export OPENAI_API_KEY='your-key-here'[/dim]")
        else:
            ai = CloudAIProvider({'api_key': api_key})
            if ai.is_available():
                console.print("[green]✓ Cloud AI is configured[/green]")
                console.print(f"[dim]Provider: {ai.get_provider_name()}[/dim]")
            else:
                console.print("[red]✗ Cloud AI configuration failed[/red]")


def _initialize_ai_provider(provider_type: str, model: Optional[str], api_key: Optional[str]):
    """Initialize AI provider based on configuration."""
    
    if provider_type == 'local':
        config = {}
        if model:
            config['model'] = model
        return LocalAIProvider(config)
    
    elif provider_type == 'cloud':
        # Get API key from parameter or environment
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            console.print("[yellow]⚠ No API key provided for cloud AI[/yellow]")
            return None
        
        config = {'api_key': api_key}
        if model:
            config['model'] = model
        
        return CloudAIProvider(config)
    
    return None


def _display_summary(report_builder: ReportBuilder):
    """Display quick summary of analysis results."""
    
    summary = report_builder.report_data.get('summary', {})
    
    table = Table(title="Analysis Summary", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Database Size", str(summary.get('database_size', 'N/A')))
    table.add_row("Tables", str(summary.get('table_count', 0)))
    table.add_row("Indexes", str(summary.get('index_count', 0)))
    
    if summary.get('security_issues'):
        table.add_row("Security Issues", str(len(summary['security_issues'])), style="yellow")
    
    if summary.get('performance_issues'):
        table.add_row("Performance Issues", str(len(summary['performance_issues'])), style="yellow")
    
    console.print("\n", table)


if __name__ == '__main__':
    main()
