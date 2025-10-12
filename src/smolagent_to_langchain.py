from smolagents import ToolCallingAgent, Tool
from smolagents.models import Model, ChatMessage, MessageRole
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline,
)
bnb_cfg = BitsAndBytesConfig(load_in_4bit=True)
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from smolagents.models import Model, ChatMessage, MessageRole

import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.cuda.set_per_process_memory_fraction(0.95, 0)

class LocalHFModel(Model):
    """SmolAgents uyumlu, pipeline kullanmadan doğrudan model.generate ile çalışan sürüm."""

    def __init__(self, model_id: str):
        super().__init__(model_id=model_id)
        torch.cuda.empty_cache()

        print(f"[INFO] Loading local model (no pipeline): {model_id}")

        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,  
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        torch.backends.cuda.matmul.allow_tf32 = True

        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            quantization_config=bnb_cfg,
            device_map="auto",
            low_cpu_mem_usage=True,
        )

        self.model.eval()
        print("[INFO] Model loaded in 4-bit float16 mode (no pipeline).")

    def generate(self, messages, **kwargs):
        """SmolAgents generate() - direkt model.generate() ile."""
        def extract_text(msg):
            if isinstance(msg, str):
                return msg
            if hasattr(msg, "content"):
                content = msg.content
            elif isinstance(msg, dict):
                content = msg.get("content", "")
            else:
                return str(msg)
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        parts.append(item["text"])
                return "\n".join(parts)
            return str(content)

        if isinstance(messages, list):
            prompt = "\n".join([extract_text(m) for m in messages])
        else:
            prompt = extract_text(messages)

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=128,           
                temperature=0.6,              
                top_p=0.9,                    
                do_sample=True,
                repetition_penalty=1.2,       
                no_repeat_ngram_size=3,       
                use_cache=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return ChatMessage(role=MessageRole.ASSISTANT, content=text)


    def __call__(self, prompt: str, **kwargs):
        return self.generate([ChatMessage(role=MessageRole.USER, content=prompt)], **kwargs)

    def run(self, prompt: str, **kwargs):
        return self.__call__(prompt, **kwargs)

def convert_langchain_tool(lc_tool):
    """
    Convert a LangChain-style tool to a SmolAgents-compatible BaseTool subclass.
    """

    class SmolTool(Tool):
        name = getattr(lc_tool, "name", lc_tool.__class__.__name__.lower())
        description = getattr(lc_tool, "description", "No description provided.")
        inputs = {
            "input": {
                "type": "string",
                "description": "Text input for the tool.",
            }
        }
        output_type = "string"

        def forward(self, input: str):
            """SmolAgents standardına uygun 'forward' metodu."""
            try:
                result = lc_tool.invoke(input)
                return str(result)
            except Exception as e:
                return f"[ToolError: {e}]"

    return SmolTool()

class Wrapper:
    """LangChain'e benzer arayüz sağlayan SmolAgents Wrapper."""

    def __init__(self, model_id, tools):
        self.model = LocalHFModel(model_id)

        smol_tools = []
        for t in tools:
            try:
                smol_tools.append(convert_langchain_tool(t))
            except Exception as e:
                print(f"[WARN] Could not wrap tool {t}: {e}")

        self.agent = ToolCallingAgent(tools=smol_tools, model=self.model)
        self.agent.model = self.model
    def invoke(self, input_text: str):
        """LangChain benzeri tek çağrı."""
        try:
            return self.model.generate([input_text]).content
        except Exception as e:
            return f"(❌ Agent error: {e})"


    def bind_tools(self, tools):
        """LangChain'in create_tool_calling_agent fonksiyonuna uyumluluk sağlar."""
        return self
