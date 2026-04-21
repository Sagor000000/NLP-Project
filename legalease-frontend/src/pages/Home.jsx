import { useState } from "react";
import Header from "../components/Header";
import QueryForm from "../components/QueryForm";
import AnswerCard from "../components/AnswerCard";
import { askLegalQuestion } from "../services/api";

function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      setError("Please enter a legal question.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const data = await askLegalQuestion(question);
      setResult(data);
    } catch (err) {
      setError("Something went wrong while fetching the answer.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <Header />

      <QueryForm
        question={question}
        setQuestion={setQuestion}
        onSubmit={handleSubmit}
        loading={loading}
      />

      {error && <p className="error-text">{error}</p>}

      <AnswerCard result={result} loading={loading} />
    </div>
  );
}

export default Home;