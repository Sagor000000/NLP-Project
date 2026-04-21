function ConfidenceBadge({ confidence }) {
  if (confidence === undefined || confidence === null) {
    return null;
  }

  const percentage = Math.round(confidence * 100);

  let label = "Low";
  if (percentage >= 80) label = "High";
  else if (percentage >= 60) label = "Medium";

  return (
    <div className="section-block">
      <h3>Confidence</h3>
      <div className={`confidence-badge confidence-${label.toLowerCase()}`}>
        {percentage}% - {label}
      </div>
    </div>
  );
}

export default ConfidenceBadge;