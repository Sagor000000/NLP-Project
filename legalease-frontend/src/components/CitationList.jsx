function CitationList({ sources }) {
  if (!sources || sources.length === 0) {
    return <p>No sources available.</p>;
  }

  return (
    <div className="section-block">
      <h3>Sources</h3>
      <ul className="citation-list">
        {sources.map((item, index) => (
          <li key={index} className="citation-item">
            <span className="citation-source">{item.source}</span>
            <span className="citation-section">{item.section}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CitationList;