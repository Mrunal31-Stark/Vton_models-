# Submission email draft

**To:** [hiring contact / recruiter email]
**Subject:** Virtual Try On Model Evaluation assignment submission [Your Name]

---

Hi [Name],

Please find my submission for the Virtual Try On Model Evaluation assignment.

**Summary of approach**

I researched the current virtual try on landscape across both commercial APIs and open source
models, then shortlisted and fully tested three models, all self hosted on a single NVIDIA
RTX 4090 so that every generation stays well inside the cost target:

* IDM-VTON, with and without a category aware optimization layer
* CatVTON
* Leffa

Each model was tested across all ten clothing categories in the brief, plus coat on a female
model, giving eleven test cases per model. The same person photo and garment photo were used
across models within each category. Results were scored 1 to 5 on fit, drape, texture fidelity,
freedom from artefacts, and face and body preservation.

**Recommended model: IDM-VTON, self hosted, with the category aware optimization layer.**

* Mean accuracy 4.18 out of 5. Best or tied on ten of the eleven categories, and the clear
  best on the eight hardest. CatVTON scored 3.53 and Leffa scored 3.33.
* Generation time about 8 to 11 seconds per image, well under the 15 second limit.
* Cost about Rs 0.16 to Rs 0.20 per image, far under the Rs 4 limit. Measured range across all
  three models was 5.6 to 11.2 seconds and Rs 0.10 to Rs 0.20.

**On the IDM-VTON note in the brief.** As required, I optimized IDM-VTON for saree and kurti
rather than using it out of the box. The optimization uses no fine tuning and no training. It
combines a category aware full body mask, garment specific prompts, tuned diffusion parameters,
a mask union that removes hanging fabric artefacts, and a light face and hair paste back. This
takes saree to 4.2 and kurti to 4.6, both catalogue grade. One honest limitation is documented:
on the men's coat, with a casual base photo the model cannot render a shirt and tie through the
open coat, since it only repaints the coat region. This is noted in the report with two fixes.

**Deliverables**

1. Model comparison report (attached, PDF) with accuracy, speed and cost per clothing category,
   the full scoring table, the best model per category, and the recommendation.
2. Screen recording of the try on flow working live across multiple clothing types, on Google
   Drive with access set to Anyone with the link: [DRIVE LINK]
3. Code, harness and README documenting the steps followed, the models evaluated, the
   configurations and parameters used, and the results and recommendation:
   https://github.com/Mrunal31-Stark/Vton_models-
4. Final recommended model, stated above, meeting all three hard requirements.

**Cost.** Total testing spend was about 3.16 US dollars. RunPod usage logs and the running
cost ledger are included in the submission for reimbursement processing if I am selected.

Happy to walk through any part of this or answer questions.

Best regards,
[Your Name]
[phone] | [email]
