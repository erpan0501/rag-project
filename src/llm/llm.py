import asyncio
from typing import List, Dict, Any

from openai import OpenAI,AsyncClient


class LLM:
    def __init__(self,model:str,api_key:str,base_url:str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

        self.demo = model == 'local-demo' or not api_key
        self.client = None if self.demo else OpenAI(api_key=api_key,base_url=base_url)
        self.async_client = None if self.demo else AsyncClient(api_key=api_key,base_url=base_url)

    
    def generate(self,messages:List[Dict[str,str]],temperature:float=0.7,max_token=2000) -> Dict[str,Any]:
        '''
        生成内容
        Args:
            messages: 聊天消息
            temperature: 采样温度
            max_token: 最大生成长度
        return: 生成结果
        '''
        if self.demo:
            question = messages[-1].get('content', '').split('[问题]')[-1]
            question = question.replace('问:', '').replace('答：', '').strip().splitlines()[0]
            content = f'本地演示模式已完成检索。问题“{question}”将基于上传文档回答；当前未配置外部模型 API。'
            return {
                'content': content,
                'finish_reason': 'stop',
                'token_used': {'total': 0, 'prompt': 0, 'completion': 0},
                'model': 'local-demo'
            }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_token)
        
        choice = response.choices[0]

        return {
            'content':choice.message.content,       # 内容
            'finish_reason':choice.finish_reason,   # 结束原因
            'token_used':{
                'total':response.usage.total_tokens,  # 总计消耗
                'prompt':response.usage.prompt_tokens,  # 提示消耗
                'completion':response.usage.completion_tokens # 完成消耗
            },
            'model':response.model  # 模型名称
        }
    async def generate_stream(self,messages:List[Dict[str,str]],temperature:float=0.7,max_token=2000):
        '''
        流式生成结果
        '''
        if self.demo:
            content = self.generate(messages, temperature=temperature, max_token=max_token)['content']
            for chunk in content:
                await asyncio.sleep(0)
                yield chunk
            return

        stream = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_token,
            stream=True)
        
        async for chunk in stream:
            if (content := chunk.choices[0].delta.content):
                yield content
