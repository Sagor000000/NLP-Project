function WarningBox({ warning }) {
  if (!warning) return null;

  return (
    <div className="warning-box">
      <strong>Warning:</strong> {warning}
    </div>
  );
}

export default WarningBox;