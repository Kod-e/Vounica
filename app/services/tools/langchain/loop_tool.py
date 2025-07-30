from langchain_core.tools import StructuredTool


class LoopTool:
    def __init__(self, max_loop_num: int = 5):
        self.is_stop = False
        self.is_loop = True
        self.loop_num = 0
        self.max_loop_num = max_loop_num
        self.tool_call = [
            StructuredTool.from_function(
                name="stop_loop",
                func=self.stop,
                description="Stop the loop",
            )
        ]
        
    def stop(self) -> None:
        self.is_stop = True
        self.is_loop = False
        
    def loop(self) -> None:
        self.loop_num += 1
        if self.loop_num >= self.max_loop_num:
            self.stop()
        
    def get_loop_prompt(self) -> str:
        return f"Loop {self.loop_num} of {self.max_loop_num}"