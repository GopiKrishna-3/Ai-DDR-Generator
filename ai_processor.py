import os
import time
import random
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class AIProcessor:
    def __init__(self, api_key, model="gemini-1.5-flash", api_version=None, temperature=0.1, strict_mode=False):
        self.api_key = api_key
        self.model = model
        self.api_version = api_version
        self.temperature = temperature
        self.temperature = temperature
        self.strict_mode = strict_mode
        # Standard cleaning to reduce token overhead
        self.clean_regex = re.compile(r'\s+')
        
        # Build configuration for version independence & safety
        kwargs = {
            "model": self.model,
            "google_api_key": self.api_key,
            "temperature": self.temperature,
            "request_timeout": 60  # FAIL-SAFE: Don't hang forever (Network/API issues)
        }
        
        if api_version:
            kwargs["api_version"] = api_version
            
        self.llm = ChatGoogleGenerativeAI(**kwargs)

    def _clean_text(self, text, max_chars=30000):
        """Minimize whitespace and truncate to prevent token overflow."""
        if not text: return ""
        cleaned = self.clean_regex.sub(' ', text).strip()
        return cleaned[:max_chars] if len(cleaned) > max_chars else cleaned

    def _call_with_retry(self, chain, inputs, max_retries=5, initial_delay=10):
        """
        Helper method to call the AI with exponential backoff for quota limits.
        Includes console logging for project visibility.
        """
        delay = initial_delay
        for i in range(max_retries + 1):
            try:
                if i > 0: print(f"DEBUG: AI Retry attempt {i}...")
                res = chain.invoke(inputs)
                
                # NUCLEAR STRING ENFORCEMENT: Handle Gemini multimodal list responses
                if isinstance(res, list):
                    res = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in res])
                elif hasattr(res, 'content'):
                    # Handle BaseMessage objects
                    res = res.content
                    if isinstance(res, list):
                        res = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in res])
                
                return str(res)
            except Exception as e:
                error_str = str(e).upper()
                print(f"DEBUG: AI Error encountered: {error_str[:150]}...")
                
                if any(err in error_str for err in ["429", "RESOURCE_EXHAUSTED", "QUOTA", "10054", "CONNECTION RESET", "TIMEOUT", "REMOTE HOST"]):
                    if i < max_retries:
                        # Auto-Fallback Strategy: If any 2.0 variant is failing, swap to 1.5-flash for the next retry
                        if any(x in self.model.upper() for x in ["2.0-FLASH", "2.0-PRO", "2.0-LITE"]) and i >= 1:
                            print(f"DEBUG: Primary model {self.model} overloaded or out of quota. Falling back to gemini-1.5-flash for maximum stability...")
                            self.model = "gemini-1.5-flash"
                            kwargs = {
                                "model": self.model,
                                "google_api_key": self.api_key,
                                "temperature": self.temperature,
                                "request_timeout": 60
                            }
                            if self.api_version:
                                kwargs["api_version"] = self.api_version
                                
                            self.llm = ChatGoogleGenerativeAI(**kwargs)
                            # Update the chain reference
                            chain.llm = self.llm 

                        # Retry logic
                        retry_match = re.search(r"RETRY IN ([\d\.]+)S", error_str)
                        if not retry_match:
                            retry_match = re.search(r"RETRYDELAY: '(\d+)S", error_str)
                            
                        if retry_match:
                            wait_time = float(retry_match.group(1)) + random.uniform(2, 5)
                        else:
                            wait_time = (delay * (2 ** i)) + random.uniform(5, 15) 
                        
                        print(f"DEBUG: Quota/Network issue. Waiting {wait_time:.1f}s before retry {i+1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                raise e

    def analyze_observations(self, txt_insp, txt_therm):
        """Pre-analysis step: merge and correlate observations."""
        print("DEBUG: Starting Phase 3 (Observation Merging)...")
        prompt = f"""
        Analyze and merge structural and thermal observations from these reports.
        Structure: {self._clean_text(txt_insp, max_chars=10000)}
        Thermal: {self._clean_text(txt_therm, max_chars=10000)}
        
        Provide a detailed engineering summary of current findings.
        """
        try:
            res = self._call_with_retry(self.llm, [{"role": "user", "content": prompt}])
            return res.content if hasattr(res, 'content') else str(res)
        except Exception as e:
            return f"SYNTHESIS_ERROR: {e}"

    def generate_final_ddr(self, txt_insp, txt_therm, bonus_ans):
        """Final generation step: using the pre-analysis summary."""
        print("DEBUG: Generating Final 7-Section DDR Report...")
        
        strict_instruction = ""
        if self.strict_mode:
            strict_instruction = "STRICT MODE ENABLED: Do NOT guess any detail. If it is not explicitly in the text, mark as Not Available. Forbid any hallucinations."

        prompt = f"""
        Generate a professional 'Detailed Diagnostic Report' (DDR) using the data below.
        
        [INPUTS]
        Structural Data: {self._clean_text(txt_insp, max_chars=12000)}
        Thermal Data: {self._clean_text(txt_therm, max_chars=12000)}
        Pre-Analysis: {bonus_ans}

        [FORMATTING RULES]
        Use these exact markers for UI rendering:
        - [[METADATA_START]]- Date:- Time:- Inspected By:- Property Type:[[METADATA_END]]
        - # 1. PROPERTY ISSUE SUMMARY
        - # 2. AREA-WISE OBSERVATIONS (Use [[AREA_START]]/[[AREA_END]] tags)
        - # 3. PROBABLE ROOT CAUSE
        - # 4. SEVERITY ASSESSMENT (High/Medium/Low keywords)
        - # 5. RECOMMENDED ACTIONS
        - # 6. ADDITIONAL NOTES
        - # 7. MISSING OR UNCLEAR INFORMATION

        Inside 'AREA-WISE OBSERVATIONS', use:
        [[AREA_START]] 
        [[NAME]]: Area Name
        [[FINDING]]: Observation
        [[DETAILS]]: Context
        [[IMAGE_REF]]: Page X
        [[AREA_END]]

        Be precise, high-contrast, and engineering-focused.
        """
        
        try:
            res = self._call_with_retry(self.llm, [{"role": "user", "content": prompt}])
            return res.content if hasattr(res, 'content') else str(res)
        except Exception as e:
            return f"PROTOCOL_ERROR: Failed to generate report. Details: {e}"
