function QueryForm({ question, setQuestion, onSubmit, loading }) {
  return (
    <form className="query-box" onSubmit={onSubmit}>
      <label htmlFor="question">Ask your legal question</label>

      <textarea
        id="question"
        rows="5"
        placeholder="আপনার আইনি প্রশ্ন লিখুন..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button type="submit" disabled={loading}>
        {loading ? "Loading..." : "Ask"}
      </button>
    </form>
  );
}

export default QueryForm;