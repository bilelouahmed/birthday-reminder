from __init__ import *
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
import re

GET_CYPHER_PROMPT = f"""Your goal is to generate a Cypher query to get context from a graph database. 

In fact, questions may require specific context about a random person that you don't know. So, generate a Cypher query to retrieve information from a Neo4j graph database. Enclose this Cypher query between triple backticks (```) to make it easy to extract. Here is the schema definition provided :
**SCHEMA**

Only utilize the relationship types and properties that are provided. Do not use ANY other types or properties not included in the schema.
        
If you can't generate a proper Cypher query with this schema, just tell you can't but do NOT try to invent node properties nor relationships.

Be as concise you can."""

GET_ANSWER_PROMPT = f"""You are Titeuf, an assistant for a family group on WhatsApp engaging in friendly conversation with the user.

Sometimes, context is given to you because we think you might need it to answer. Please, use it when it's disponible.

Note : Do not include any explanations or apologies in your responses. Additionally, responses should be provided in the language of the user. To finish, be as concise you can."""


class Neo4jGPTQuery:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
        )
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125", temperature=0.5, api_key=OPENAI_KEY
        )
        self.schema = self.graph.schema

    def refresh_schema(self):
        self.schema = self.graph.refresh_schema()

    def get_system_message(self, option: str):
        if option == "CONTEXT":
            return GET_CYPHER_PROMPT.replace("**SCHEMA**", self.schema)
        elif option == "ANSWER":
            return GET_ANSWER_PROMPT

    def query_database(self, neo4j_query):
        return graph.query(neo4j_query)

    def create_cypher(self, question: str, history=None):
        messages = [
            {"role": "system", "content": self.get_system_message(option="CONTEXT")},
            {"role": "user", "content": f"Question : {question}"},
        ]

        if history:
            messages.extend(history)

        return self.llm.invoke(messages).content

    def answer(self, question: str, context: str = None):
        user_message = (
            f"{question}\n\nContext :\n{context}" if context is not None else question
        )
        messages = [
            {"role": "system", "content": self.get_system_message(option="ANSWER")},
            {"role": "user", "content": user_message},
        ]

        return self.llm.invoke(messages).content

    def run(self, question, history=None, retry=True):
        first_generation = self.create_cypher(question, history)

        ""
        matches = re.findall(r"```([\s\S]+?)```", first_generation)

        if len(matches) == 0:
            context = None
            return self.answer(question, context)
        else:
            cypher_query = matches[0].strip()
            try:
                context = self.query_database(cypher_query)
                print("Context :", context)
                return self.answer(question, context)

            except Exception as e:
                if not retry:
                    return "Invalid Cypher syntax"
