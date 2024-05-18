from pydantic import BaseModel

class CreateScrapeSchema(BaseModel):
    name: str
    section: str
    category: str
    image: str
    price: str
    
    