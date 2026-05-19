import { useState } from "react";
import "../styles/components.css";

interface LoanFormProps {
  onPredict: (data: Record<string, unknown>) => void;
  loading: boolean;
}

// Loan type configurations with min/max amounts in INR
const LOAN_TYPES = {
  HOME: { label: "Home Loan", minAmount: 500000, maxAmount: 50000000, defaultTerm: 240 },
  VEHICLE: { label: "Vehicle Loan", minAmount: 200000, maxAmount: 5000000, defaultTerm: 60 },
  PERSONAL: { label: "Personal Loan", minAmount: 50000, maxAmount: 1000000, defaultTerm: 36 },
  EDUCATION: { label: "Education Loan", minAmount: 100000, maxAmount: 10000000, defaultTerm: 120 },
};

export function LoanForm({ onPredict, loading }: LoanFormProps) {
  const [loanType, setLoanType] = useState<keyof typeof LOAN_TYPES>("PERSONAL");
  const [formData, setFormData] = useState({
    loan_amnt: 500000, // Changed to INR
    term: 36,
    int_rate: 12.5,
    annual_inc: 750000, // Changed to INR
    fico_avg: 690,
    dti: 0.25,
    emp_length: 5,
    delinq_2yrs: 1,
    open_acc: 8,
    pub_rec: 0,
    revol_bal: 100000,
    revol_util: 0.5,
    inq_last_6mths: 1,
    installment: 15000,
    grade_encoded: 3,
    sub_grade_encoded: 3,
    home_ownership_MORTGAGE: 1,
    home_ownership_OWN: 0,
    home_ownership_RENT: 0,
    verification_status_Verified: 1,
    verification_status_Source_Verified: 0,
    purpose_credit_card: 0,
    purpose_debt_consolidation: 1,
    purpose_car: 0,
    purpose_medical: 0,
    purpose_home_improvement: 0,
    application_type_Individual: 1,
    application_type_Joint_App: 0,
  });

  const currentLoanConfig = LOAN_TYPES[loanType];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const numValue =
      type === "number" ? parseFloat(value) : value === "true" ? true : value === "false" ? false : value;
    setFormData((prev) => ({ ...prev, [name]: numValue }));
  };

  const handleLoanTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newType = e.target.value as keyof typeof LOAN_TYPES;
    setLoanType(newType);
    const config = LOAN_TYPES[newType];
    setFormData((prev) => ({
      ...prev,
      loan_amnt: config.minAmount + (config.maxAmount - config.minAmount) * 0.3,
      term: config.defaultTerm,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const fico = formData.fico_avg;
    const dti = formData.dti;
    const delinq = formData.delinq_2yrs;
    const income = formData.annual_inc;
    const loan = formData.loan_amnt;

      const warnings: string[] = [];
      if (fico < 500) warnings.push("FICO score under 500 (critical risk)");
      if (dti > 0.5) warnings.push("Debt-to-Income above 50%");
      if (delinq > 3) warnings.push("More than 3 late payments in 2 years");
      if (income < 250000 && loan > 2000000) warnings.push("Income may be insufficient for this loan");
      if (fico < 600 && dti > 0.4) warnings.push("Weak credit with high debt ratio");

    if (warnings.length > 0) {
      const msg = warnings.join("\n");
      if (!confirm(`Risk Warnings:\n\n${msg}\n\nContinue?`)) {
        return;
      }
    }

    onPredict(formData);
  };

  return (
    <div className="card form-card">
      <h2>Loan Application</h2>
      <form onSubmit={handleSubmit} className="loan-form">
        {/* Loan Type Selection */}
        <div className="form-row">
          <div className="form-group form-group-full">
            <label htmlFor="loanType">Type of Loan</label>
            <select id="loanType" value={loanType} onChange={handleLoanTypeChange} style={{ fontSize: "1rem", padding: "0.75rem" }}>
              {Object.entries(LOAN_TYPES).map(([key, config]) => (
                <option key={key} value={key}>
                  {config.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Primary Inputs: Salary & FICO */}
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="annual_inc">
              Annual Salary
              <span style={{ fontSize: "0.85rem", color: "#7f8c8d", marginLeft: "0.5rem" }}>
                (₹ {(formData.annual_inc as number).toLocaleString("en-IN")})
              </span>
            </label>
            <input
              type="number"
              id="annual_inc"
              name="annual_inc"
              value={formData.annual_inc}
              onChange={handleChange}
              min={200000}
              max={10000000}
              step={50000}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="fico_avg">
              FICO Score
              <span style={{ fontSize: "0.85rem", color: "#7f8c8d", marginLeft: "0.5rem" }}>
                ({formData.fico_avg})
              </span>
            </label>
            <input
              type="number"
              id="fico_avg"
              name="fico_avg"
              value={formData.fico_avg}
              onChange={handleChange}
              min={300}
              max={850}
              required
            />
          </div>
        </div>

        {/* Loan Amount with Limits */}
        <div className="form-row">
          <div className="form-group form-group-full">
            <label htmlFor="loan_amnt">
              Loan Amount
              <span style={{ fontSize: "0.85rem", color: "#7f8c8d", marginLeft: "0.5rem" }}>
                (₹ {(formData.loan_amnt as number).toLocaleString("en-IN")})
              </span>
              <span style={{ fontSize: "0.8rem", color: "#95a5a6", marginLeft: "1rem" }}>
                Range: ₹{currentLoanConfig.minAmount.toLocaleString("en-IN")} - ₹
                {currentLoanConfig.maxAmount.toLocaleString("en-IN")}
              </span>
            </label>
            <input
              type="number"
              id="loan_amnt"
              name="loan_amnt"
              value={formData.loan_amnt}
              onChange={handleChange}
              min={currentLoanConfig.minAmount}
              max={currentLoanConfig.maxAmount}
              step={10000}
              required
            />
            {/* Loan amount slider */}
            <input
              type="range"
              min={currentLoanConfig.minAmount}
              max={currentLoanConfig.maxAmount}
              step={10000}
              value={formData.loan_amnt}
              name="loan_amnt_slider"
              onChange={(e) => setFormData((prev) => ({ ...prev, loan_amnt: parseInt(e.target.value) }))}
              style={{ marginTop: "0.5rem", width: "100%", cursor: "pointer" }}
            />
          </div>
        </div>

        {/* Term & Interest Rate */}
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="term">Loan Duration</label>
            <input
              type="number"
              id="term"
              name="term"
              value={formData.term}
              onChange={handleChange}
              min={12}
              max={360}
              step={12}
              required
            />
            <small style={{ color: "#7f8c8d" }}>{formData.term} months = {(formData.term / 12).toFixed(1)} years</small>
          </div>
          <div className="form-group">
            <label htmlFor="int_rate">Interest Rate (%)</label>
            <input
              type="number"
              id="int_rate"
              name="int_rate"
              value={formData.int_rate}
              onChange={handleChange}
              step={0.1}
              min={1}
              max={30}
              required
            />
          </div>
        </div>

        {/* Additional Details (Collapsible) */}
        <details style={{ marginTop: "1rem", padding: "1rem", backgroundColor: "var(--surface-elevated)", borderRadius: "8px", cursor: "pointer" }}>
          <summary style={{ fontWeight: 600, color: "var(--text)", marginBottom: "1rem" }}>Additional Details</summary>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="dti">Debt-to-Income Ratio</label>
              <input
                type="number"
                id="dti"
                name="dti"
                value={formData.dti}
                onChange={handleChange}
                step={0.01}
                min={0}
                max={1}
                placeholder="0.25"
              />
              <small style={{ color: "#7f8c8d" }}>{(formData.dti * 100).toFixed(1)}% of income</small>
            </div>
            <div className="form-group">
              <label htmlFor="emp_length">Employment (years)</label>
              <input
                type="number"
                id="emp_length"
                name="emp_length"
                value={formData.emp_length}
                onChange={handleChange}
                min={0}
                max={50}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="delinq_2yrs">Late Payments (2 years)</label>
              <input
                type="number"
                id="delinq_2yrs"
                name="delinq_2yrs"
                value={formData.delinq_2yrs}
                onChange={handleChange}
                min={0}
                max={10}
              />
            </div>
            <div className="form-group">
              <label htmlFor="open_acc">Open Accounts</label>
              <input type="number" id="open_acc" name="open_acc" value={formData.open_acc} onChange={handleChange} min={0} max={50} />
            </div>
          </div>
        </details>

        <button type="submit" disabled={loading} className="submit-btn">
           {loading ? "Checking eligibility..." : "Check Loan Eligibility"}
        </button>
      </form>
    </div>
  );
}
