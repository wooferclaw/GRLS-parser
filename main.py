import webpage
import pdf

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from pathlib import Path


class Request(BaseModel):
    url: str

    class Config:
        schema_extra = {
            "example": {
                "url": "http://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=f4d664a2-1579-4fe1-a208-c61795ed1ce9&t="
            }
        }


responses = {
    404: {"description": "API not available"},
    302: {"description": "API has moved"},
    403: {"description": "Not enough privileges to use API"},
}

app = FastAPI()


@app.get('/status', status_code=200)
async def status():
    return 'Up and running!'


@app.post("/instructions",
          responses={
              **responses,
              200: {
                  "description": "Response from GRLS wrapper",
                  "content": {
                      "application/json": {
                          "example": {
                              "instructions": [
                                  {"ЛС-000574": [
                                      {"Изм. №1 к ЛС-000574-250117":
                                          {
                                              "Restrictions": "Противопоказания",
                                              "Usage_and_dose": "Способ применения и дозы",
                                          }
                                      }
                                  ]}
                              ],
                          }
                      }
                  },
              },
          },
          )
async def instructions(request: Request):
    reg_num, reg_id = webpage.get_reg_data(request.url)
    instr_dict = webpage.get_pdfs(reg_num, reg_id)

    texts = {}
    for pdf_instr in instr_dict:
        pdf.ocr(instr_dict[pdf_instr])
        txt = instr_dict[pdf_instr].replace('.pdf', '.txt')
        texts[pdf_instr] = open(txt, 'r').read()

        # removing paths
        pdfpath = Path(instr_dict[pdf_instr])
        txtpath = Path(txt)
        pdfpath.unlink()
        txtpath.unlink()

    dict_result = {
        "instructions:": {
            reg_num:
                texts
        }
    }



    return jsonable_encoder(dict_result)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="GRLS wrapper",
        version="0.0.1",
        description="GRLS drug registry wrapper and instruction version comparer",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
