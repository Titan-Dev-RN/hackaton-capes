import fastapi
import modules as md
import json
import uvicorn

from modules.ai import sanitize_input
app = fastapi.FastAPI()

@app.get("/search/{title}&{prompt}")
async def search_by_title(title: str, prompt:str):
    print(title)
    prompt = sanitize_input(prompt)
    print(prompt)
    papers = md.search_by_title(title)
    df = md.get_json(papers)
    # return md.return_response(df, prompt)

if __name__ == '__main__':
	# papers = md.search_by_title('medicine')
	# with open('papers.txt', 'w') as file:
		# json.dump({'papers':papers}, file, indent=4, ensure_ascii=False)
	# with open('papers.txt', 'r') as file:
	# 	df = json.load(file)['papers']
	# 	df = md.get_dataframe(df)
	# print(md.return_response(df, "Quantos artigos são estrangeiros?"))
    uvicorn.run(app, port=8080, host="localhost")