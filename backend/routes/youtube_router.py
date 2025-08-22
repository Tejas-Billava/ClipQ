from fastapi import APIRouter,HTTPException
from backend.model.request_models import UrlBody,AskBody
from backend.services.transcript_service import get_transcript
from backend.services.gemni_service import gemini_client
from backend.services.chroma_service import get_collection, retrieve_chunks
from typing import List

router=APIRouter()

MODEL_ID = "gemini-2.0-flash-lite"

@router.post("/summarise")
async def summarise(body:UrlBody):
  transcript=get_transcript(body.url)

  print(transcript)

  prompt = (
      "Summarise the following transcript into concise, high-level bullet points. "
      "Focus on key facts and actionable insights.\n\n"
      f"{transcript}"
  )


  try:
    summary=gemini_client().models.generate_content(
      model=MODEL_ID,
      contents=prompt
    ).text
  except Exception as e:
    raise HTTPException(status_code=500,detail=f"Gemini error: {e}")
  
  return {"summary": summary}



@router.post("/ask")
async def ask(body:AskBody):
  collection=get_collection(body.url)

  try:
    top_k_chunks:List[str] = retrieve_chunks(body.question,collection,body.top_k)
  except Exception as e:
        raise HTTPException(status_code=500,detail=f"Chroma retrieval error: {e}")
  
  context_block = "\n\n".join(top_k_chunks)
  # prompt = (
  #   "Use the context below to answer the question. "
  #   "If the answer cannot be found, say so.\n\n"
  #   f"Context:\n{context_block}\n\n"
  #   f"Question: {body.question}\n\nAnswer:"
  # )
  
  prompt = f"""
  You are VideoQA-GPT, an assistant that answers questions about a YouTube
  video transcript.  ONLY use information that appears in the CONTEXT
  section.  If the answer is missing, reply exactly with:
  Not found in the provided transcript.

  Answer format
  1. 1-3 sentence answer, written in your own words.
  2. A new line starting with → Sources: followed by the chunk-number(s)
    you relied on, e.g. “→ Sources: 2, 4”.
  3. Optionally include **up to 10 consecutive words** quoted from each
    cited chunk (enclosed in “…”).  Do not quote from chunks you did not
    cite.

  CONTEXT
  ========
  {context_block}

  QUESTION
  ========
  {body.question}

  ANSWER
  ======
  """

  try:
    answer = gemini_client().models.generate_content(
       model=MODEL_ID,
       contents=prompt
    ).text
  except Exception as e:
    raise HTTPException(status_code=500,detail=f"Gemini error: {e}")

  return {"answer": answer, "context": top_k_chunks}