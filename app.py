import json
from fastapi import FastAPI, APIRouter, UploadFile, File
from typing import List

from utils import (
    add_text_to_collection, 
    get_answer, 
    verify_pdf_path, 
    delete_collection
  )

from utils import save_uploaded_file, post_message_to_slack
app= FastAPI(debug=True)

import os


@app.post('/get-anwers')
async def get_answers_for_pdf( questions: List[str]= ['Who is the CEO of the company?'], n_results:int= 1,pdf_file: UploadFile=File(...)):
    
    questions= questions[0].split(',') # make a list of questions

    if pdf_file is not None:
        saved_pdf_file = await save_uploaded_file(file=pdf_file.file, filename=pdf_file.filename) 
        # verify_pdf_path(saved_pdf_file)
        confirmation = add_text_to_collection(file = saved_pdf_file
                                              )
        print(confirmation)

        outputlist = list()
        for i in questions:
            print(i)
            answer = get_answer(i, n = n_results)
            outputlist.append({"question": i, "answer": answer})
        json_data = json.dumps(outputlist)
        response = post_message_to_slack(json_data)
        print(response)
        return json_data

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)