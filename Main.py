import os
from typing import Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

load_dotenv()

# Get API keys - Both are FREE!
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Free from https://console.groq.com
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Free 2500 searches from https://serper.dev

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Get free API key from https://console.groq.com")
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found. Get free API key from https://serper.dev")

# Initialize LLM with Groq (FREE and FAST!)
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

# Initialize tools
search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool()

# Create Research Agent
researcher = Agent(
    role="Newsletter Research Specialist",
    goal="Find the most relevant and recent information about {topic}",
    backstory="""You are an expert researcher with years of experience in 
    gathering high-quality information from credible sources. You excel at 
    finding trending topics, expert opinions, and data-driven insights.""",
    tools=[search_tool, scrape_tool],
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Create Writer Agent
writer = Agent(
    role="Newsletter Content Writer",
    goal="Create an engaging and well-structured newsletter about {topic}",
    backstory="""You are a skilled content writer specializing in newsletters.
    You know how to structure content for maximum engagement, use compelling 
    headlines, and present information in an accessible way.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

def NewsletterGenerator(topic: str, customization: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a newsletter based on the given topic.
    
    Args:
        topic (str): The topic to generate the newsletter about
        customization (Dict): Optional customization parameters
    
    Returns:
        Dict[str, Any]: Newsletter content
    """
    if customization is None:
        customization = {}
    
    # Extract customization options
    tone = customization.get("tone", "Professional")
    length = customization.get("length", "Medium (1000 words)")
    focus = customization.get("focus", "Balanced")
    include_images = customization.get("include_images", False)
    include_cta = customization.get("include_cta", False)
    include_stats = customization.get("include_stats", True)
    include_quotes = customization.get("include_quotes", True)
    template = customization.get("template", "Standard")
    custom_sections = customization.get("custom_sections", None)
    
    # Build custom instructions based on options
    style_instructions = f"""
    Writing Style:
    - Tone: {tone}
    - Length: {length}
    - Focus: {focus}
    {'- Include image placeholders with [Image: description]' if include_images else ''}
    {'- Include a clear call-to-action at the end' if include_cta else ''}
    {'- Emphasize statistics and data points' if include_stats else ''}
    {'- Include expert quotes when available' if include_quotes else ''}
    """
    
    # Define templates
    templates = {
        "Standard": """
        # [Compelling Subject Line]
        
        ## Welcome
        [Engaging introduction]
        
        ## [Main Story]
        [Key insights and analysis]
        
        ## Featured Content
        [Deeper exploration]
        
        ## Quick Updates
        [Bullet points with actionable insights]
        
        ## This Week's Highlights
        [Notable developments]
        
        ## Sources & Further Reading
        [Properly cited sources]
        """,
        
        "Tech News": """
        # 🚀 [Tech Headline]
        
        ## 💡 The Big Picture
        [Context and why it matters]
        
        ## 🔬 Deep Dive
        [Technical analysis]
        
        ## 💼 Industry Impact
        [Business implications]
        
        ## 🛠️ What You Can Do
        [Actionable takeaways]
        
        ## 📰 More Headlines
        [Quick hits]
        
        ## 🔗 Resources
        [Links and sources]
        """,
        
        "Business Weekly": """
        # 📊 [Business Headline]
        
        ## Executive Summary
        [Quick overview]
        
        ## Market Analysis
        [Trends and movements]
        
        ## Company Spotlight
        [Featured business/leader]
        
        ## Investment Insights
        [Financial implications]
        
        ## Week Ahead
        [What to watch]
        
        ## Sources
        [References]
        """,
        
        "Research Digest": """
        # 🔬 [Research Topic]
        
        ## Abstract
        [Summary of key findings]
        
        ## Key Research
        [Main studies and papers]
        
        ## Methodology Spotlight
        [Interesting approaches]
        
        ## Implications
        [What this means]
        
        ## Future Directions
        [What's next]
        
        ## References
        [Academic sources]
        """,
        
        "Custom": custom_sections if custom_sections else "Standard"
    }
    
    selected_template = templates.get(template, templates["Standard"])
    
    try:
        # Research Task
        research_task = Task(
            description=f"""Research the latest developments, trends, and insights about {topic}.
            
            Your research should include:
            1. Recent news and developments (last 7 days preferred)
            2. Expert opinions and quotes
            3. Statistics and data points
            4. Industry trends and analysis
            5. Multiple credible sources
            
            {style_instructions}
            
            Provide a comprehensive summary with all sources.""",
            agent=researcher,
            expected_output="A detailed research report with sources"
        )
        
        # Writing Task
        writing_task = Task(
            description=f"""Using the research provided, create a compelling newsletter about {topic}.
            
            {style_instructions}
            
            Use this structure:
            {selected_template}
            
            Guidelines:
            - Use markdown formatting
            - Include specific quotes and data
            - Keep it engaging and accessible
            - Cite all sources properly with links
            - Make section titles specific to the topic
            - Match the {tone.lower()} tone throughout
            - Aim for approximately {length.split('(')[1].split(')')[0]}
            - Focus on {focus.lower()} content""",
            agent=writer,
            expected_output="A complete, well-formatted newsletter in markdown",
            context=[research_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff(inputs={"topic": topic})
        
        return {
            "content": str(result),
            "status": "success",
            "customization": customization
        }
    except Exception as e:
        return {
            "content": f"Error generating newsletter: {str(e)}",
            "status": "error"
        }

if __name__ == "__main__":
    result = NewsletterGenerator("Latest developments in AI")
    print(result["content"])
