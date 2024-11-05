import json
import random
import re
from colorama import Fore, Style, init
from sympy import sympify, Eq, solve as sympy_solve, Symbol
from fuzzywuzzy import process

# Initialize colorama
init(autoreset=True)

class SimpleAI:
    def __init__(self, storage_file='knowledge_base.json'):
        self.knowledge_base = {}
        self.storage_file = storage_file
        self.load_knowledge()
        self.conversation_history = []
        self.context = {}

    def load_knowledge(self):
        """Load the knowledge base from the JSON file."""
        try:
            with open(self.storage_file, 'r') as file:
                self.knowledge_base = json.load(file)
        except FileNotFoundError:
            print(f"Knowledge base file '{self.storage_file}' not found. Starting with an empty knowledge base.")
            self.knowledge_base = {}
        except json.JSONDecodeError:
            print(f"Error decoding '{self.storage_file}'. Starting with an empty knowledge base.")
            self.knowledge_base = {}

    def save_knowledge(self):
        """Save the knowledge base to the JSON file."""
        with open(self.storage_file, 'w') as file:
            json.dump(self.knowledge_base, file, indent=2)

    def get_answer(self, question):
        """Get an answer from the knowledge base."""
        return self.knowledge_base.get(question.lower())

    def ask_for_answer(self, question):
        """Ask the user for an answer to an unknown question."""
        print(Fore.RED + f"I don't know the answer to '{question}'. Can you teach me?")
        answer = input(Fore.YELLOW + "Enter the answer (or press Enter to skip): ")
        if answer:
            self.knowledge_base[question.lower()] = answer
            self.save_knowledge()
            print(Fore.GREEN + "Thank you! I've learned something new.")
        else:
            print(Fore.YELLOW + "Okay, I'll try to learn that later.")

    def view_knowledge(self):
        """Display all known questions and answers."""
        print(Fore.CYAN + "\nHere's what I know:")
        for question, answer in self.knowledge_base.items():
            print(Fore.BLUE + f"Q: {question}")
            print(Fore.GREEN + f"A: {answer}\n")

    def solve_algebra(self, equation):
        """Solve a simple algebraic equation."""
        try:
            # Split the equation into left and right sides
            left, right = equation.split('=')
            
            # Convert strings to SymPy expressions
            left_expr = sympify(left.strip())
            right_expr = sympify(right.strip())
            
            # Create a SymPy equation
            eq = Eq(left_expr, right_expr)
            
            # Solve the equation
            solution = sympy_solve(eq)
            
            if solution:
                return str(solution[0])  # Return the first solution as a string
            else:
                return "No solution found"
        except Exception as e:
            return f"Error solving equation: {str(e)}"

    def evaluate_condition(self, condition):
        """Evaluate a simple condition."""
        try:
            result = eval(condition)
            return f"The condition '{condition}' is {result}"
        except Exception as e:
            return f"Error evaluating condition: {str(e)}"

    def fuzzy_match(self, question):
        """Find the closest matching question in the knowledge base."""
        if not self.knowledge_base:
            return None
        closest_match, score = process.extractOne(question, self.knowledge_base.keys())
        if score >= 80:  # You can adjust this threshold
            return closest_match
        return None

    def analyze_context(self, question):
        """Analyze the conversation history to determine context."""
        self.context = {}
        
        # Look for context clues in the last few interactions
        recent_history = self.conversation_history[-5:]
        for interaction in recent_history:
            if "topic" in interaction:
                self.context["topic"] = interaction["topic"]
            if "entity" in interaction:
                self.context["entity"] = interaction["entity"]

        # Extract potential topics or entities from the current question
        words = question.lower().split()
        for word in words:
            if word in ["it", "this", "that"] and "entity" in self.context:
                return  # Keep the existing context
        
        # If no pronouns found, update the context with potential new topic/entity
        if len(words) > 2:
            self.context["topic"] = " ".join(words[:2])
            self.context["entity"] = words[-1]

    def get_contextual_answer(self, question):
        """Get an answer considering the current context."""
        self.analyze_context(question)
        
        # Try to find an answer using the full context
        if "topic" in self.context and "entity" in self.context:
            contextual_question = f"{self.context['topic']} {question} {self.context['entity']}"
            answer = self.get_answer(contextual_question)
            if answer:
                return answer

        # If no contextual answer, fall back to regular answer
        return self.get_answer(question)

    def run(self):
        """Run the Simple AI interface with context awareness."""
        print(Fore.MAGENTA + "Welcome to SerpentScope! Type 'exit' to quit, or 'view' to see all known questions.")
        while True:
            question = input(Fore.YELLOW + "\nAsk me a question: ")
            if question.lower() == 'exit':
                print(Fore.MAGENTA + "Goodbye!")
                break
            elif question.lower() == 'view':
                self.view_knowledge()
                continue
            elif '=' in question and '==' not in question:  # Check if the question is an equation
                solution = self.solve_algebra(question)
                print(Fore.GREEN + f"The solution is: {solution}")
                self.conversation_history.append({"question": question, "answer": str(solution), "topic": "algebra"})
                continue
            elif '==' in question:  # Check if the question is a condition
                result = self.evaluate_condition(question)
                print(Fore.GREEN + result)
                self.conversation_history.append({"question": question, "answer": result, "topic": "condition"})
                continue
            
            # Attempt to get a contextual answer
            answer = self.get_contextual_answer(question)
            if answer:
                print(Fore.GREEN + f"The answer is: {answer}")
                self.conversation_history.append({"question": question, "answer": answer, "topic": self.context.get("topic", ""), "entity": self.context.get("entity", "")})
            else:
                # Attempt fuzzy matching
                matched_question = self.fuzzy_match(question)
                if matched_question:
                    answer = self.get_answer(matched_question)
                    if answer:
                        print(Fore.GREEN + f"The answer is: {answer}")
                        self.conversation_history.append({"question": question, "answer": answer, "topic": self.context.get("topic", ""), "entity": self.context.get("entity", "")})
                    else:
                        self.ask_for_answer(matched_question)
                else:  # Assume it's an unknown question
                    self.ask_for_answer(question)
            
            # Keep the conversation history to a manageable size
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

if __name__ == "__main__":
    ai = SimpleAI()
    ai.run()
