# discussion_panel.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
import time
from dotenv import load_dotenv
from termcolor import colored

load_dotenv()

PERSONA_PROMPT = """You are a {persona} with the following characteristics:
Description: {description}
Focus areas: {focus}

You are part of an AI discussion panel with the following participants:
{other_personas}

DISCUSSION TOPIC: {topic}

CURRENT DISCUSSION STATE:
{discussion_history}

Based on your expertise and the current state of the discussion, provide your insights, questions, or ideas on the topic.
Consider what has already been discussed, build upon others' ideas when appropriate, and contribute unique perspectives from your area of expertise.
Keep your response concise and focused (maximum 150 words). Format your key points clearly.

YOUR CONTRIBUTION AS {persona}:"""

class AIDiscussionPanel:
    def __init__(self, topic, num_iterations=5, model_name="gemini-2.0-flash"):
        self.topic = topic
        self.num_iterations = num_iterations
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        self.discussion_history = ""
        self.PERSONAS = {}

    def get_participant_input(self, persona_name):
        other_personas = "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.PERSONAS.items() if name != persona_name]
        )
        prompt = PromptTemplate(
            input_variables=["persona", "description", "focus", "other_personas", "topic", "discussion_history"],
            template=PERSONA_PROMPT,
        )
        try:
            formatted_prompt = prompt.format(
                persona=persona_name,
                description=self.PERSONAS[persona_name]["description"],
                focus=self.PERSONAS[persona_name]["focus"],
                other_personas=other_personas,
                topic=self.topic,
                discussion_history=self.discussion_history,
            )
            response = self.llm.invoke(formatted_prompt)
            return response.content
        except Exception as e:
            print(f"Error getting input from {persona_name}: {str(e)}")
            return f"[{persona_name} was unable to respond due to an error]"

    def format_contribution(self, persona_name, contribution):
        color = self.PERSONAS[persona_name]["color"]
        formatted = f"\n{'-'*80}\n"
        formatted += colored(f"{persona_name}:", color, attrs=["bold"])
        formatted += f"\n{contribution}\n"
        return formatted

    def run_discussion(self):
        print(f"\n{'='*80}")
        print(colored(f"AI DISCUSSION PANEL - TOPIC: {self.topic}", "white", attrs=["bold"]))
        print(f"{'='*80}\n")
        print(f"Number of iterations: {self.num_iterations}\n")

        for iteration in range(1, self.num_iterations + 1):
            print(f"\n{'='*80}")
            print(colored(f"ITERATION {iteration}/{self.num_iterations}", "white", attrs=["bold"]))
            print(f"{'='*80}")

            for persona_name in self.PERSONAS.keys():
                print(f"\nWaiting for {persona_name}'s contribution...")
                contribution = self.get_participant_input(persona_name)
                formatted_contribution = self.format_contribution(persona_name, contribution)
                print(formatted_contribution)
                self.discussion_history += f"\n{persona_name}: {contribution}"

            if iteration < self.num_iterations:
                print("\nMoving to next iteration...")
                time.sleep(5)

        print(f"\n{'='*80}")
        print(colored("DISCUSSION COMPLETED", "white", attrs=["bold"]))
        print(f"{'='*80}\n")
        return self.discussion_history

    def save_discussion(self, filename=None):
        if filename is None:
            safe_topic = "".join(c if c.isalnum() else "_" for c in self.topic)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"discussion_{safe_topic}_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write(f"AI DISCUSSION PANEL\n")
            f.write(f"Topic: {self.topic}\n")
            f.write(f"Participants: {', '.join(self.PERSONAS.keys())}\n")
            f.write(f"Number of iterations: {self.num_iterations}\n\n")
            f.write(self.discussion_history)

        print(f"Discussion saved to {filename}")
        return filename