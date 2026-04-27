import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 3000000,
});

function normalizeResponse(data, originalQuestion) {
  return {
    question: data?.question || originalQuestion,
    answer: {
      legalExplanation:
        data?.answer?.legalExplanation || "No legal explanation was provided.",
      userRights:
        data?.answer?.userRights || "User rights information is not available.",
      nextSteps:
        Array.isArray(data?.answer?.nextSteps) && data.answer.nextSteps.length > 0
          ? data.answer.nextSteps
          : ["Please consult the cited legal sources for more details."],
      formalVersion:
        data?.answer?.formalVersion || "A formal legal version was not provided.",
    },
    sources: Array.isArray(data?.sources) ? data.sources : [],
    confidence:
      typeof data?.confidence === "number" ? data.confidence : 0.5,
    warning:
      data?.warning ||
      (typeof data?.confidence === "number" && data.confidence < 0.5
        ? "তথ্য অনিশ্চিত। অনুগ্রহ করে একজন আইনজীবীর পরামর্শ নিন।"
        : ""),
  };
}

export const askLegalQuestion = async (question) => {
  try {
    const response = await API.post("/chat", {
      message: question,
    });

    return normalizeResponse(response.data, question);
  } catch (error) {
    if (error.response) {
      throw new Error(
        error.response.data?.detail ||
          `Server error: ${error.response.status}`
      );
    }

    if (error.request) {
      throw new Error(
        "Cannot reach backend server. Make sure FastAPI is running."
      );
    }

    throw new Error(error.message || "Unexpected error occurred.");
  }
};

export const ingestDocuments = async () => {
  const response = await API.post("/ingest");
  return response.data;
};

export const checkBackendHealth = async () => {
  const response = await API.get("/health");
  return response.data;
};