import CitationList from "./CitationList";
import ConfidenceBadge from "./ConfidenceBadge";
import WarningBox from "./WarningBox";
import LoadingCard from "./LoadingCard";

function AnswerCard({ result, loading }) {
  if (loading) {
    return <LoadingCard />;
  }

  if (!result) {
    return (
      <div className="answer-card">
        <h2>Answer</h2>
        <p>Your legal answer will appear here.</p>
      </div>
    );
  }

  return (
    <div className="answer-card">
      <h2>Legal Response</h2>

      <div className="section-block">
        <h3>Legal Explanation</h3>
        <p>{result.answer.legalExplanation}</p>
      </div>

      <div className="section-block">
        <h3>User Rights</h3>
        <p>{result.answer.userRights}</p>
      </div>

      <div className="section-block">
        <h3>Next Steps</h3>
        <ol className="steps-list">
          {result.answer.nextSteps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ol>
      </div>

      <div className="section-block">
        <h3>Formal Legal Version</h3>
        <p className="formal-text">{result.answer.formalVersion}</p>
      </div>

      <CitationList sources={result.sources} />
      <ConfidenceBadge confidence={result.confidence} />
      <WarningBox warning={result.warning} />
    </div>
  );
}

export default AnswerCard;