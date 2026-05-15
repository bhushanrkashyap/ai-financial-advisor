import { useState } from 'react';
import '../styles/components.css';

interface LoanFormProps {
  onPredict: (data: Record<string, any>) => void;
  loading: boolean;
}

export function LoanForm({ onPredict, loading }: LoanFormProps) {
  const [formData, setFormData] = useState({
    loan_amnt: 15000,
    term: 60,
    int_rate: 12.5,
    annual_inc: 75000,
    fico_avg: 690,
    dti: 0.25,
    emp_length: 5,
    delinq_2yrs: 1,
    open_acc: 8,
    pub_rec: 0,
    revol_bal: 10000,
    revol_util: 0.5,
    inq_last_6mths: 1,
    installment: 300,
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const numValue = type === 'number' ? parseFloat(value) : value === 'true' ? true : value === 'false' ? false : value;
    setFormData(prev => ({ ...prev, [name]: numValue }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Client-side validation for extremely risky profiles
    const fico = formData.fico_avg;
    const dti = formData.dti;
    const delinq = formData.delinq_2yrs;
    const income = formData.annual_inc;
    const loan = formData.loan_amnt;

    const warnings = [];
    if (fico < 500) warnings.push("⚠️ FICO score < 500 (critical)");
    if (dti > 0.50) warnings.push("⚠️ DTI > 50% (unsustainable)");
    if (delinq > 3) warnings.push("⚠️ Delinquencies > 3");
    if (income < 15000 && loan > 50000) warnings.push("⚠️ Insufficient income for loan");
    if (fico < 600 && dti > 0.40) warnings.push("⚠️ Poor credit + high DTI combo");

    if (warnings.length > 0) {
      const msg = warnings.join("\n");
      console.warn("Risk flags detected:\n" + msg);
      if (!confirm(`Red flags detected:\n${msg}\n\nProceed anyway?`)) {
        return;
      }
    }

    onPredict(formData);
  };

  return (
    <div className="card form-card">
      <h2>📋 Loan Application</h2>
      <form onSubmit={handleSubmit} className="loan-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="loan_amnt">Loan Amount ($)</label>
            <input
              type="number"
              id="loan_amnt"
              name="loan_amnt"
              value={formData.loan_amnt}
              onChange={handleChange}
              min="1000"
              max="100000"
              step="1000"
            />
          </div>
          <div className="form-group">
            <label htmlFor="term">Term (months)</label>
            <input
              type="number"
              id="term"
              name="term"
              value={formData.term}
              onChange={handleChange}
              min="12"
              max="84"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="int_rate">Interest Rate (%)</label>
            <input
              type="number"
              id="int_rate"
              name="int_rate"
              value={formData.int_rate}
              onChange={handleChange}
              step="0.1"
              min="1"
              max="30"
            />
          </div>
          <div className="form-group">
            <label htmlFor="annual_inc">Annual Income ($)</label>
            <input
              type="number"
              id="annual_inc"
              name="annual_inc"
              value={formData.annual_inc}
              onChange={handleChange}
              min="10000"
              max="500000"
              step="5000"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="fico_avg">FICO Score</label>
            <input
              type="number"
              id="fico_avg"
              name="fico_avg"
              value={formData.fico_avg}
              onChange={handleChange}
              min="300"
              max="850"
            />
          </div>
          <div className="form-group">
            <label htmlFor="dti">DTI Ratio (Decimal: 0.0-1.0)</label>
            <input
              type="number"
              id="dti"
              name="dti"
              value={formData.dti}
              onChange={handleChange}
              step="0.01"
              min="0"
              max="1"
              placeholder="e.g., 0.25 for 25%"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="emp_length">Employment Length (years)</label>
            <input
              type="number"
              id="emp_length"
              name="emp_length"
              value={formData.emp_length}
              onChange={handleChange}
              min="0"
              max="50"
            />
          </div>
          <div className="form-group">
            <label htmlFor="delinq_2yrs">Delinquencies (2 years)</label>
            <input
              type="number"
              id="delinq_2yrs"
              name="delinq_2yrs"
              value={formData.delinq_2yrs}
              onChange={handleChange}
              min="0"
              max="10"
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Processing...' : '🚀 Get Prediction'}
        </button>
      </form>
    </div>
  );
}
