# Reflection Log – Assignment 2

## What I learned

In this assignment, I implemented a two-agent travel planner, teaching me how important it is to give AI agents clear, separate jobs. I made the Planner focus on creating detailed itineraries while the Reviewer checked facts and practicality. This kept them from getting confused about their roles.

The step-by-step approach worked really well—first the Planner made a draft using its knowledge, then the Reviewer used live searches to fix any unrealistic parts. It felt like having one person plan the trip and another double-check everything, which made the final results much more reliable.

## Challenges

1. **Budget and Time Validation**
The Reviewer Agent needs to balance with practical constraints. I emphasized "revision" in the Delta List rather than just identifying problems, ensuring the Reviewer agent provides concrete alternatives to improve feasibility.

2. **Structured Output Formatting**
Getting consistent, parseable outputs from both agents required careful prompt engineering. I implemented standardized Delta List for the Reviewer Agent. The key was providing explicit output templates with clear section headers and required elements.

## Creative Ideas

1. **Table-based Planner Formatting**  
I used markdown tables (e.g., `| Time | Activity | Location | Cost | Notes |`) in the Planner output to ensure readability and structure. This also made it easier for the Reviewer to reference and validate specific parts of the itinerary.

2. **Persona-Based Role Assignment**  
I designed the Planner Agent as a “professional travel planner” focused on curating engaging travel experiences, while the Reviewer Agent acted as a “strict reviewer” concerned with logistical realism. This personality contrast ensured that the two agents maintained distinct perspectives and did not overlap in function.


## External Tools Used

I used **ChatGPT** to help refine the prompt instructions and troubleshoot output formatting issues. The AI assistance was particularly for:
- Testing different phrasing approaches for the Delta List concept
- Identifying potential ambiguities in the role definitions

The core agent logic, workflow design, and implementation decisions were developed independently based on the assignment requirements and provided code structure.

