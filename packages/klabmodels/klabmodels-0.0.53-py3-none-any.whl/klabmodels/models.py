from langroid.utils.configuration import settings as lsettings
lsettings.cache_type = "fakeredis"
import langroid as lr

from typing import Dict, List, Optional
from redis_om import JsonModel, EmbeddedJsonModel, Field
from langroid.language_models.base import LLMMessage

from pydantic import BaseModel, Extra, HttpUrl, EmailStr
import time


### Models for Kiwi

class Company(JsonModel, extra=Extra.allow):
    name: str = Field(index=True)
    vision: Optional[str]
    mission: Optional[str]
    description: Optional[str]

    def __str__(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk'})



### Models used by Pickey
class Question(EmbeddedJsonModel):
    qnum: str
    question: str
    category: Optional[str]
    skill: Optional[str]
    options: Optional[List[str]] # for multiple choice questions

    def __str__(self):
        return f"{self.question}\n"+'\n'.join(f"{i}: {o}" for i,o in enumerate(self.options)) if self.options else f"{self.question}"
    
    def __str_with_skills__(self):
        qstr = f"Q: {self.question}\nCAT: {self.category}\nSKILL: {self.skill}"
        return qstr+'\nOPTIONS:\n'+'\n'.join(f"{i}: {o}" for i,o in enumerate(self.options)) if self.options else qstr



class Questionnaire(EmbeddedJsonModel):
    questions: List[Question]
    def __str__(self):
        return  f"Questions: ({len(self.questions)})\n"+'\n\n'.join(str(q) for q in self.questions)
    def __str_with_skills__(self):
        return  f"Questions: ({len(self.questions)})\n"+'\n\n'.join(q.__str_with_skills__() for q in self.questions)



# Evaluation of a CV by the Evaluator agent
class CVEvaluation(JsonModel):
    candidate: str = Field(index=True)# candidate pk
    company: Optional[str] = ""# company ref
    jobdesc: Optional[str] = ""# job description reftr
    skills_evaluation : List[Dict[str, List[Dict[str, str]]]]
    company_fit_grade: str
    vacancy_fit_grade: str
    summary: str



# Interview contents
class Interview(JsonModel):
    date: float # unix epoch
    candidate: str = Field(index=True) # Link to candidate
    job_description: str = Field(index=True) # Link to Job description
    questions: Questionnaire # interview questions
    interview: List[LLMMessage] = []
    evaluation: List[Dict] = []

    def __str__(self):
         return self.questions.__str_with_skills__()+"\n\nINTERVIEW:\n".join([f"{msg.role}: {msg.content}" for msg in self.interview])



class Candidate(JsonModel, extra=Extra.allow):
    name: str = Field(index=True)
    resume: str
    resume_classified: Optional[Dict] # processed resume with a local model
    jobs_applied: List[str] = [] # list of job pks the candidate applied for 
    interviews: List[str] = [] # reference to interviews (pk)
    questions: Optional[Questionnaire] # questions generated for the candidate only (not a vacancy)

    def __str__(self):
        if self.resume_classified:
            return '\n'.join({f"{k.upper()} : {v}" for k,v in self.resume_classified.items() if v})
        else:
            return self.resume


class JobDescription(JsonModel, extra=Extra.allow):
    reference: str = Field(index=True)
    job_title: str
    company: str = Field(index=True) # Reference to the company
    job_description: Optional[str]
    active: bool = True # whether the job listing is still active
    questions: Optional[Questionnaire]# job-only questions
    opened: float = time.time()
    closed: Optional[float]

    def __str__(self):
         return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk'})



# Wrapper for langroid agents
class Agent(BaseModel):
    agent: lr.ChatAgent
    task: lr.Task = None
    msgs: int = 0
    class Config:
        arbitrary_types_allowed = True

### Models for Kopi

### Models for Lumina

### Other Models

# Define the ANSI escape sequences for various colors and reset
class Colors(BaseModel):
    RED: str = "\033[31m"
    BLUE: str = "\033[34m"
    GREEN: str = "\033[32m"
    ORANGE: str = "\033[33m"  # no standard ANSI color for orange; using yellow
    CYAN: str = "\033[36m"
    MAGENTA: str = "\033[35m"
    YELLOW: str = "\033[33m"
    BLACK: str = "\033[30m"
    RESET: str = "\033[0m"

