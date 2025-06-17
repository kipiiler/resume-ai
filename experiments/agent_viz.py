import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import JobAnalysisAgent
from IPython.display import Image, display

job_analysis_agent = JobAnalysisAgent()

graph = job_analysis_agent.get_graph()
# Save the mermaid diagram to a PNG file
png_data = graph.draw_mermaid_png()
with open('job_analysis_graph.png', 'wb') as f:
    f.write(png_data)

# Also display it
display(Image(png_data))

# result = job_analysis_agent.run({
#     "job_posting_url": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Research-Scientist--Spatial-Intelligence---New-College-Grad-2025_JR1997979?jobFamilyGroup=0c40f6bd1d8f10ae43ffda1e8d447e94&locationHierarchy1=2fcb99c455831013ea52fb338f2932d8"
# })

# print(result)
