import asyncio
import os
from typing import Dict, Any
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled, trace, WebSearchTool
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Configure OpenAI clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"  # or your preferred OpenAI model

if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your environment variables.")

# Create separate clients for Perplexity and OpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
set_tracing_disabled(disabled=True)


class ScriptCheckerOutput(BaseModel):
    good_quality: bool
    feedback: str

class CleanScript(BaseModel):
    script_only: str


class ResearchAgent:
    def __init__(self):
        self.agent = Agent(
            name="Market Research Analyst",
            instructions="""You are an expert market research analyst. Your task is to analyze product information and generate actionable market insights.
            For each analysis, consider:
            1. The product's unique selling points and value proposition
            2. Potential customer motivations and pain points
            3. Key market trends or opportunities
            4. Possible challenges or competitive threats
            5. Suggested marketing strategies and positioning
            
            Provide detailed explanations and support your insights with clear reasoning.
            """,
            model=OPENAI_MODEL,
            tools=[WebSearchTool()]
        )
    
    async def generate(self, info):
        """Generate market research insights for a product.
        
        Args:
            info (Dict[str, Any]): Product information dictionary
            
        Returns:
            str: Generated market research insights
        """
        prompt = f"""Please analyze the following product and provide comprehensive market research insights:
        
        Product Information:
        - Name: {info['product_name']}
        - Language: {info['language']}
        - Description: {info['description']}
        - Price: {info['price']}
        - Promotion: {info['promotion_detail']}
        - Target Audience: {info['target_audience']}

        Provide a detailed analysis covering all key aspects of market research."""
        
        result = await Runner.run(self.agent, prompt)
        return result.final_output

class OutlineGeneratorAgent:
    def __init__(self, info):
        self.info = info
        self.agent = Agent(
            name="Script Outline Generator",
            instructions= """
                You are a PhD in marketing and expert in generating short marketing video scripts
                based on product information and market insights. 
            """,
            model=OPENAI_MODEL
        ) 


class EvaluatorAgent:
    def __init__(self, info):
        self.info = info
        self.agent = Agent(
            name="Marketing Script Evaluator",
            instructions="""
                Read the given marketing script outline, and judge the quality based on the level of engagement.
                Think of it this way: if you saw the script in a video, would you be interested in learning more?
            """,
            model=OPENAI_MODEL,
            output_type=ScriptCheckerOutput
        )


class GeneratorAgent:
    def __init__(self, info):
        self.info = info
        self.agent = Agent(
            name="Marketing Video Generator",
            instructions="""You are a PhD in marketing and expert in generating short marketing video scripts
            based on product information, market insights, and outline. Focus on creating compelling, concise scripts
            that effectively communicate the product's value proposition and appeal to the target audience.""",
            model=OPENAI_MODEL
        )


class GenerateScript:
    def __init__(self, info):
        self.info = info
    
    async def generate(self):
        with trace("Script Generation Flow"):
            # 1. Generate Market Research
            research_prompt = f"""
                You are a market research analyst. Based on the following product information, generate actionable 
                market insights to help guide marketing strategy and positioning
                - Product Name: {self.info['product_name']}
                - Language: {self.info['language']}
                - Description: {self.info['description']}
                - Price: {self.info['price']}
                - Promotion Detail: {self.info['promotion_detail']}
                - Target Audience: {self.info['target_audience']}
                Please analyze:
                1. The product's unique selling points and value proposition
                2. Potential customer motivations and pain points
                3. Key market trends or opportunities relevant to this product and audience
                4. Possible challenges or competitive threats
                5. Suggested marketing strategies and positioning
                Your response should be in full sentences explaining the insights in details
            """

            market_research_result = await Runner.run(
                ResearchAgent().agent,
                research_prompt
            )

            outline_prompt = f"""
                You are a marketing script outline generator. You are provided with the details of a product:

                - Product Name: {self.info['product_name']}
                - Language: {self.info['language']}
                - Description: {self.info['description']}
                - Price: {self.info['price']}
                - Promotion Detail: {self.info['promotion_detail']}
                - Target Audience: {self.info['target_audience']}
                
                You are provided with the market research insights:
                {market_research_result.final_output}

                Please generate a full marketing script outline that clearly describes the flow of the marketing pitch.
                Your response should only be an outline, not a full script. If you think the outline is not good, please provide feedback.
            """

            # 2. Generate The Outline
            script_outline = await Runner.run(
                OutlineGeneratorAgent(self.info).agent,
                outline_prompt
            )

            script_outline_checker = await Runner.run(
                EvaluatorAgent(self.info).agent,
                script_outline.final_output
            )

            # 3. Evaluate the Outline
            # if not script_outline_checker.final_output.good_quality:
            #     print("No Bueno")
            #     exit(0)

            print(script_outline_checker.final_output.good_quality)
            
            generation_prompt = f"""
                You are a PhD in marketing and expert in generating short marketing video scripts
                You are given the following information:
                - Product Name: {self.info['product_name']}
                - Language: {self.info['language']}
                - Description: {self.info['description']}
                - Price: {self.info['price']}
                - Promotion Detail: {self.info['promotion_detail']}
                - Target Audience: {self.info['target_audience']}
                
                You are also given the following market research insights:
                {market_research_result.final_output}
                
                You are also given the following script outline:
                {script_outline.final_output}

                **Important:**  
                - Write only the lines the speaker would say — no descriptions, no labels, no explanation and no titles for each section.
                - Use the given language: {self.info['language']}
                - Make the script sound natural, engaging, and tailored for the target audience.
                - Make sure that the duration of the script is around 30 seconds.    
            """
            # 4. Generate the Script
            script = await Runner.run(
                GeneratorAgent(self.info).agent,
                generation_prompt
            )

            return script.final_output

async def main():
    # Example usage
    agent = ResearchAgent()
    info = {
        "product_name": "LuxeStride Eco Sneakers",
        "language": "English",
        "description": "Stylish, ultra-lightweight sneakers crafted from recycled ocean plastics and vegan leather. Designed with breathable mesh and ergonomic soles for all-day comfort and sustainability.",
        "price": "$129.00",
        "promotion_detail": "Grand opening special: 15 percent off and a free organic cotton tote bag with every order.",
        "target_audience": "Eco-conscious millennials, urban trendsetters, and young professionals aged 20-35"
    }
    
    print("=== Market Research Analysis ===")
    generator = GenerateScript(info)
    script = await generator.generate()
    print("=== Generated Script ===")
    print(script)

if __name__ == "__main__":
    asyncio.run(main())
