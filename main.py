import os
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from crewai_tools.tools import WebsiteSearchTool, SerperDevTool, FileReadTool
import pandas as pd 
import json 
import streamlit as st
from langchain_groq import ChatGroq



serper_dev_tool = SerperDevTool()

llm = ChatGroq(model_name="mixtral-8x7b-32768", temperature=0.2) 


os.environ['SERPER_API_KEY'] = st.secrets["SERPER_API_KEY"]
os.environ['GROQ_API_KEY'] = st.secrets["GROQ_API_KEY"]

def create_crew(OUTPUT_FOLDER):
  # Load an Excel file into a DataFrame
  #df = pd.read_excel('tasks.xlsx')
  agent_load= json.loads(open("agents.json", "r").read())
  agents={}
  for agent in agent_load: 
    agents[agent['agent_name']] = Agent(
      role=agent['agent_name'],
      backstory=agent['Backstory'],
      goal=agent['Goal'],
      allow_delegation=False,
      verbose=True,
      llm=llm,
      memory=True,
      tools=[serper_dev_tool]
    )
  tasks={}
  tasks_load=json.loads(open("tasks.json", "r").read())
  for row in tasks_load:
    tasks[row['task_variable_name']] = Task(
      description=row['task_description'],
      agent=agents[row['agent']],
      memory=True,
      final_answer='Your final answer must well formated and clear',
      expected_output=row['excpected_output'],
      output_file=f"{OUTPUT_FOLDER}/{row['doc_title']}.txt"
    )
  return agents, tasks 


def crewai_setup( business_overview="I run a digital AI startup called YourMVP.com", start_with="ALL", OUTPUT_FOLDER="out"):
  agents, tasks = create_crew(OUTPUT_FOLDER) 
  
  def create_tasks_list_from_start_with(start_with):
    i=0
    for task_name in tasks.keys():
      if task_name == start_with:
        return i 
      i+=1 
    return None 


  if start_with=="ALL":
  # Instantiate your crew with a sequential process
    crew = Crew(
      agents=[a for a in agents.values()],
      tasks=[t for t in tasks.values()],
      verbose=True
    )
  else: 
    i = create_tasks_list_from_start_with(start_with)
    crew = Crew(
      agents=[a for a in agents.values()],
      tasks=[t for t in tasks.values()][i:],
      verbose=True
    )

  # Get your crew to work!
  result = crew.kickoff({"business overview": business_overview })

  print("######################")
  return result

if __name__=="__main__":
  crewai_setup()
