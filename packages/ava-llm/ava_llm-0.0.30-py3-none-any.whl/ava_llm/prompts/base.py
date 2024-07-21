class PromptTemplate:
    def format(self, **kwargs):
        return self.template.format(**kwargs)


class PromptWithSystemInstructionTemplate:
    """Prompt template with system instruction.
    
    Args:
        template (str): The template string for the normal (user) prompt.
        system_template (str): The template string for the system instruction.
    """
    def format(self, **kwargs):
        system_prompt = self.system_template.format(**kwargs)
        user_prompt = self.template.format(**kwargs)
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
