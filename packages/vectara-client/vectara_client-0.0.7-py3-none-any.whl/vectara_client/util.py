from abc import ABC
from typing import Type, TypeVar, List
import logging
import threading
import json





class BaseFormatter(ABC):

    def __init__(self):
        pass

    def heading(self, heading: str, level: int = 1):
        raise Exception("Implement in subclass")

    def sentence(self, sentence: str):
        raise Exception("Implement in subclass")

    def link(self, text: str, url: str):
        raise Exception("Implement in subclass")

    def paragraph(self, paragraph: str):
        raise Exception("Implement in subclass")

    def bold(self, text: str):
        raise Exception("Implement in subclass")

    def italic(self, text: str):
        raise Exception("Implement in subclass")

    def list(self, items: List[str], level: int = 1):
        raise Exception("Implement in subclass")

    def rtl(self, text: str):
        raise Exception("Implement in subclass")

    def code(self, text: str, language=None):
        raise Exception("Implement in subclass")

class MarkdownFormatter(BaseFormatter):

    def __init__(self):
        pass

    def heading(self, heading: str, level: int = 1):
        indent = "#" * level
        return f'\n{indent} {heading}'

    def sentence(self, sentence: str):
        return sentence

    def link(self, text, url):
        return f"[{text}]({url})"

    def paragraph(self, paragraph: str):
        return f"\n\n{paragraph}\n"

    def bold(self, text: str):
        return f"**{text}**"

    def italic(self, text: str):
        return f"*{text}*"

    def list(self, items: List[str], level: int = 1):
        if level < 1:
            raise TypeError("List level must be greater than 0")
        indent = " " * (level - 1)
        results = [f"{indent} {idx + 1}. {item}" for idx, item in enumerate(items)]
        return "\n" + "\n".join(results) + "\n"

    def rtl(self, text):
        return '<div dir="rtl">\n' + text + '</div>'

    def code(self, text: str, language=None):
        result = "\n```"
        if language:
            result += language
        result += str(text)
        result += "\n```\n"
        return result





prompt_text = (
    '[ {"role": "system", "content": "You are a human resources manager who takes the search results and summarizes them as a coherent response. Only use information provided in this chat. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."}, \n'  # ,\n'
    '#foreach ($qResult in $vectaraQueryResults) \n'
    '   #if ($foreach.first) \n'
    '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n'
    '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
    '   #else \n'
    '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n'
    '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
    '   #end \n'
    ' #end \n'
    '{"role": "user", "content": "Generate a detailed answer (that is no more than 300 words) for the query \\"$esc.java(${vectaraQuery})\\" solely based on the search results in this chat. You must only use information from the provided results. Cite search results using \\"[number]\\" notation. Only cite the most relevant results that answer the question accurately." } ]')


class BasePromptFactory(ABC):

    def __init__(self):
        pass

    def build(self):
        raise Exception("Implement in subclasses")


class SimplePromptFactory(BasePromptFactory):
    SYSTEM_PROMPT_TEMPLATE = 'You are a {persona} who takes the search results and {a_cite_text} {just_rag_text} Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\".'
    USER_PROMPT_TEMPLATE = 'Generate a detailed answer (that is no more than {max_word_count} words) for the query \\"$esc.java(${{vectaraQuery}})\\" {just_rag_text} {b_cite_text}'

    A_DO_CITE = "summarizes them as a coherent response,"
    A_DO_NOT_CITE = "only return the most relevant answer. Do not iterate over each question,"

    B_DO_CITE = 'Cite search results using \\\\\\"[number]\\\\\\" notation. Only cite the most relevant results that answer the question accurately.'
    B_DO_NOT_CITE = 'Do not cite search results.'

    RAG_ONLY = 'solely based on the search results in this chat. You must only use information from the provided results.'
    ALLOW_NON_RAG = 'preferably based on the search results in this chat. You may allow additional information you know in the results.'

    """
    Generates a valid prompt text

    """

    def __init__(self, persona: str, max_word_count: int = 300, cite: bool = True, just_rag=True):
        super().__init__()
        self.persona = persona
        self.max_word_count = max_word_count
        self.cite = cite
        self.just_rag = just_rag

    def build(self):
        lines = []

        if self.just_rag:
            just_rag_text = SimplePromptFactory.RAG_ONLY
        else:
            just_rag_text = SimplePromptFactory.ALLOW_NON_RAG

        if self.cite:
            a_cite_text = SimplePromptFactory.A_DO_CITE
            b_cite_text = SimplePromptFactory.B_DO_CITE
        else:
            a_cite_text = SimplePromptFactory.A_DO_NOT_CITE
            b_cite_text = SimplePromptFactory.B_DO_NOT_CITE

        system_prompt = SimplePromptFactory.SYSTEM_PROMPT_TEMPLATE.format(
            persona=self.persona, just_rag_text=just_rag_text, a_cite_text=a_cite_text
        )

        user_prompt = SimplePromptFactory.USER_PROMPT_TEMPLATE.format(
            max_word_count=self.max_word_count, just_rag_text=just_rag_text, b_cite_text=b_cite_text
        )

        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{system_prompt}"}}, \n')

        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        # TODO interpolate.
        lines.append(f'{{"role": "user", "content": "{user_prompt}" }} ]')

        return "".join(lines)


class StandardPromptFactory(BasePromptFactory):
    """
    Generates a valid prompt text

    """

    def __init__(self, system_prompt=None, user_prompt=None):
        super().__init__()
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def build(self):
        lines = []
        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{self.system_prompt}"}}, \n')

        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        # TODO interpolate.
        lines.append(f'{{"role": "user", "content": "{self.user_prompt}" }} ]')

        return "".join(lines)


class ChatPromptFactory(BasePromptFactory):
    SYSTEM_PROMPT_TEMPLATE = 'You are a {chat_persona} talking with a customer, respond to small talk in a nice way. You must not say you are an AI model. Provide a short answer from the search results, though you can go into more detail if requested from the user. Do not iterate over each question, just provide a short answer based on prior assistant answers in this chat. You may allow additional information you know in the results if nothing relevant is found. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\".'
    USER_PROMPT_TEMPLATE = 'Generate a chat response which is part of a back-and-forth, that is no more than {max_word_count} words, for the query \\"$esc.java(${{vectaraQuery}})\\" preferably based on the interactions in this chat. Please ask for more information to help clarify if needed. If the response answers the question, please finish with a closing phrase that uses \\"does that answer your question\\" to confirm resolution.'

    def __init__(self, chat_persona="Customer Support", name="Gary", max_word_count=300, prompt_metadata={}):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.chat_persona = chat_persona
        self.name = name
        self.messages = []
        self.max_word_count = max_word_count
        self.prompt_metadata = prompt_metadata

    def add_user_message(self, user_message):
        self.messages.append({"role": "user", "content": user_message})

    def add_assistant_message(self, assistant_message):
        self.messages.append({"role": "assistant", "content": assistant_message})

    def add_user_assistant_pair(self, user_message, assistant_message):
        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": assistant_message})

    def build(self):
        system_prompt = ChatPromptFactory.SYSTEM_PROMPT_TEMPLATE.format(
            chat_persona=self.chat_persona
        )

        user_prompt = ChatPromptFactory.USER_PROMPT_TEMPLATE.format(
            max_word_count=self.max_word_count
        )

        lines = []

        # Append the system indicator.
        lines.append(f'[ {{"role": "system", "content": "{system_prompt}"}}, \n')

        # Insert prior context user/assistant messages.
        for message in self.messages:
            lines.append(f'    {json.dumps(message)}, \n')
        # Append the pre-requisite 'for-loop' for RAG.
        lines.append('#foreach ($qResult in $vectaraQueryResults) \n')

        metadata = ""
        if (self.prompt_metadata):
            bits = []
            for key in self.prompt_metadata.keys():
                value = self.prompt_metadata[key]
                bits.append(f"{key}: ")

        # Insert the Retrieval results.
        lines.append('   #if ($foreach.first) \n')
        lines.append(
            '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #else \n')
        lines.append(
            '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n')
        lines.append('   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n')
        lines.append('   #end \n')
        lines.append(' #end \n')

        # Append the Final user phrasing.
        lines.append(f'{{"role": "user", "content": "{user_prompt}" }} ]')

        result = "".join(lines)
        self.logger.info("Chat prompt is:\n" + result)
        return result


class CountDownLatch:
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notify_all()
        self.lock.release()

    def sweat_it_out(self):
        """
        Because await is a keyword.

        :return:
        """
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()


