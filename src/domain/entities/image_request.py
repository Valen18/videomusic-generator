from dataclasses import dataclass


@dataclass
class ImageRequest:
    prompt: str
    aspect_ratio: str = "16:9"
    
    def __post_init__(self):
        if not self.prompt:
            raise ValueError("Prompt cannot be empty")
        
        valid_ratios = ["1:1", "4:3", "3:4", "16:9", "9:16"]
        if self.aspect_ratio not in valid_ratios:
            raise ValueError(f"Aspect ratio must be one of: {valid_ratios}")
    
    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "aspect_ratio": self.aspect_ratio
        }