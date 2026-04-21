function LoadingCard() {
  return (
    <div className="answer-card">
      <div className="skeleton title-skeleton"></div>

      <div className="section-block">
        <div className="skeleton heading-skeleton"></div>
        <div className="skeleton line-skeleton"></div>
        <div className="skeleton line-skeleton"></div>
        <div className="skeleton short-line-skeleton"></div>
      </div>

      <div className="section-block">
        <div className="skeleton heading-skeleton"></div>
        <div className="skeleton line-skeleton"></div>
        <div className="skeleton short-line-skeleton"></div>
      </div>

      <div className="section-block">
        <div className="skeleton heading-skeleton"></div>
        <div className="skeleton line-skeleton"></div>
        <div className="skeleton line-skeleton"></div>
      </div>
    </div>
  );
}

export default LoadingCard;