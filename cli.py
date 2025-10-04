"""
Command Line Interface for Bangladesh Constitution Chatbot
Provides an easy-to-use CLI for local interaction
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config import Config
from src.chatbot import ConstitutionChatbot
from validate_env import validate_environment

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🏛️  BANGLADESH CONSTITUTION CHATBOT - CLI v1.0              ║
║                                                                  ║
║     Your AI assistant for Constitutional queries                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

def print_help():
    """Print help information"""
    help_text = f"""
{Colors.OKCYAN}{Colors.BOLD}Available Commands:{Colors.ENDC}
  {Colors.OKGREEN}query <question>{Colors.ENDC}    - Ask a question about the Constitution
  {Colors.OKGREEN}history{Colors.ENDC}              - Show recent conversation history
  {Colors.OKGREEN}stats{Colors.ENDC}                - Display system statistics
  {Colors.OKGREEN}clear{Colors.ENDC}                - Clear conversation history
  {Colors.OKGREEN}help{Colors.ENDC}                 - Show this help message
  {Colors.OKGREEN}exit / quit{Colors.ENDC}          - Exit the application

{Colors.OKCYAN}{Colors.BOLD}Examples:{Colors.ENDC}
  query What are the fundamental rights?
  query Article 27 সম্পর্কে বলুন
  
{Colors.OKCYAN}{Colors.BOLD}Tips:{Colors.ENDC}
  • You can ask questions in English or Bengali
  • Refer to specific articles for detailed information
  • Use simple, clear questions for best results
"""
    print(help_text)

def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text"""
    print(f"{color}{text}{Colors.ENDC}")

def format_answer(result: dict) -> str:
    """Format answer with nice styling"""
    lines = []
    
    # Header
    lines.append(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    lines.append(f"{Colors.BOLD}{Colors.OKCYAN}📖 Answer{Colors.ENDC}")
    lines.append(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
    # Answer text
    lines.append(result['answer'])
    
    # Metadata
    lines.append(f"\n{Colors.HEADER}{'-' * 70}{Colors.ENDC}")
    lines.append(f"{Colors.OKBLUE}📊 Metadata:{Colors.ENDC}")
    lines.append(f"  • Language: {result.get('language', 'unknown')}")
    lines.append(f"  • Sources: {result.get('num_sources', 0)} constitutional provisions")
    lines.append(f"  • Processing time: {result.get('processing_time', 0):.2f}s")
    lines.append(f"  • Scope: {result.get('scope', 'unknown')}")
    lines.append(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
    return '\n'.join(lines)

def interactive_mode(chatbot: ConstitutionChatbot, use_llm: bool = True):
    """Run interactive mode"""
    print_colored("\n🎯 Interactive Mode - Type 'help' for commands, 'exit' to quit\n", Colors.OKGREEN)
    
    while True:
        try:
            # Get user input
            user_input = input(f"{Colors.BOLD}💬 You: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            # Parse command
            command = user_input.lower()
            
            # Exit commands
            if command in ['exit', 'quit', 'q']:
                print_colored("\n👋 Thank you for using Bangladesh Constitution Chatbot!", Colors.OKGREEN)
                # Show final stats
                stats = chatbot.get_session_stats()
                print_colored(f"\n📊 Session Summary:", Colors.OKCYAN)
                print(f"  • Queries processed: {stats.get('queries_processed', 0)}")
                print(f"  • Session duration: {stats.get('session_duration_minutes', 0):.1f} minutes")
                print(f"  • Languages used: {', '.join(stats.get('languages_detected', set()))}")
                break
            
            # Help command
            elif command == 'help':
                print_help()
                continue
            
            # History command
            elif command == 'history':
                history = chatbot.get_conversation_history(10)
                if not history:
                    print_colored("\n📜 No conversation history yet", Colors.WARNING)
                else:
                    print_colored(f"\n📜 Recent Conversations (last {len(history)}):", Colors.OKCYAN)
                    for i, conv in enumerate(history, 1):
                        print(f"\n{Colors.BOLD}{i}. {Colors.ENDC}{conv['query'][:60]}...")
                        print(f"   Lang: {conv['language']}, Sources: {conv['sources']}")
                        print(f"   Time: {conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                continue
            
            # Stats command
            elif command == 'stats':
                stats = chatbot.get_session_stats()
                print_colored(f"\n📊 System Statistics:", Colors.OKCYAN)
                for key, value in stats.items():
                    if key not in ['session_start', 'languages_detected']:
                        print(f"  • {key}: {value}")
                    elif key == 'languages_detected':
                        print(f"  • {key}: {', '.join(value)}")
                continue
            
            # Clear command
            elif command == 'clear':
                chatbot.clear_conversation_history()
                print_colored("\n🗑️ Conversation history cleared", Colors.OKGREEN)
                continue
            
            # Query command (everything else)
            else:
                # Remove 'query' prefix if present
                if user_input.lower().startswith('query '):
                    user_input = user_input[6:].strip()
                
                if not user_input:
                    print_colored("⚠️ Please provide a question", Colors.WARNING)
                    continue
                
                # Process query
                print_colored("\n🤔 Processing your question...\n", Colors.OKCYAN)
                
                result = chatbot.process_query(user_input, use_llm=use_llm)
                
                # Display result
                print(format_answer(result))
        
        except KeyboardInterrupt:
            print_colored("\n\n👋 Interrupted by user. Goodbye!", Colors.WARNING)
            break
        except Exception as e:
            print_colored(f"\n❌ Error: {str(e)}", Colors.FAIL)
            logging.error(f"CLI error: {e}", exc_info=True)

def single_query_mode(chatbot: ConstitutionChatbot, question: str, use_llm: bool = True):
    """Process a single query and exit"""
    print_colored(f"\n💬 Question: {question}\n", Colors.BOLD)
    print_colored("🤔 Processing...\n", Colors.OKCYAN)
    
    result = chatbot.process_query(question, use_llm=use_llm)
    print(format_answer(result))

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Bangladesh Constitution Chatbot - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python cli.py
  
  # Single query mode
  python cli.py -q "What are fundamental rights?"
  
  # Without LLM (faster, simpler responses)
  python cli.py --no-llm
  
  # Validate environment
  python cli.py --validate-env
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Ask a single question and exit"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM for faster responses (retrieval only)"
    )
    
    parser.add_argument(
        "--validate-env",
        action="store_true",
        help="Validate environment configuration"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Don't show banner"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cli.log'),
            logging.StreamHandler() if args.debug else logging.NullHandler()
        ]
    )
    
    # Show banner
    if not args.no_banner and not args.query:
        print_banner()
    
    # Validate environment if requested
    if args.validate_env:
        print_colored("🔍 Validating environment configuration...\n", Colors.OKCYAN)
        can_run = validate_environment(auto_fix=True)
        if not can_run:
            print_colored("\n❌ Environment validation failed. Please fix errors above.", Colors.FAIL)
            return 1
        print_colored("\n✅ Environment validation passed!\n", Colors.OKGREEN)
        if not args.query:
            return 0
    
    # Initialize chatbot
    try:
        print_colored("🔧 Initializing chatbot...", Colors.OKCYAN)
        config = Config()
        chatbot = ConstitutionChatbot(config)
        
        if not chatbot.is_ready():
            print_colored("⚠️ Chatbot not fully initialized - some features may be limited", Colors.WARNING)
        else:
            print_colored("✅ Chatbot ready!", Colors.OKGREEN)
        
        # Show system info
        stats = chatbot.get_session_stats()
        if not args.no_banner and not args.query:
            print_colored(f"\n📊 System Status: {stats.get('system_status', 'unknown')}", Colors.OKBLUE)
            print_colored(f"🤖 LLM Mode: {'enabled' if not args.no_llm else 'disabled'}\n", Colors.OKBLUE)
        
    except Exception as e:
        print_colored(f"❌ Failed to initialize chatbot: {e}", Colors.FAIL)
        logging.error(f"Initialization error: {e}", exc_info=True)
        return 1
    
    # Run appropriate mode
    try:
        use_llm = not args.no_llm
        
        if args.query:
            # Single query mode
            single_query_mode(chatbot, args.query, use_llm)
        else:
            # Interactive mode
            interactive_mode(chatbot, use_llm)
        
        return 0
        
    except Exception as e:
        print_colored(f"\n❌ Fatal error: {e}", Colors.FAIL)
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
