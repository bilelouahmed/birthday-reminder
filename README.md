# Birthday Reminder (WIP)
Birthday reminder and chatbot for Whatsapp family groups based on RAG and Graph Knowledge.

## Setup and Run

First, clone this repository to your local machine and navigate into the project directory.

```git clone https://github.com/bilelouahmed/birthday-reminder.git```

```cd snake-ai```

Setup your credentials using these variable names :

```OPENAI_KEY=<YOUR_OPENAI_KEY>```

```NEO4J_URI=<YOUR NEO4J URI>```

```NEO4J_USERNAME=<YOUR NEO4J USERNAME>```

```NEO4J_PASSWORD=<YOUR NEO4J PASSWORD>```

Enter your group members' birthdays in the graph/birthday.txt file, add the phone numbers of the individuals you wish to notify about birthdays to lists/notified.txt, and include the phone numbers of those permitted to use the chatbot in lists/whitelist.txt.

If the Neo4j graph you're going to use to support RAG isn't ready yet, you can set it up using the graph_creation.ipynb notebook.

Finally, make sure you have Docker installed. You can now launch your Docker Compose :

```docker-compose up --build```

TO DO :

- Take into account history