from manager import PromptManager


print(PromptManager(0).get_qa_prompt(question="黛玉是什么时候进贾府的", retrieved_docs=None))