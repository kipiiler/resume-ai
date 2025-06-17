import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.resume_writer import ResumeWriter

PATH_TO_RESUME_GENERATION_RESULTS = "experiments/sample/resume_generation_results.json"

data = json.load(open(PATH_TO_RESUME_GENERATION_RESULTS))
exp_results = data["experience_results"]
proj_results = data["project_results"]

exp_list = []
for exp_result in exp_results:
    exp_list.append((exp_result["item_id"], exp_result["bullet_points"]))

proj_list = []
for proj_result in proj_results:
    proj_list.append((proj_result["item_id"], proj_result["bullet_points"]))

resume_writer = ResumeWriter(template_path="template/jake_resume.tex")
resume_writer.write_resume(1, "resume.tex", exp_list, proj_list)