import re
import json
import http.client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def generate_script(prompt, video_length, target_audience, creativity, api_key):
    
    # [LANGCHAIN] SETUP GOOGLE GEMINI
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                 temperature=creativity,
                                 google_api_key=api_key)
    
    # [LANGCHAIN] PROMPT TEMPLATE FOR GENERATING VIDEO TITLE
    title_template = PromptTemplate(input_variables=["topic"],
                                    template="Generate one YouTube video title with this topic: {topic}. Please answer directly.")
    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)
    
    # [LANGCHAIN] PROMPT TEMPLATE FOR GENERATING VIDEO SCRIPT
    script_template = PromptTemplate(input_variables=["title", "duration", "search_data"],
                                     template = """
                                                Create a YouTube script with the title '{title}' that lasts {duration}.
                                                The target audience are {target_audience}.
                                                Use this as additional context: {search_data}
                                                """)
    script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True)

    # [SERPER] GET SEARCH DATA FROM SERPER
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
      "q": prompt
    })
    headers = {
      'X-API-KEY': '1469508ac2361b6216e234933538fbf89f302251',
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode('utf-8'))
    if 'knowledgeGraph' in data:
        search_data = data['knowledgeGraph']['description']
        search_data = re.sub(r'\s*[^.]*\.\.\.$', '', search_data)
    else:
        search_data = "None"
    
    # [LANGCHAIN] GENERATE THE TITLE
    title = title_chain.run({"topic": prompt})
    
    # [LANGCHAIN] GENERATE THE SCRIPT
    script = script_chain.run({"title": title,
                               "duration": video_length,
                               "target_audience": target_audience,
                               "search_data": search_data})
    
    return title, script, search_data