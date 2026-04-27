import os
import glob
import json
import re
import time  # ⏳ [আপডেট] API রেট লিমিট হ্যান্ডেল করার জন্য time ইমপোর্ট করা হলো
from typing import Any, Dict, List

import json_repair
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore

PDF_DIR = "./legal_pdfs"
TRANSLATION_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "google").lower()

LEGAL_PROMPT = PromptTemplate.from_template("""
You are LegalEase BD, an AI legal assistant for Bangladeshi law.

You are working with these legal documents: {sources_context}

STRICT RULES — follow every rule without exception:

1. Answer ONLY using information explicitly stated in the LEGAL CONTEXT below.
2. Do NOT invent, assume, or add any law names, section numbers, or years not found in the context.
3. Only cite the exact law names and section numbers that appear word-for-word in the context.
4. If the context does not contain enough information, set confidence to 0.3 and explain what was not found.
5. Never hallucinate — if you are not sure, say so honestly.
6. Always respond in ENGLISH. The answer will be translated to the user's language afterward.
7. Keep answers concise, factual, and directly based on the context.
8. For sources, use the exact law name as it appears in the context.
9. If the answer is NOT explicitly found in the context, return EXACTLY:
{{
  "legalExplanation": "Not found in provided law",
  "userRights": "",
  "nextSteps": [],
  "formalVersion": "",
  "sources": [],
  "confidence": 0.3
}}
10. Do NOT mention, suggest, or refer to any law, act, or regulation that is NOT present in the provided context.
11. If the question involves comparison, multiple subjects, or multiple legal scenarios:
- You MUST check whether multiple laws are present in the context
- If multiple relevant laws are found, include ALL of them in the answer
- If only one law is found, clearly state that the other part is NOT found in the provided law.
12. Do NOT combine or mix unrelated laws. Only combine information when clearly relevant to the question.
13. If the answer is incomplete or partially missing from the context:
- Clearly state what is missing
- Set confidence below 0.6

Respond ONLY in this exact JSON format. No markdown, no extra text outside the JSON:

{{
  "legalExplanation": "factual explanation based strictly on the context",
  "userRights": "specific rights found in the context",
  "nextSteps": ["concrete step 1", "concrete step 2", "concrete step 3"],
  "formalVersion": "formal legal restatement of the answer",
  "sources": [
    {{"source": "exact law name from context", "section": "exact section from context"}}
  ],
  "confidence": 0.85
}}

LEGAL CONTEXT:
{context}

USER QUESTION:
{question}

JSON RESPONSE:
""")

class LegalRAG:
    def __init__(self):
        print("⚙️ Loading Cloud LegalRAG...")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "legalease-bd")

        self.vectorstore = None
        self.retriever = None
        self._translator = self._init_translator()
        self._load_vectorstore()

    # ─── Translation Setup ─────────────────────────────────────────────────────

    def _init_translator(self) -> bool:
        try:
            if TRANSLATION_PROVIDER == "google":
                from deep_translator import GoogleTranslator  # noqa: F401
                print("✅ Google Translator ready")
            elif TRANSLATION_PROVIDER == "deepl":
                from deep_translator import DeeplTranslator  # noqa: F401
                print("✅ DeepL Translator ready")
            elif TRANSLATION_PROVIDER == "mymemory":
                from deep_translator import MyMemoryTranslator  # noqa: F401
                print("✅ MyMemory Translator ready")
            else:
                raise ValueError(f"Unknown provider: {TRANSLATION_PROVIDER}")
            return True
        except ImportError:
            print("⚠️ deep-translator not installed! Run: pip install deep-translator")
            return False

    def _do_translate(self, text: str, source: str, target: str) -> str:
        if not self._translator or not text or not text.strip():
            return text
        try:
            if TRANSLATION_PROVIDER == "google":
                from deep_translator import GoogleTranslator
                return GoogleTranslator(source=source, target=target).translate(text)

            if TRANSLATION_PROVIDER == "deepl":
                from deep_translator import DeeplTranslator
                return DeeplTranslator(
                    source=source,
                    target=target,
                    use_free_api=True
                ).translate(text)

            if TRANSLATION_PROVIDER == "mymemory":
                from deep_translator import MyMemoryTranslator
                return MyMemoryTranslator(source=source, target=target).translate(text)

        except Exception as e:
            print(f"⚠️ [{TRANSLATION_PROVIDER}] translation failed: {e}")

        return text

    # ─── Vector Store (Pinecone) ───────────────────────────────────────────────

    def _load_vectorstore(self) -> None:
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
        )
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )
        print("✅ Pinecone DB loaded")

    # ─── Text Cleaner ──────────────────────────────────────────────────────────

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"-\n(?=[a-z])", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    # ─── Language Detection ────────────────────────────────────────────────────

    def _detect_language(self, text: str) -> str:
        bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
        return "bn" if bengali_chars > 3 else "en"

    def _detect_chunk_language(self, text: str) -> str:
        bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
        ratio = bengali_chars / max(len(text), 1)
        return "bn" if ratio > 0.3 else "en"

    # ─── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_documents(self) -> int:
        pdf_files = glob.glob(f"{PDF_DIR}/*.pdf")
        if not pdf_files:
            raise FileNotFoundError(f"No PDFs found in {PDF_DIR}/")

        print(f"📄 Found {len(pdf_files)} PDF(s)")
        all_docs = []

        for pdf_path in pdf_files:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            filename = os.path.basename(pdf_path)
            law_name = os.path.splitext(filename)[0]
            law_name = law_name.replace("_", " ").replace("-", " ").title()

            for doc in docs:
                doc.page_content = self._clean_text(doc.page_content)
                doc.metadata["source_file"] = filename
                doc.metadata["law_name"] = law_name
                doc.metadata["language"] = self._detect_chunk_language(doc.page_content)

            all_docs.extend(docs)
            print(f"   📖 Loaded: {filename} → '{law_name}' ({len(docs)} pages)")

        all_docs = [d for d in all_docs if len(d.page_content.strip()) > 50]
        print(f"📝 Pages after cleaning: {len(all_docs)}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\nSection", "\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(all_docs)
        print(f"✂️ Chunks created: {len(chunks)}")

        print("☁️ Uploading to Pinecone in batches to avoid API limits...")

        # ─── [আপডেট] Batch Processing Logic শুরু ───
        batch_size = 80  # গুগলের লিমিট ১০০, তাই আমরা ৮০টি করে পাঠাবো
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            print(f"   ⬆️ Uploading batch {batch_num}/{total_batches} (Chunks {i} to {i + len(batch_chunks)})...")
            
            try:
                # Pinecone-এ ডেটা অ্যাড করা
                self.vectorstore.add_documents(batch_chunks)
                    
                # যদি আরো চাঙ্ক বাকি থাকে, তবে ৬০ সেকেন্ড অপেক্ষা করবো
                if i + batch_size < len(chunks):
                    print("   ⏳ Sleeping for 62 seconds to reset Google API limit...")
                    time.sleep(62) # সেইফটির জন্য ২ সেকেন্ড বেশি দেওয়া হলো
                    
            except Exception as e:
                print(f"❌ Error in batch {batch_num}: {e}")
                raise e
        # ─── Batch Processing Logic শেষ ───

        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )
        print(f"✅ Stored {len(chunks)} chunks in Pinecone Cloud")
        return len(chunks)

    # ─── Smart Retrieval ───────────────────────────────────────────────────────

    def _translate_query_to_english(self, question: str) -> str:
        translated = self._do_translate(question, source="bn", target="en")
        print(f"🌐 Query translated [{TRANSLATION_PROVIDER}]: {translated}")
        return translated or question

    def _smart_retrieve(self, user_question: str, lang: str) -> List[Any]:
        seen = set()
        all_docs = []

        def add_docs(docs: List[Any]) -> None:
            for doc in docs:
                content = getattr(doc, "page_content", "")
                if content and content not in seen:
                    seen.add(content)
                    all_docs.append(doc)

        if lang == "bn":
            print("🔍 Searching Bengali PDFs with original query...")
            add_docs(self.retriever.invoke(user_question))

            english_query = self._translate_query_to_english(user_question)
            print(f"🔍 Searching English PDFs with translated query: {english_query}")
            add_docs(self.retriever.invoke(english_query))
        else:
            print(f"🔍 Searching with English query: {user_question}")
            add_docs(self.retriever.invoke(user_question))

        print(f"📦 Total unique chunks retrieved: {len(all_docs)}")
        return all_docs

    def _extract_sources_context(self, docs: List[Any]) -> str:
        law_names = set()
        for doc in docs:
            law_name = doc.metadata.get("law_name", "")
            if law_name:
                law_names.add(law_name)

        result = ", ".join(sorted(law_names)) if law_names else "Bangladeshi Law"
        print(f"📚 Laws in context: {result}")
        return result

    # ─── Answer Translation ────────────────────────────────────────────────────

    def _translate_answer_to_bengali(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        print(f"🔄 Translating answer → Bengali [{TRANSLATION_PROVIDER}]...")

        parsed["legalExplanation"] = self._do_translate(
            parsed.get("legalExplanation", ""), source="en", target="bn"
        )
        parsed["userRights"] = self._do_translate(
            parsed.get("userRights", ""), source="en", target="bn"
        )
        parsed["formalVersion"] = self._do_translate(
            parsed.get("formalVersion", ""), source="en", target="bn"
        )
        parsed["nextSteps"] = [
            self._do_translate(step, source="en", target="bn")
            for step in parsed.get("nextSteps", [])
        ]

        print("✅ Answer translated to Bengali")
        return parsed

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def _get_warning(self, confidence: float, lang: str) -> str:
        if confidence < 0.7:
            return (
                "প্রয়োজনে একজন আইনজীবীর পরামর্শ নিন।"
                if lang == "bn"
                else "Please consult a licensed lawyer for this matter."
            )

        return (
            "এই তথ্য শুধুমাত্র সাধারণ গাইডেন্সের জন্য।"
            if lang == "bn"
            else "This information is for general guidance only."
        )

    def _default_parsed_response(self) -> Dict[str, Any]:
        return {
            "legalExplanation": "Sorry, no relevant legal information found.",
            "userRights": "",
            "nextSteps": ["Please consult a licensed lawyer."],
            "formalVersion": "",
            "sources": [],
            "confidence": 0.0,
        }

    def _parse_llm_response(self, raw: str) -> Dict[str, Any]:
        cleaned = raw.strip()

        # remove ```json ... ``` fences if the model returns them
        cleaned = re.sub(
            r"^```json\s*|\s*```$",
            "",
            cleaned,
            flags=re.MULTILINE
        ).strip()

        try:
            parsed = json.loads(cleaned)
        except Exception:
            try:
                parsed = json_repair.loads(cleaned)
            except Exception:
                parsed = self._default_parsed_response()

        if not isinstance(parsed, dict):
            parsed = self._default_parsed_response()

        next_steps = parsed.get("nextSteps", [])
        if not isinstance(next_steps, list):
            next_steps = []
        next_steps = [str(step).strip() for step in next_steps if str(step).strip()]

        raw_sources = parsed.get("sources", [])
        clean_sources = []
        if isinstance(raw_sources, list):
            for item in raw_sources:
                if isinstance(item, dict):
                    source = str(item.get("source", "")).strip()
                    section = str(item.get("section", "")).strip()
                    if source or section:
                        clean_sources.append(
                            {
                                "source": source or "Unknown Law",
                                "section": section or "N/A",
                            }
                        )

        try:
            confidence = float(parsed.get("confidence", 0.0))
        except Exception:
            confidence = 0.0

        confidence = max(0.0, min(1.0, confidence))

        return {
            "legalExplanation": str(
                parsed.get("legalExplanation", "Sorry, no relevant legal information found.")
            ),
            "userRights": str(parsed.get("userRights", "")),
            "nextSteps": next_steps,
            "formalVersion": str(parsed.get("formalVersion", "")),
            "sources": clean_sources,
            "confidence": confidence,
        }

    def query(self, question: str) -> Dict[str, Any]:
        lang = self._detect_language(question)
        docs = self._smart_retrieve(question, lang)

        if not docs:
            answer = {
                "legalExplanation": "Sorry, no relevant legal information found.",
                "userRights": "",
                "nextSteps": ["Please consult a licensed lawyer."],
                "formalVersion": "",
            }

            if lang == "bn":
                answer = self._translate_answer_to_bengali(answer)

            return {
                "question": question,
                "answer": answer,
                "sources": [],
                "confidence": 0.0,
                "warning": self._get_warning(0.0, lang),
            }

        context_parts = []
        for doc in docs:
            law_name = doc.metadata.get("law_name", "Unknown Law")
            page_no = doc.metadata.get("page", "")
            context_parts.append(
                f"[LAW: {law_name} | PAGE: {page_no}]\n{doc.page_content}"
            )

        context = "\n\n".join(context_parts)
        sources_context = self._extract_sources_context(docs)

        question_for_llm = question
        if lang == "bn":
            question_for_llm = self._translate_query_to_english(question)

        chain = LEGAL_PROMPT | self.llm | StrOutputParser()
        raw = chain.invoke(
            {
                "sources_context": sources_context,
                "context": context,
                "question": question_for_llm,
            }
        )

        parsed = self._parse_llm_response(raw)

        answer = {
            "legalExplanation": parsed["legalExplanation"],
            "userRights": parsed["userRights"],
            "nextSteps": parsed["nextSteps"],
            "formalVersion": parsed["formalVersion"],
        }

        if lang == "bn":
            answer = self._translate_answer_to_bengali(answer)

        return {
            "question": question,
            "answer": answer,
            "sources": parsed["sources"],
            "confidence": parsed["confidence"],
            "warning": self._get_warning(parsed["confidence"], lang),
        }