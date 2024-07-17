from dataclasses import dataclass, field
from typing import List

from db_copilot.contract.memory_core import MemoryItem, MessageRole, Message
from db_copilot.contract.llm_core import LLM

BotReplyTag = 'BotReply'
UserQueryTag = 'UserQuery'

@dataclass
class FollowUpExample:
    message_history: List[Message] = field(default_factory=list) 
    current_query: str = None
    followup_query: str = None

    def add_message(self, speaker: MessageRole, message: str) -> None:
        self.message_history.append(Message(speaker, message))

    def get_input_prompt(self) -> str:
        example_str = []        
        for turn in self.message_history:
            tag = BotReplyTag if turn.role == MessageRole.ASSISTANT else UserQueryTag
            example_str.append(f'<{tag}>{turn.content}</{tag}>')
        example_str.append(f'<CurrentQuery>{self.current_query}</CurrentQuery>')
        return '\n'.join(example_str)

    def get_full_prompt(self) -> str:
        # corresBotMsg = '' if self.correspondingBotMsg<0 else f'{BotReplyTag}.{self.correspondingBotMsg}'
        # corresUserMsg = '' if self.correspondingUserMsg<0 else f'{UserQueryTag}.{self.correspondingUserMsg}'
        example_str = [
            self.get_input_prompt(),
            f'<MeaningOfLastQuery>{self.followup_query}</MeaningOfLastQuery>',
            # f'<CorrespondingUserMsg>{corresUserMsg}</CorrespondingUserMsg>',
            # f'<CorrespondingBotMsg>{corresBotMsg}</CorrespondingBotMsg>'
        ]
        return '\n'.join(example_str)

    def get_messages_by_role(self, role: MessageRole) -> List[str]:
        return [turn.content for turn in self.message_history if turn.role == role]
    
    def get_message_by_role_and_id(self, role: MessageRole, idx: int) -> str:
        assert idx>=0
        return self.get_messages_by_role(role)[idx]    
    
    def get_message_by_role_and_tag(self, role: MessageRole, tag: str) -> str:
        if not tag:
            return None
        idx = int(tag.split('.')[1])
        return self.get_messages_by_role(role)[idx]
    


def build_followup_example()-> List[FollowUpExample]:
    example1 = FollowUpExample(
        current_query='in windows', followup_query='How to set password in windows')
    example1.add_message(MessageRole.USER, 'Hello')
    example1.add_message(MessageRole.ASSISTANT,
                        'Hello! How can I assist you today?')
    example1.add_message(MessageRole.USER,
                        'How to login this system')
    example1.add_message(MessageRole.ASSISTANT,
                        'Power on your machine, enter your username and password in the appropriate fields, then click the login button')
    example1.add_message(MessageRole.USER,
                        'How to set password')
    example1.add_message(MessageRole.ASSISTANT,
                        'Open the terminal, type the command `passwd` and press Enter, you will be prompted to enter your current password, then to enter your new password twice (to confirm it).')
    # example1.correspondingUserMsg = 2
    # assert example1.getCorrespondingMsgByRole(
    #     DialogueSessionRole.USER) == 'How to set password'

    example2 = FollowUpExample(
        current_query='pie chart', followup_query='pie chart of top 3 students by english score')
    example2.add_message(MessageRole.USER, 'Who are you?')
    example2.add_message(MessageRole.ASSISTANT,
                        'I\'m an AI bot, how can I help you?')
    example2.add_message(MessageRole.USER,
                        'top 3 students by english score')
    example2.add_message(MessageRole.ASSISTANT, """SELECT TOP(3)
    CONCAT([students].[first_name], ' ', [students].[last_name]) AS name,
    [students].[english] AS english_score
FROM
    [students]
ORDER BY 
    english_score
DESC""")
    # example2.correspondingUserMsg = 1
    # example2.correspondingBotMsg = 1
    # assert example2.getCorrespondingMsgByRole(
    #     DialogueSessionRole.USER) == 'top 3 students by english score'
    # assert example2.getCorrespondingMsgByRole(
    #     DialogueSessionRole.ASSISTANT).startswith("SELECT TOP(3)")

    example3 = FollowUpExample(
        current_query='What about Genna?', followup_query='does Genna live in west coast?')
    example3.add_message(MessageRole.USER,
                        'does David live in west coast?')
    example3.add_message(MessageRole.ASSISTANT, 'No')
    # example3.correspondingUserMsg = 0
    # assert example3.getCorrespondingMsgByRole(
    #     DialogueSessionRole.USER) == 'does David live in west coast?'

    example4 = FollowUpExample(
        current_query='BMW sales', followup_query='BMW sales')
    example4.add_message(MessageRole.USER, 'UK')
    example4.add_message(MessageRole.ASSISTANT, """SELECT * FROM
    [Companies]
WHERE
    Country = "United Kingdom";""")

    example5 = FollowUpExample(
        current_query='chinese score trend', followup_query='chinese score trend')
    example5.add_message(MessageRole.USER, 'Who are you?')
    example5.add_message(MessageRole.ASSISTANT,
                        'I\'m an AI bot, how can I help you?')
    example5.add_message(MessageRole.USER,
                        'top 3 students by english score')
    example5.add_message(MessageRole.ASSISTANT, """SELECT TOP(3)
    CONCAT([students].[first_name], ' ', [students].[last_name]) AS name,
    [students].[english] AS english_score
FROM
    [students]
ORDER BY 
    english_score
DESC""")

    example6 = FollowUpExample(
        current_query='students older than 18', followup_query='students older than 18')
    example6.add_message(MessageRole.USER, 'Who are you?')
    example6.add_message(MessageRole.ASSISTANT,
                        'I\'m an AI bot, how can I help you?')
    example6.add_message(MessageRole.USER,
                        'top 3 students by english score')
    example6.add_message(MessageRole.ASSISTANT, """SELECT TOP(3)
    CONCAT([students].[first_name], ' ', [students].[last_name]) AS name,
    [students].[english] AS english_score
FROM
    [students]
ORDER BY 
    english_score
DESC""")
    example6.add_message(MessageRole.USER, 'pie chart')
    example6.add_message(MessageRole.ASSISTANT,
                        'Here is the pie chart of top 3 students by english score...')

    example7 = FollowUpExample(
        current_query='who sold the most', followup_query='who sold the most')
    example7.add_message(MessageRole.USER,
                        'does David live in west coast')
    example7.add_message(MessageRole.ASSISTANT, 'No')
    example7.add_message(MessageRole.USER,
                        'top 3 customers by total sales')
    example7.add_message(MessageRole.ASSISTANT,
                        'Peter, Rob, and Steve are top 3 customers by total sales')
    
    example8 = FollowUpExample(
        current_query='show me more details about the two students', followup_query='show me more details about Tom and Jim')
    example8.add_message(MessageRole.USER, 'which student has the best overall grade')
    example8.add_message(MessageRole.ASSISTANT, 'Tom has the best overall grade')
    example8.add_message(MessageRole.USER, 'which student has the second best overall grade')
    example8.add_message(MessageRole.ASSISTANT, 'Jim has the second best overall grade')

    return [example1, example2, example3, example4, example5, example6, example7, example8]






class FollowUpQueryRewriteSkill:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        examples = build_followup_example()
        self.example_str = '\n\n'.join([ex.get_full_prompt() for ex in examples])+'\n\n'
        

    def generate(self, currentQuery: str, queryHistory: List[MemoryItem]) -> str:
        if not queryHistory or len(queryHistory) == 0:
            return currentQuery
        
        followupExample = FollowUpExample(current_query=currentQuery, message_history=[Message(item.role, item.content) for item in queryHistory[-6:]])
        
        prompt = f'''
Task:
One user may ask several queries in natural language one by one, in a dialogue session with the AI assistant.
The meaning of the last query may depend on the previous dialogues. We need to predict the full meaning of the last query. 

- If the full meaning depends on previous bot reply or use query, we also output the corresponding message tag.
- If the meaning of the last query is complete, do not change it. We prefer to not change the last query, unless it is a very clear follow-up question.


{self.example_str}
{followupExample.get_input_prompt()}
<MeaningOfLastQuery>
'''.strip()
        result = list(self.llm.chat(messages=None, prompt=prompt, stop=['</MeaningOfLastQuery>'], stream=False))[0]
        if len(result.strip()) == 0:
            return currentQuery
        return result
