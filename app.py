from dotenv import load_dotenv 
import streamlit as st 
import os 
import io
from PIL import Image 
import pdf2image 
import google.generativeai as genai 
import base64 

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) 

def Automated_Resume_Ranking_System(job_description , pdf_content):
  # Prompts should be clear  , Because the output of llms is random or LLMs are word smithers 
  # LLMs write sentence based on the probability of word , where that probability depends on its context words or it's precedence words .
  prompt_1 = f"""
  Extract the designation of the job from job description
  Extract the key words from job description
  Final output is the designation and keywords in json format
  job description:
  {job_description}
  """
  prompt_2 = f"""
  Extract the designation from this resume
  Extract the key words from this resume
  Final output is the designation and keywords in json format
  """
  model1 =  genai.GenerativeModel('gemini-pro')  # Model for text to text data
  response_job = model1.generate_content(prompt_1) # Extracting the Keywords from Job Description
  response_job = response_job.text.replace("\n","")

  model2 =  genai.GenerativeModel('gemini-pro-vision')  # Model for image data to text 
  response_resume = model2.generate_content([prompt_2,pdf_content]) # Extracting the Keywords from Resume
  response_resume = response_resume.text.replace("\n","")

  prompt_3 = f"""
  job:
  {response_job}
  resume:
  {response_resume}
  show output in json format:
  Designation Match : Give me the semantic percentage match of destination of job and resume in number.
  Semantic Keyword Match : Give the semantic percentage match of keywords in job and resume in number.
  Final Match : Give me the final sematic match between job and resume in number.
  """
  
  # Comparing the Semantic relation between the Extracted keywords of Job Description and Resume .
  response_final = model1.generate_content(prompt_3)   
  response_final = response_final.text.replace("\n","")

  return response_final

def input_pdf_setup(uploaded_file): 
    ## Convert the PDF to Image 
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        
        first_page = images[0] 
        
        # Convert to bytes 
        img_byte_arr = io.BytesIO() 
        first_page.save(img_byte_arr , format = "JPEG") 
        img_byte_arr = img_byte_arr.getvalue() 
        
        pdf_parts = [
            {
                "mime_type" : "image/jpeg"  , 
                "data" : base64.b64encode(img_byte_arr).decode() # encode to base64 .
                
            }
        ]
        
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded") 
    


# Streamlit App 
st.set_page_config(page_title="Automated Resume Ranking System")
st.header("Automated Resume Ranking System")
input_text = st.text_area("Job Description" , key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF) ...",type = ["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")
    
submit = st.button("Percentage Match") 

input_prompt = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of specific role in the given job description and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as Percentage , Missing keywords and Final thoughts in json format.
"""


if  submit:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = Automated_Resume_Ranking_System(input_text,pdf_content[0])
        st.subheader("The Response is") 
        st.write(response)
    else:
        st.write("Please upload the resume")
    






    
