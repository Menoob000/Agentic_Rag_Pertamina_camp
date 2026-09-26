import requests

# URL of the FastAPI endpoint
url = "http://localhost:8000/api/generate-rks"

# The text form data
data = {
    "jenis_pekerjaan": "Pembangunan Gardu Listrik",
    "detail_pekerjaan": "Pembangunan gardu listrik kapasitas 150kV beserta instalasi panel kontrol.",
    "lokasi": "Plumpang, Jakarta Utara"
}

# The file you want to upload
# IMPORTANT: Replace this with the actual path to your PDF BOQ file
file_path = "boq_sample.pdf" 

try:
    # Open the file in binary read mode
    with open(file_path, "rb") as f:
        # Prepare the files payload. 
        # The key "files" matches the parameter name in our FastAPI endpoint
        files_payload = [
            ("files", (file_path.split("/")[-1], f, "application/pdf"))
        ]
        
        print("Sending request to API... This may take a few minutes for the LLM to generate.")
        
        # We pass both `data` (for the Form strings) and `files` (for the PDF)
        response = requests.post(url, data=data, files=files_payload)
        
        if response.status_code == 200:
            # The API returns a downloadable file (FileResponse)
            # We save the content to a local .docx file
            output_filename = "Generated_RKS_Result.docx"
            with open(output_filename, "wb") as out_file:
                out_file.write(response.content)
            print(f"✅ Success! Document saved locally as {output_filename}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print("Error Details:", response.text)

except FileNotFoundError:
    print(f"Error: Could not find the file at {file_path}. Please provide a valid PDF file path.")
