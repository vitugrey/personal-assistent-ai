# ============ IMPORTAÇÕES ============ #
import os
import sys

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from src.assistentbot import AssistentBot

# ============ Código ============ #


class CliMenu:
    def __init__(self, assistant_bot):
        self.assistant = assistant_bot
        self.console = Console()
        self.commands: dict = {
            '1': ('Iniciar assistente por voz', self.start_voice_assistant),
            '2': ('Gerenciar diretórios', self.manage_directories),
            '3': ('Configurar personalidades', self.manage_personality),
            '4': ('Visualizar histórico', self.view_history),
            '5': ('Configurações', self.settings),
            '0': ('Sair', self.exit_program)
        }

    def display_menu(self):
        self.console.clear()
        table = Table(title="🤖 AssistentBot - Menu Principal")

        table.add_column("Opção", style="cyan")
        table.add_column("Descrição", style="white")

        for key, (description, _) in self.commands.items():
            table.add_row(key, description)

        self.console.print(table)

    def start_voice_assistant(self):
        self.console.print("\n[bold green]Iniciando assistente por voz...[/bold green]")
        self.console.print("Pressione Ctrl+C para voltar ao menu principal")
        try:
            while True:
                self.assistant.run()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Voltando ao menu principal...[/yellow]")

    def manage_directories(self):
        self.console.print("[yellow]Funcionalidade em desenvolvimento[/yellow]")
        input("\nPressione Enter para continuar...")

    def manage_personality(self):
        self.console.print("[yellow]Funcionalidade em desenvolvimento[/yellow]")
        input("\nPressione Enter para continuar...")

    def view_history(self):
        self.console.print("[yellow]Funcionalidade em desenvolvimento[/yellow]")
        input("\nPressione Enter para continuar...")
    
    def settings(self):
        self.console.print("[yellow]Funcionalidade em desenvolvimento[/yellow]")
        input("\nPressione Enter para continuar...")

    def exit_program(self):
        self.console.print("\n[bold green]Encerrando AssistentBot. Até logo![/bold green]")
        sys.exit(0)

    def run(self):
        while True:
            self.display_menu()
            choice = Prompt.ask("\nEscolha uma opeção", choices=list(self.commands.keys()))
            _, command = self.commands[choice]
            command()

            if choice == '0':
                break


if __name__ == "__main__":
    assistent_bot = AssistentBot()
    menu = CliMenu(assistent_bot)
    menu.run()
